import requests
import os
import glob
from instabot import Bot
from PIL import Image
from configparser import ConfigParser

parser = ConfigParser()
parser.read(".env")

r_code = parser.get('strava_dev_credentials', 'r_code')
ig_username = parser.get('strava_dev_credentials', 'ig_username')
ig_password = parser.get('strava_dev_credentials', 'ig_password')


headers = {
    "Authorization": "Bearer {}".format(r_code) 
}

class Activity:   
      
    def __init__(self, id):   
        self.id = id
        self.photo_count = 0
        self.bot = Bot() 
        self.title = ""
        self.description = ""
        self.bot_msg = "🤖 Post created by PostMyRide, more info: https://github.com/davidlrnt/postmyride-strava-to-ig"
        self.activity_url = "https://www.strava.com/activities/" + str(id);

    def fetch_data(self):   
        r = requests.get("https://www.strava.com/api/v3/activities/{}?include_all_efforts=false".format(self.id), headers=headers)
        activity = r.json()

        self.title = activity["name"]
        self.description = activity["description"] if "description" in activity else ""

        if activity["total_photo_count"] > 0 and "Virtual" not in activity["type"]:
            rp = requests.get("https://www.strava.com/api/v3/activities/{}/photos?photo_sources=true&size=1080".format(self.id), headers=headers)
            photos = rp.json()
            self.photo_count = len(photos)
            pic_id = 1
            
            for i,photo in enumerate(photos):
                title = ""
                if photo["default_photo"]:
                    title = "pic0.jpg".format(pic_id)
                else:
                    title = "pic{}.jpg".format(pic_id)
                    pic_id += 1

                with open("pictmp/" + title, 'wb') as handle:
                    response = requests.get(photo["urls"]["1080"], stream=True)

                    if not response.ok:
                        print(response)

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

                self.resize("pictmp/" + title)

            self.create_ig_post()

    def resize(self, image_pil):
        im = Image.open(image_pil)

        width  = im.size[0]
        height = im.size[1]
        aspect = width / float(height)

        if width < height:
            #Portrait 4:5 1080 x 1350px

            ideal_width = 1080
            ideal_height = 1350


        elif width > height:
            #Landscape 1.91:1 1080 x 608px
            ideal_width = 1080
            ideal_height = 608
        else:
            #1:1 1080 x 1080:
            ideal_width = 1080
            ideal_height = 1080
        
        ideal_aspect = ideal_width / float(ideal_height)


        if aspect > ideal_aspect:
            # Then crop the left and right edges:
            new_width = int(ideal_aspect * height)
            offset = (width - new_width) / 2
            resize = (offset, 0, width - offset, height)
        else:
            # ... crop the top and bottom:
            new_height = int(width / ideal_aspect)
            offset = (height - new_height) / 2
            resize = (0, offset, width, height - offset)

        thumb = im.crop(resize).resize((ideal_width, ideal_height), Image.ANTIALIAS)
        thumb.save(image_pil)


    def create_ig_post(self):
        self.bot.login(username = ig_username,  
          password = ig_password)

        full_title = ( self.title
            + "\n" + self.activity_url
            + "\n" + self.bot_msg )

        if self.description:
            full_title += "\n"
            full_title += self.description

        if self.photo_count == 1:
            self.bot.upload_photo("./pictmp/pic0.jpg",  
                caption = full_title) 
        else:
            album = []

            for i in range(self.photo_count):
                album.append("./pictmp/pic{}.jpg".format(i))

            self.bot.upload_album(album,  
                       caption = full_title) 


        files = glob.glob('/pictmp/*')
        for f in files:
            os.remove(f)