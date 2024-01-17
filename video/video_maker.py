"""
Given a voiceover audio file and a background image/mp4, combines
them into a video. Also resizes to an HD height and then crops it
to a popular social media aspect ratio (9:16)
"""

import os
import moviepy.editor as mp
from moviepy.video.fx.all import crop

class VideoMaker:


    def generate_video(self, audio_file_path, image_path, title_dir, duration):


        audio = mp.AudioFileClip(audio_file_path)
        video1 = mp.VideoFileClip(image_path)
        # Loop the background GIF as many times as necessary to last the entire
        # prompt voiceover
        video1 = video1.loop(duration=duration)
        # Resize to HD height
        video1 = video1.resize(height=1280)
        
        # Crop to popular vertical social media aspect ration (9:16)
        (w, h) = video1.size
        crop_width = h * 9/16
        x1, x2 = (w - crop_width)//2, (w+crop_width)//2
        y1, y2 = 0, h
        video1 = crop(video1, x1=x1, y1=y1, x2=x2, y2=y2)

        # Combine the looped background with the audio
        final = video1.set_audio(audio)
        dubbed_video ="%s.mp4" % os.path.join(title_dir, 'post_video_dubbed')
        final.write_videofile(
            dubbed_video,
            fps=30,
            threads=1
        )
        return dubbed_video
