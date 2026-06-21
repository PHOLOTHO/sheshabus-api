from geopy.distance import geodesic


class LocationService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates in kilometers
        """
        coord1 = (lat1, lon1)
        coord2 = (lat2, lon2)
        return geodesic(coord1, coord2).kilometers

    @staticmethod
    def calculate_eta(distance_km, average_speed_kmh=30):
        """
        Calculate estimated time of arrival in minutes
        """
        if average_speed_kmh <= 0:
            return 0
        time_hours = distance_km / average_speed_kmh
        return round(time_hours * 60)  # Convert to minutes

    @staticmethod
    def is_location_near_stop(user_lat, user_lon, stop_lat, stop_lon, radius_km=0.5):
        """
        Check if user location is near a bus stop
        """
        distance = LocationService.calculate_distance(user_lat, user_lon, stop_lat, stop_lon)
        return distance <= radius_km