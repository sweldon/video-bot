"""
Given a search query, call the GIPHY API and return
a random choice from results
"""

import json
from urllib import parse, request
import requests
import os
import random
import time


class GiphyClient:
    
    def __init__(
        self,
        endpoint = "http://api.giphy.com/v1/gifs/search",
        search_limit = 100,
        download_format = "mp4",
        download_type = "original",
        query = "space",
        rating = "g"
    ):
        self.endpoint = endpoint
        self.api_key = os.environ["GIPHY_API_KEY"]
        self.search_limit = search_limit
        self.download_format = download_format
        # To get a GIF instead of an mp4, use 'url' for download_type
        self.download_type = download_type
        self.query = query
        self.rating = rating
        self.max_attempts = 20

        self.params = parse.urlencode({
            "q": query,
            "api_key": self.api_key,
            "limit": str(self.search_limit),
            "rating": rating
        })

    def get_background(self, title_dir, title):

        attempts = 1
        while True:
            random_index = random.randint(0, self.search_limit - 1)

            with request.urlopen("".join((self.endpoint, "?", self.params))) as response:
                results = json.loads(response.read())

            try:
                image_url = results["data"][random_index]["images"][self.download_type][self.download_format]
                print("using GIF/MP4:", image_url)
                break
            except IndexError:
                print(
                    f"[GIPHY ERROR] Could not find any {self.download_format} results for query: '{self.query}'... "
                    f"Trying again! ({attempts}/{self.max_attempts} attempts)"
                )
                if attempts > self.max_attempts:
                    print("Max attempts reached, exiting. Please try again later.")
                    exit(1)
                attempts += 1
                time.sleep(1)
        img_data = requests.get(image_url).content
        gif_path = "%s.%s" % (os.path.join(title_dir, title+"_bg"), self.download_format)
        with open(gif_path, 'wb') as handler:
            handler.write(img_data)
        return gif_path
