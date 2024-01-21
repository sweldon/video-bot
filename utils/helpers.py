

"""
Cleans up temp files from the video directory
"""
import os
import glob
import time


def cleanup_video_directory(video_file: str, output_dir: str):
    print("Cleaning up video directory...")
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
