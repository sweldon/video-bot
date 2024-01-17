"""
Chooses a prompt from a database, generates a voiceover, chooses
a background image, generates captions, and then combines them into
a video
"""

import sys
sys.path.insert(0, '../post_bot/')
import argparse
from prompts.prompt_selector import PromptSelector
from speech.speaker import Speaker
from video.video_maker import VideoMaker
from video.captioner import DubbedVideoManager, SubtitleGenerator
import os
import shutil
from clients.giphy import GiphyClient

class Poster:

    def generate_post(
            self,
            sqllite_path,
            output_dir
        ):

        # Get a random prompt
        prompt_selector = PromptSelector(sqllite_path)
        title, prompt = prompt_selector.select_prompt()

        # If the directory already exists, blow it away and start over
        title_dir = f"{output_dir}{title}"
        if os.path.isdir(title_dir):
            print("Video dir already exists, deleting")
            shutil.rmtree(title_dir)
        os.mkdir(title_dir)

        # Generate voiceover
        speaker = Speaker()
        audio_file_path = speaker.generate_audio(prompt, title_dir)
        # Voiceover duration dictates length of the video (background is looped if it's an image)
        audio_duration = speaker.get_duration(audio_file_path)

        # Get a background image to be looped while voiceover runs
        giphy_client = GiphyClient()
        bg_path = giphy_client.get_background(title_dir, title)

        # Join image and audio into a video
        video_maker = VideoMaker()
        dubbed_video = video_maker.generate_video(
            audio_file_path,
            bg_path,
            title_dir,
            audio_duration
        )

        # Add captions
        videomanager = DubbedVideoManager(dubbed_video, title_dir)
        subtitle_generator = SubtitleGenerator(videomanager, title_dir)
        subtitle_generator.attach()

        # Mark this video as used, completed successfully
        prompt_selector.mark_as_used(title)


parser = argparse.ArgumentParser()
parser.add_argument('--sqllite_path', type=str, required=True)
parser.add_argument('--output_dir', type=str, required=True)
args = parser.parse_args()

poster = Poster()
post = poster.generate_post(
    sqllite_path=args.sqllite_path,
    output_dir=args.output_dir
)
