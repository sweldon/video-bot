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
from clients.pexels import PexelsClient
from clients.giphy import GiphyClient
from utils.helpers import cleanup_video_directory


class Poster:

    def generate_post(
            self,
            sqllite_path,
            output_dir,
            reuse_prompts,
            title,
            bg_source
        ):

        # Get a random prompt
        prompt_selector = PromptSelector(sqllite_path, title)
        title, prompt = prompt_selector.select_prompt()

        # If the directory already exists, blow it away and start over
        title_dir = f"{output_dir}{title}"
        final_file_path = f"{title_dir}/{title}.mp4"

        if os.path.isdir(title_dir):
            print("Video dir already exists, deleting")
            shutil.rmtree(title_dir)
        os.mkdir(title_dir)

        # Generate voiceover
        speaker = Speaker()
        audio_file_path = speaker.generate_audio(prompt, title_dir)
        # Voiceover duration dictates length of the video (background is looped if it's an image)
        audio_duration = speaker.get_duration(audio_file_path)

        # Get a background video/GIF to be looped while voiceover runs
        if bg_source == "giphy":
            giphy_client = GiphyClient()
            bg_path = giphy_client.get_background(title_dir, title)
        else:
            pexels_client = PexelsClient(query=title)
            bg_path = pexels_client.get_background_video(title_dir, title)

        # Join image and audio into a video
        # TODO: add search terms col to database to pick more relevant background videos
        video_maker = VideoMaker()
        dubbed_video = video_maker.generate_video(
            audio_file_path,
            bg_path,
            title_dir,
            audio_duration
        )

        # Add captions
        video_manager = DubbedVideoManager(dubbed_video, title_dir)
        subtitle_generator = SubtitleGenerator(video_manager, title_dir)
        subtitle_generator.attach()

        # Cleanup video directory, leaving only the final video
        cleanup_video_directory(final_file_path, title_dir)

        # Mark this video as used, completed successfully, if applicable
        if reuse_prompts is False:
            print("Video successfully generated, flagging as used...")
            prompt_selector.mark_as_used(title)


parser = argparse.ArgumentParser()
parser.add_argument('--sqllite_path', type=str, required=True)
parser.add_argument('--output_dir', type=str, required=True)
parser.add_argument('--reuse_prompts', action='store_true')
parser.add_argument('--title', type=str)
parser.add_argument('--bg_source', type=str, default="pexels")
args = parser.parse_args()

poster = Poster()
post = poster.generate_post(
    sqllite_path=args.sqllite_path,
    output_dir=args.output_dir,
    reuse_prompts=args.reuse_prompts,
    title=args.title,
    bg_source=args.bg_source
)
