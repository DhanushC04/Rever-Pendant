import requests

class LocationService:
    def get_location_from_ip(self):
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
            }
        except:
            return {
                'city': 'Bengaluru',
                'region': 'Karnataka',
                'country': 'India'
            }
    
    def format_location(self, location_data):
        return f"{location_data['city']}, {location_data['region']}, {location_data['country']}"