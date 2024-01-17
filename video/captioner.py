"""
Setup notes for adding captions:
1. Ubuntu: Install ffmpeg, imagemagick (via sudo apt install)
2. Python: Install python whisper using:
    pip install git+https://github.com/openai/whisper.git
4. Comment appropriate lines: https://askubuntu.com/a/879784
"""

import os
from datetime import timedelta
import whisper
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip


class DubbedVideoManager:
    def __init__(self, dubbed_video, title_dir) -> None:
        self.video = VideoFileClip(dubbed_video)
        self.title_dir = title_dir
        self.extract_audio()

    def extract_audio(self) -> None:
        if self.video.audio is not None:
            temp_file = "%s.mp3" % os.path.join(self.title_dir, 'temp')
            self.video.audio.write_audiofile(temp_file, codec="mp3")
        else:
            print("Video has no audio, quitting")
            exit(1)


class SubtitleGenerator:
    def __init__(self, videomanager: DubbedVideoManager, title_dir) -> None:
        self.videomanager = videomanager
        self.output_srt = "%s.srt" % os.path.join(title_dir, 'output')
        self.title_dir = title_dir
        self.title = title_dir.split("/")[-1]
        self.video_width, self.video_height = self.videomanager.video.size


    def generate(self) -> None:

        model = whisper.load_model("base")
        temp_file = "%s.mp3" % os.path.join(self.title_dir, 'temp')
        transcribe = model.transcribe(audio=temp_file, fp16=False)
        segments = transcribe["segments"]

        # Write caption segments to a file, based on input audio
        for seg in segments:
            start_secs = timedelta(seconds=int(seg["start"]))
            end_secs =  timedelta(seconds=int(seg["end"]))
            start = (str(0) + str(start_secs) + ",000")
            end = str(0) + str(end_secs) + ",000"
            text = seg["text"]
            segment_id = seg["id"] + 1
            segment = f"{segment_id}\n{start} --> {end}\n{text[1:] if text[0] == ' ' else text}\n\n"
            with open(self.output_srt, "a", encoding="utf-8") as f:
                f.write(segment)

    def attach(self) -> None:
        """
        Generates subtitles and attaches them to a video
        """
        self.generate()
        if os.path.exists(self.output_srt):
            subtitles = SubtitlesClip(
                self.output_srt,
                lambda txt: TextClip(
                    txt,
                    font="Georgia-Bold",
                    fontsize=48,
                    color="black",
                    bg_color="white",
                    method="caption",
                    # stroke_color="black",
                    # stroke_width=1,
                    # size=self.videomanager.video.size
                    # size=(self.video_width*3/4 + 3, None),
                    # fontsize=72, stroke_width=12, color="white",
                    # stroke_color="black"
                ),
            )

            video_with_subtitles = CompositeVideoClip(
                [
                    self.videomanager.video,
                    subtitles.set_position(("center", "bottom")),
                    # subtitles.set_position((.40, .75), relative=True),
                ]
            )
            output_vid = "%s.mp4" % os.path.join(self.title_dir, self.title)
            video_with_subtitles.write_videofile(
                output_vid, codec="libx264",
                bitrate="10000k",
                fps=self.videomanager.video.fps
            )

            print(f"Final video saved to -> {output_vid}")
