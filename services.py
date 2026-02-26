from haversine import haversine


def calculate_metrics(locations):
    first_location = locations[0]
    latest_location = locations[-1]
    print("first_location:", first_location)
    print("latest_location:", latest_location)
    distance = haversine(
        (first_location["latitude"], first_location["longitude"]),
        (latest_location["latitude"], latest_location["longitude"]),
    )
    time = latest_location["time"] - first_location["time"]
    return {"distance": distance, "time": str(time)}
