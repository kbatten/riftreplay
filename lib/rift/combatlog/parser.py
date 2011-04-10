# todo, have some concept of timestamp_last

import re
import json


def pretty_print(var):
    print json.dumps(var, sort_keys = False, indent = 4)

def parse_line(line):
    expr = "^([0-9]{2}:[0-9]{2}:[0-9]{2}): \( ([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , (.*) , (.*) , (.*) , ([0-9]+) , (.*) \) (.*)[.!](?: \(([0-9a-zA-Z ]+)\))?$"
    results = re.match(expr, line.strip())
    if not results:
        try:
            if line.split()[1] == "(":
                raise ErrorParse(line)
        except IndexError:
            pass
        return None

    timestamp = int(results.group(1).split(":")[0])*3600 + int(results.group(1).split(":")[1])*60 + int(results.group(1).split(":")[2])

    event = {}
    event["type"] = "event"
    event["timestamp"] = int(timestamp)
    event["action_type"] = int(results.group(2))
    event["actor1_type"] = results.group(3)
    event["actor1_group"] = results.group(4)
    event["actor1_id"] = results.group(5)
    event["actor2_type"] = results.group(6)
    event["actor2_group"] = results.group(7)
    event["actor2_id"] = results.group(8)
    event["owner1_type"] = results.group(9)
    event["owner1_group"] = results.group(10)
    event["owner1_id"] = results.group(11)
    event["owner2_type"] = results.group(12)
    event["owner2_group"] = results.group(13)
    event["owner2_id"] = results.group(14)
    event["actor1_name"] = results.group(15)
    event["actor2_name"] = results.group(16)
    event["action_value"] = int(results.group(17))
    event["action_id"] = results.group(18)
    event["action_name"] = results.group(19)

    # parse out absorbed, blocked, etc
    try:
        for extra in re.findall("[0-9]+ [a-zA-Z]+", results.group(21)):
            event["action_" + extra.split()[1]] = int(extra.split()[0])
    except TypeError:
        pass

    return event
    

def parse_log(filename, db, batch_size=10000):
    timestamp_last = 0
    event_count = 0
    event_batch = []
    expr = "^([0-9]{2}:[0-9]{2}:[0-9]{2}): \( ([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , T=([PNX])#R=([COGRX])#([0-9]+) , (.*) , (.*) , (.*) , ([0-9]+) , (.*) \) (.*)[.!](?: \(([0-9a-zA-Z ]+)\))?$"

    cexpr = re.compile(expr)

    for line in file(filename):
        results = cexpr.match(line.strip())
        if not results:
            if line.split()[1] == "(":
                print line
            continue

        timestamp = int(results.group(1).split(":")[0])*3600 + int(results.group(1).split(":")[1])*60 + int(results.group(1).split(":")[2])
        if timestamp < timestamp_last:
            timestamp = timestamp + 86400
            timestamp_last = timestamp

        event = {}
        event["type"] = "event"
        event["timestamp"] = timestamp
        event["action_type"] = int(results.group(2))
        event["actor1_type"] = results.group(3)
        event["actor1_group"] = results.group(4)
        event["actor1_id"] = results.group(5)
        event["actor2_type"] = results.group(6)
        event["actor2_group"] = results.group(7)
        event["actor2_id"] = results.group(8)
        event["owner1_type"] = results.group(9)
        event["owner1_group"] = results.group(10)
        event["owner1_id"] = results.group(11)
        event["owner2_type"] = results.group(12)
        event["owner2_group"] = results.group(13)
        event["owner2_id"] = results.group(14)
        event["actor1_name"] = results.group(15)
        event["actor2_name"] = results.group(16)
        event["action_value"] = int(results.group(17))
        event["action_id"] = results.group(18)
        event["action_name"] = results.group(19)

        # if in the log, parse out absorbed, blocked, etc
        try:
            for extra in re.findall("[0-9]+ [a-zA-Z]+", results.group(21)):
                event["action_" + extra.split()[1]] = int(extra.split()[0])
        except:
            pass

        event_batch.append(event)
        db.save(event)
        event_count += 1
        if (event_count % batch_size) == 0:
            db.update(event_batch,batch="ok")
            event_batch = []

    db.update(event_batch,batch="ok")


class Error(Exception):
    pass

class ErrorParse(Error):
    pass
