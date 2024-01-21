"""
Given a search query, call the Pexels API and return
a random video that is appropriately sized
"""
from urllib import parse, request
import requests
import os
import random
import time
from typing import List

class PexelsClient:
    
    def __init__(
        self,
        endpoint = "https://api.pexels.com/videos/search",
        search_limit = 3,
        query = "space",
        min_width = 1280,
        min_height = 720
    ):
        self.endpoint = endpoint
        self.api_key = os.environ["PEXELS_API_KEY"]
        self.search_limit = search_limit
        self.query = query
        self.min_width = min_width
        self.min_height = min_height
        self.max_attempts = 20
        self.params = parse.urlencode({
            "query": query,
            "per_page": self.search_limit,
        })

    def download_video(self, video_id, output_dir, title, height, width):
        opener =request.build_opener()
        opener.addheaders = [('Authorization', self.api_key)]
        request.install_opener(opener)
        download_link = f"https://www.pexels.com/download/video/{video_id}/?h={height}&w={width}"
        download_path = "%s.mp4" % (os.path.join(output_dir, title+"_bg"))
        request.urlretrieve(download_link, download_path) 
        return download_path

    def filter_video_list(self, video_list: List[dict], filter_conditions: dict):

        filtered_vids = list(filter(
            lambda record: all((
                # If the value is a list, filter for any values in that list (i.e. OR condition)
                record[filter_key] in filter_value
                if isinstance(filter_value, list)
                # Otherwise, filter by the exact value
                else record[filter_key] == filter_value
                for (filter_key, filter_value)
                in filter_conditions.items()
            )),
            video_list
        ))
        return filtered_vids

    def download_first_available_hd_video(self, parent_video_id, video_file_list, output_dir, title):

        for v in video_file_list:
            if v["height"] >= self.min_height:
                # Some video sizes are not available for download, so try again with the next size if necessary
                video_id = v["id"]
                height = v["height"]
                width = v["width"]
                try:
                    # See if video is available
                    video_path = self.download_video(parent_video_id, output_dir, title, height, width)
                    return video_path
                except Exception:
                    print(
                        f"Video file {video_id} (parent {parent_video_id}) "
                        "unavailable for download, checking for other options..."
                    )

    def get_background_video(self, output_dir, title):
        attempts = 1
        while True:   
            try:
                endpoint = "".join((self.endpoint, "?", self.params))
                results = requests.get(endpoint, headers={'Authorization': self.api_key})
                video_list = results.json()["videos"]

                # First get all HD videos
                hd_videos = [
                    v for v in video_list
                    if v["width"] >= self.min_width
                    and v["height"] >= self.min_height
                ]
                # Get a random video
                random_index = random.randint(0, len(hd_videos) - 1)
                random_video = hd_videos[random_index]
                # TODO don't reuse background vids, probably just use memcached. If all available vids
                # are used on first page (80 by default), increment page on pexels and go to next page
                parent_video_id = random_video['id']
                
                # Get the first, smallest HD video file of an acceptable size (an HD height which can be cropped)
                video_files_by_size = sorted(random_video["video_files"], key= lambda x: x["height"])
                background_video_path = self.download_first_available_hd_video(
                    parent_video_id,
                    video_files_by_size,
                    output_dir,
                    title
                )
                if background_video_path is None:
                    raise(f"Could not find any usable video sizes in video list {video_files_by_size}")
                break

            except Exception as e:
                print(
                    f"[PEXELS ERROR] There was a problem getting a video for query: '{self.query}'... "
                    f"Trying again! ({attempts}/{self.max_attempts} attempts)"
                )

                if e.__class__.__name__ == 'ValueError' and self.query != 'space':
                    # If there were no results for a custom query, fall back to 'space' and expand the search
                    print(
                        f"No results found for {self.query}, falling back to default query "
                        "and expanding the search..."
                    )
                    self.params = parse.urlencode({
                        "query": "space",
                        "per_page": 20,
                    })

                if attempts > self.max_attempts:
                    print("Max attempts reached, exiting. Please try again later.")
                    exit(1)
                attempts += 1
                time.sleep(5)

        return background_video_path
