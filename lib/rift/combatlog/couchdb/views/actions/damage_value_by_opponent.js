// - returns [<friend_id>, <enemy_id>], [<timestamp>, <damage value>]
// ? is there a way to sum values with the same timestamp?
//   - if not, then it will need to be done before resampling

function map(doc) {
    if (doc["type"] == "event") {
        if (doc["action_value"] > 0) {
            emit({"friend_id" : doc["actor1_id"], "enemy_id" : doc["actor2_id"]}, [doc["timestamp"], doc["action_value"]]);
        }
    }
}

//# doesn't seem to be merging timestamps :/
function reduce(keys, values, rereduce) {
    var lvalues = [];
    if (!rereduce) {
        lvalues = values;
    } else {
        // first flatten
        for (list_index in values) {
            for (var value_index in values[list_index]) {
                lvalues.push(values[list_index][value_index]);
            }
        }
    }

    // merge timestamps
    var value;
    var timestamp;
    dvalues =[];
    for (var value_index in lvalues) {
        timestamp = lvalues[value_index][0];
        value = lvalues[value_index][1];
        if (dvalues[timestamp]) {
            dvalues[timestamp] = dvalues[timestamp] + value;
        } else {
            dvalues[timestamp] = value;
        }
    }

    // convert back to array
    lvalues = [];
    for (var timestamp in dvalues) {
        value = dvalues[timestamp];
        lvalues.push([parseInt(timestamp), value]);
    }

    return lvalues;

    /*
    lvalues = []
    if rereduce:
        for value_list in values:
            for value in value_list:
                lvalues.append(value)
    else:
        lvalues = values
    
    dvalues = {}
    for value in lvalues:
        if value["timestamp"] in dvalues:
            dvalues[value["timestamp"]] += value["value"]
        else:
            dvalues[value["timestamp"]] = value["value"]

    advalues = []
    for kv in dvalues.iteritems():
        advalues.append({"timestamp" : kv[0], "value" : kv[1]})

    return advalues
*/
    return values[0];
}