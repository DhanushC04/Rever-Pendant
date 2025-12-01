import requests
import logging

class LocationService:
    def __init__(self):
        # Try multiple providers for better reliability
        self.providers = [
            ('https://ipapi.co/json/', lambda d: (d.get('city'), d.get('region'), d.get('country_name'))),
            ('https://ipinfo.io/json', lambda d: (d.get('city'), d.get('region'), d.get('country'))),
            ('http://ip-api.com/json/', lambda d: (d.get('city'), d.get('regionName'), d.get('country'))),
        ]
        self.default = {'city': 'Bengaluru', 'region': 'Karnataka', 'country': 'India'}

    def get_location_from_ip(self):
        for url, parser in self.providers:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    logging.debug(f"Location provider {url} returned {resp.status_code}")
                    continue
                data = resp.json()
                city, region, country = parser(data)
                # Accept partial results but prefer populated values
                if city or region or country:
                    return {
                        'city': city or 'Unknown',
                        'region': region or 'Unknown',
                        'country': country or 'Unknown'
                    }
            except Exception as e:
                logging.debug(f"Location provider {url} failed: {e}")
                continue
        # final fallback (stable default)
        return self.default.copy()

    def format_location(self, location_data):
        return f"{location_data['city']}, {location_data['region']}, {location_data['country']}"