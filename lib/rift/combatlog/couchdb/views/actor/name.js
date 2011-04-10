function map(doc) {
    if (doc["type"] == "event") {
        emit(doc["actor1_id"], doc["actor1_name"]);
        emit(doc["actor2_id"], doc["actor2_name"]);
    }
}

function reduce(keys, values) {
    return values[0];
}
