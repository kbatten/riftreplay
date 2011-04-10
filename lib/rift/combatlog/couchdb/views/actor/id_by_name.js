function map(doc) {
    if (doc["type"] == "event") {
        emit(doc["actor1_name"], doc["actor1_id"]);
        emit(doc["actor2_name"], doc["actor2_id"]);
    }
}

// this reduce will squash NPCs and pet ids
function reduce(keys, values) {
    return values[0];
}
