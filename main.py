"""
Chooses a prompt from a database, generates a voiceover, chooses
a background video, generates captions, and then combines it all into
a video
"""

from prompts.prompt_selector import PromptSelector
from speech.speaker import Speaker
from video.video_maker import VideoMaker
from video.captioner import DubbedVideoManager, SubtitleGenerator
import os
import shutil
from clients.pexels import PexelsClient
from clients.giphy import GiphyClient
from clients.tiktok import TikTokUploader
from utils.helpers import cleanup_video_directory
from typing import Tuple
from utils.arg_processor import process_args
import datetime


class VideoBot:

    def generate_post(
            self,
            sqlite_path: str,
            output_dir: str,
            reuse_prompts: bool,
            title: str,
            bg_source: str,
            pexels_download_link: str,
            post_date_time: datetime,
            tiktok_cookie_path: str
        ) -> Tuple[str, str]:

        # Get a random prompt
        prompt_selector = PromptSelector(sqlite_path, title)
        title, prompt, post_description = prompt_selector.select_prompt()

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
            pexels_client = PexelsClient(query=title, download_link=pexels_download_link)
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

        # Upload to TikTok
        tiktok_uploader = TikTokUploader()
        tiktok_uploader.post_video(
            final_file_path,
            post_description,
            tiktok_cookie_path,
            post_date_time
        )

        # Cleanup video directory, leaving only the final video
        cleanup_video_directory(final_file_path, title_dir)

        # Mark this video as used, completed successfully, if applicable
        if reuse_prompts is False:
            print("Video successfully generated, flagging as used...")
            prompt_selector.mark_as_used(title)

        return title, final_file_path


if __name__ == "__main__":
    args = process_args()
    poster = VideoBot()
    num_videos = args.num_videos
    scheduled_times = args.post_date_times
    num_generated = 0
    print(f"Generating {num_videos} videos...")
    for video_number in range(num_videos):
        post_time = scheduled_times[video_number]
        try:
            video_name, video_path = poster.generate_post(
                sqlite_path=args.sqlite_path,
                output_dir=args.output_dir,
                reuse_prompts=args.reuse_prompts,
                title=args.title,
                bg_source=args.bg_source,
                pexels_download_link=args.pexels_download_link,
                post_date_time=post_time,
                tiktok_cookie_path=args.tiktok_cookie_path
            )
            print(f"({video_number}/{num_videos}) Successfully generated video for '{video_name}' at {video_path}")
            num_generated += 1
        except Exception as e:
            print(f"Could not generate video: {e}")

    print(f"Total videos generated: {num_generated}/{num_videos}")
