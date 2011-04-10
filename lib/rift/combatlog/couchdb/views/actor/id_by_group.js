function map(doc) {
    if (doc["type"] == "event") {
        if (doc["actor1_group"] != "X") {
            emit(doc["actor1_group"], doc["actor1_id"]);
        }
        if (doc["actor1_group"] != "X") {
            emit(doc["actor2_group"], doc["actor2_id"]);
        }
    }
}

// this reduce will squash NPCs and pet ids
function reduce(keys, values) {
    return values[0];
}

