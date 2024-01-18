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
        self.video_size = self.videomanager.video.size
        self.stroked_subtitles = []
        self.font_size = 60
        self.font_color = 'white'
        self.font_face = 'Arial-bold'
        self.stroke_width = 10
        self.stroke_color = 'black'

    def generate(self) -> None:

        model = whisper.load_model("base")
        temp_file = "%s.mp3" % os.path.join(self.title_dir, 'temp')
        transcribe = model.transcribe(audio=temp_file, fp16=False)
        segments = transcribe["segments"]

        # Transcribe audio and write caption segments to a file
        with open(self.output_srt, "w", encoding="utf-8") as f:
            
            for seg in segments:
                start_time = seg["start"]
                end_time = seg["end"]

                start_secs = timedelta(seconds=int(start_time))
                end_secs =  timedelta(seconds=int(end_time))
                start = (str(0) + str(start_secs) + ",000")
                end = str(0) + str(end_secs) + ",000"
                text = seg["text"]
                segment_id = seg["id"] + 1
                segment = f"{segment_id}\n{start} --> {end}\n{text[1:] if text[0] == ' ' else text}\n\n"

                # Write segment to subtitle SRT file
                f.write(segment)

                # Since out-of-the-box stroke is bad, do some custom magic to add nice-looking subtitle outlining
                duration = float(end_time) - float(start_time)
                subtitle_x_position = "center"
                subtitle_y_position = self.video_height * 4/9

                # Create a TextClip to act as the outline, i.e. stroke. This will be combined with a regular TextClip
                # to present a nice outline
                text_clip_stroke = TextClip(
                    seg["text"],
                    fontsize=self.font_size,
                    color=self.font_color,
                    font=self.font_face,
                    stroke_width=self.stroke_width,
                    stroke_color=self.stroke_color,
                    size=(self.video_width*1/2, self.video_height*1/2),
                    method='caption',
                    align='center',
                ).set_duration(duration)
                # Align the text clip with the subtitle segment
                text_clip_stroke = text_clip_stroke.set_start(float(start_time))
                text_clip_stroke = text_clip_stroke.set_position((subtitle_x_position, subtitle_y_position))

                # Create the regular text clip, outlined by the layer above (stroked TextClip)
                text_clip = TextClip(
                    seg["text"],
                    fontsize=self.font_size,
                    color=self.font_color,
                    font=self.font_face,
                    size=(self.video_width*1/2, self.video_height*1/2),
                    method='caption',
                    align='center',
                ).set_duration(duration)

                # Align the text clip with the subtitle segment
                text_clip = text_clip.set_start(float(start_time))
                text_clip = text_clip.set_position((subtitle_x_position, subtitle_y_position))

                # Combine the stroke text clip with the normal text clip
                stroked_text_clip = CompositeVideoClip([text_clip_stroke, text_clip], size=self.video_size)
                # Queue all of the clips up to be combined with the video, via self.generate
                self.stroked_subtitles.append(stroked_text_clip)

    def attach(self) -> None:
        """
        Attaches generated (self.generate) subtitles to a video
        """
        self.generate()
        if os.path.exists(self.output_srt):

            video_with_subtitles = CompositeVideoClip(
                [
                    self.videomanager.video,
                    *self.stroked_subtitles
                ]
            )
            output_vid = "%s.mp4" % os.path.join(self.title_dir, self.title)
            video_with_subtitles.write_videofile(
                output_vid, codec="libx264",
                bitrate="10000k",
                fps=self.videomanager.video.fps
            )

            print(f"Final video saved to -> {output_vid}")
