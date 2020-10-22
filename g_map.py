import requests

from configparser import ConfigParser

parser = ConfigParser()
parser.read(".env")

google_key = parser.get('strava_dev_credentials', 'google_maps_api_key')

class GMap:   
      
    def __init__(self, polyline, start_latlng, end_latlng):   
        self.polyline = polyline
        self.start_latlng = start_latlng
        self.end_latlng = end_latlng


    def get_image_url(self):
        return ( "https://maps.googleapis.com/maps/api/staticmap?maptype=terrain&path=color:0xF57900FF|weight:3|enc:" 
            + self.polyline 
            + "&size=1080x1080&key=" 
            + google_key )


    def fetch_image(self):
        url = self.get_image_url()
        with open("pictmp/map.jpeg", 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
