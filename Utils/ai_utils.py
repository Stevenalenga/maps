from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth specified in decimal degrees
    using the Haversine formula.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius of Earth in kilometers
    return r * c  # Distance in kilometers

def get_nearby_locations(user_location, radius):
    """
    Fetch nearby locations based on user's latitude and longitude.
    
    :param user_location: A dictionary with 'latitude' and 'longitude' keys.
    :param radius: The radius within which to search for nearby locations.
    :return: A list of nearby locations within the specified radius.
    """
    user_latitude = user_location['latitude']
    user_longitude = user_location['longitude']

    # Sample data with latitude and longitude
    nearby_locations = [
        {"name": "Hospital A", "latitude": -1.2921, "longitude": 36.8219, "distance": 0.5},
        {"name": "Airbnb B", "latitude": -1.2950, "longitude": 36.8210, "distance": 1.0},
        {"name": "School C", "latitude": -1.2900, "longitude": 36.8100, "distance": 1.5},
    ]

    # Calculate actual distance and filter locations based on the radius
    results = []
    for location in nearby_locations:
        location_latitude = location["latitude"]
        location_longitude = location["longitude"]

        # Calculate distance from user to the location
        distance = calculate_distance(user_latitude, user_longitude, location_latitude, location_longitude)
        if distance <= radius:
            results.append({**location, "distance": distance})  # Include calculated distance

    return results
