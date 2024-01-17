"""
Given a prompt, generates a voiceover for the video
"""


from gtts import gTTS 
import os  
from mutagen.mp3 import MP3
import os
import shutil
from pydub import AudioSegment

class Speaker:

    def generate_audio(self, content, path, language='en'):

            
        file_path = "%s.mp3" % os.path.join(path, 'post_audio')
        audio = gTTS(text=content, lang=language, slow=False)
        audio.save(file_path)

        # Speed-up the voice a bit (gtts doesn't allow that yet)
        audio = AudioSegment.from_mp3(file_path)
        a = audio.speedup(playback_speed=1.1)
        a.export(file_path, format="mp3")

        return file_path

    def get_duration(self, file_path):
        audio = MP3(file_path)
        return audio.info.length
