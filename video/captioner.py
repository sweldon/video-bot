"""
Generates and attaches captions to the video
"""

import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
import stable_whisper

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
        self.video_size = self.videomanager.video.size
        self.stroked_subtitles = []
        self.font_size = 48
        self.font_color = 'white'
        self.font_face = 'Heavitas'
        self.stroke_width = 3
        self.stroke_color = 'black'

    def generate(self) -> None:

        # model = whisper.load_model("base")
        temp_file = "%s.mp3" % os.path.join(self.title_dir, 'temp')


        model = stable_whisper.load_model('base')
        result = model.transcribe(temp_file)

        result.to_srt_vtt(self.output_srt, segment_level=False, word_level=True)
        # There is a bug in moviepy SubtitlesClip where if there arent 2 lines at
        # the bottom of the SRT, the subtitles wont be shown in the video.
        with open(self.output_srt, "a", encoding="utf-8") as f:
            f.write("\n\n")

    def attach(self) -> None:
        """
        Attaches generated (self.generate) subtitles to a video
        """
        # Generate the captions
        self.generate()

        if os.path.exists(self.output_srt):
            # Combine the video with the captions
            subtitles = SubtitlesClip(
                self.output_srt,
                lambda txt: TextClip(
                txt,
                fontsize=self.font_size,
                color=self.font_color,
                font=self.font_face,
                size=(self.video_width, self.video_height*1/2),
                method='caption',
                align='center',
                stroke_width=self.stroke_width,
                stroke_color=self.stroke_color,
            ),
            )
            video_with_subtitles = CompositeVideoClip(
                [
                    self.videomanager.video,
                    subtitles.set_position(("center", "bottom")),
                ],
            )
            output_vid = "%s.mp4" % os.path.join(self.title_dir, self.title)
            video_with_subtitles.write_videofile(
                output_vid, codec="libx264",
                bitrate="10000k",
                fps=self.videomanager.video.fps
            )

            print(f"Done! Final video saved to -> {output_vid}")
