"""
Given a voiceover audio file and a background image/mp4, combines
them into a video. Also resizes to an HD height and then crops it
to a popular social media aspect ratio (9:16)
"""

import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop
from utils.constants import VIDEO_RATIO_HEIGHTS


class VideoMaker:

    def get_closest_ratio_height(self, video_height):
        """
        In order for moviepy to be able to crop videos to 9:16, the height
        needs to be a true 9:16 widescreen size. So here we resize the vid
        height to the closest true value for the smallest change.
        """
        return min(VIDEO_RATIO_HEIGHTS, key=lambda x:abs(x-video_height))

    def generate_video(
        self,
        audio_file_path,
        video_path,
        title_dir,
        duration
    ):
        audio = mp.AudioFileClip(audio_file_path)
        video = mp.VideoFileClip(video_path)

        # Set the background video length to the length of the
        # prompt voiceover
        video = video.loop(duration=duration)
        (w, h) = video.size

        # Before cropping, height has to be a valid 9:16 value
        updated_height = self.get_closest_ratio_height(h)
        video = video.resize(height=updated_height)

        # Crop to popular vertical social media aspect ratio (9:16)
        (w, h) = video.size
        crop_width = h * 9/16
        x1, x2 = (w - crop_width)//2, (w+crop_width)//2
        y1, y2 = 0, h
        video = crop(video, x1=x1, y1=y1, x2=x2, y2=y2)

        # Combine the looped background with the audio
        final = video.set_audio(audio)
        dubbed_video ="%s.mp4" % os.path.join(title_dir, 'post_video_dubbed')
        final.write_videofile(
            dubbed_video,
            fps=video.fps,
            threads=1
        )
        return dubbed_video
