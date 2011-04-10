// returns:
//   {
//     [actorX_id, actorY_id], actorY_id,
//     [actorX_id, actorY_id], actorY_id,
//     [actorX_id, actorY_id], actorY_id,
//   }
// for now remove actor1_id == actor2_id
function map(doc) {
    if (doc["type"] == "event") {
        if ([5,6,7,27,28].indexOf(doc["action_type"]) != -1) {
            if (doc["actor1_id"] != doc["actor2_id"]) {
                emit([doc["actor1_id"], doc["actor2_id"]], doc["actor2_id"]);
                emit([doc["actor2_id"], doc["actor1_id"]], doc["actor1_id"]);
            }
        }
    }
}

// returns a list of unique actorY_id
// doesn't play well with reduce limit apparently
function reduce(keys, values, rereduce) {
    var duplicates = [];
    if (!rereduce) {
        duplicates = values;
    } else {
        // first flatten
        for (list_index in values) {
            for (var value_index in values[list_index]) {
                duplicates.push(values[list_index][value_index]);
            }
        }
    }

    // dedup
    var uniques = [];
    var curr_value = "X";
    for (value_index in duplicates.sort()) {
        if (duplicates[value_index] != curr_value) {
            uniques.push(duplicates[value_index]);
            curr_value = duplicates[value_index];
        }
    }

    return uniques;
}
