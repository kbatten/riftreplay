import StringIO
import uuid
import socket
import time
import sys

import couchdb

import rift.combatlog.couchdb.indexer as indexer
import rift.combatlog.parser as parser

class Combatlog(object):
    def __init__(self, name, create, overwrite, loc):
        self.url = loc
        self.name = name
        # if name is '' then we will automatically generate one
        # db      | create | overwrite
        # noexist | false  | false     - Error
        # exist   | false  | false     - saved DB
        # noexist | true   | false     - new DB
        # exist   | true   | false     - Error
        # noexist | false  | true      - Error
        # exist   | false  | true      - saved DB (overwrite has no effect)
        # noexist | true   | true      - new DB (overwrite has no effect)
        # exist   | true   | true      - new DB (old db deleted)

        self.server = couchdb.Server(self.url)
        if not self.name:
            self.name = 'log-' + str(uuid.uuid4())
        if create:
            if overwrite:
                try:
                    self.server.delete(self.name)
                except couchdb.http.ResourceNotFound:
                    pass
            self.db = self.server.create(self.name)
            self.create_views()
        else:
            self.db = self.server[self.name]

    def create_views(self):
        indexer.create(self.db)

    def update_index(self):
        indexer.update(self.db)

    def store(self, data, batch_size=10000):
        if isinstance(data, str):
            self._store_string(data, batch_size)
        elif isinstance(data, file):
            data_str = ""
            line_count = 0
            for line in data:
                line_count += 1
                data_str += line
                if (line_count % batch_size) == 0:
                    self._store_string(data_str, batch_size)
                    data_str = ""
            self._store_string(data_str, batch_size)
        else:
            raise TypeError

    def _store_string(self, lines, batch_size):
        event_batch = []
        event_count = 0
        for line in StringIO.StringIO(lines):
            event = parser.parse_line(line)
            if event:
                event_batch.append(event)
                event_count += 1
                if (event_count % batch_size) == 0:
                    self.db.update(event_batch,batch="ok")
                    event_batch = []

        self.db.update(event_batch,batch="ok")

    def get_name(self, actor_id):
        results = self.db.view("actor/name", key=actor_id, group=True)
        return list(results)[0]["value"]

    def get_player_id(self):
        results = self.db.view("actor/id_by_group", key="C", group=True)
        return list(results)[0]["value"]

    def get_player_id_by_name(self, name):
        results = self.db.view("actor/id_by_name", key=name, group=True)
        return list(results)[0]["value"]

    def get_friend_ids(self, actor_id):
        results = self.db.view("actor/friend", group_level=1)
        ids = []
        for row in results:
            if row["key"] == [actor_id]:
                ids = row["value"]
                break
        # the actor is always his own friend
        ids.insert(0, actor_id)
        return ids

    def get_enemy_ids(self, actor_id):
        results = self.db.view("actor/enemy", group_level=1)
        for row in results:
            if row["key"] == [actor_id]:
                return row["value"]


    def _resample(self, data, step_size):
        resampled = [data[0]]
        next_step = data[0][0]

        for index in range(len(data)-1):
            kv0 = data[index]
            try:
                kvn = data[index+1]
            except IndexError:
                kvn = kv0

            # resample
            while next_step <= kvn[0]:
                if kv0[0] != (next_step):
                    v = kv0[1] + ((kvn[1]-kv0[1])/(kvn[0]-kv0[0]-0.0)) * (next_step-kv0[0])
                    resampled.append([next_step, v])
                next_step += step_size

        return resampled

    # get a moving averate from Tn-(window/2) to Tn+(window/2)
    # window size is based off of num_samples
    # xxx: this may still be wrong. need to caluculate end DPS of this data vs end DPS of original
    def _smooth(self, data, num_samples, window_size_resampled):
        step_size = (data[-1][0]-data[0][0])/num_samples
        if step_size < 1:
            step_size = 1

        window_size = (step_size * window_size_resampled)

        if window_size < 2:
            window_size = 2

        resampled = self._resample(data, 1)
        recalculated = []

        for index in range(len(resampled)):
            w_tot = 0
            w_start = -1
            w_end = -1
            for window_index in range(index-(window_size/2), 1+index+(window_size/2)):
                if window_index >= 0 and window_index < len(resampled):
                    w_tot += resampled[window_index][1]
                    if w_start == -1:
                        w_start = resampled[window_index][0]
                    w_end = resampled[window_index][0]

            recalculated.append([resampled[index][0], w_tot / (w_end-w_start)])

        return self._resample(recalculated, step_size)


    def get_dps_by_enemy_id(self, actor_id, enemy_id, num_samples, window_size=3):
        results = self.db.view("actions/damage_value_by_opponent", key={"friend_id":actor_id,"enemy_id":enemy_id})
        if not list(results):
            return []

        damage_values = sorted(list(results)[0]["value"])

        return self._smooth(damage_values, num_samples, window_size)

    def get_dps_by_time(self, actor_id, start_time, end_time, num_samples, window_size=3):
        results = self.db.view("actions/damage_value", key=actor_id)
        if not list(results):
            return []

        damage_values = sorted(list(results)[0]["value"])

        if not start_time:
            start_time = 0
        if not end_time:
            end_time = damage_values[-1][0] + 1

        return self._smooth([damage for damage in damage_values if damage[0] >= start_time and damage[0] <= end_time], num_samples, window_size)
