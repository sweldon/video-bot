

"""
Useful helper functions that don't belong anywhere specific
"""
import os
import glob
import time
from urllib import request
from typing import List, Tuple, Optional


def cleanup_video_directory(video_file: str, output_dir: str) -> None:
    print(f"Cleaning up video directory {output_dir}...")
    max = 5
    attempts = 1
    while not os.path.exists(video_file):
        time.sleep(1)
        attempts += 1
        if attempts > max:
            print(
                f"Unable to cleanup video directory at {output_dir}, "
                "please make sure you provided an absolute path for the "
                "--output parameter"
            )
            return

    if os.path.isfile(video_file):
        for f in glob.glob(output_dir+"/*"):
            if f != video_file:
                os.remove(f)


def download_file(
    link: str,
    output_dir: str,
    title: str,
    file_type: str,
    headers: Optional[List[Tuple]] = None
) -> str:
    opener = request.build_opener()
    if headers:
        opener.addheaders = headers
    request.install_opener(opener)
    download_path = "%s.%s" % (os.path.join(output_dir, title), file_type)
    request.urlretrieve(link, download_path)

    return download_path
