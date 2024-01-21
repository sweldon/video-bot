"""
Given a prompt, generates a voiceover for the video
"""


from gtts import gTTS 
import os  
from mutagen.mp3 import MP3
import os
from pydub import AudioSegment
from typing import Optional
import sys
import random
sys.path.insert(0, '../post_bot/')
from utils.constants import ACCENTS_ENGLISH

class Speaker:

    def generate_audio(
        self,
        content: str,
        path: str,
        language: str = 'en',
        speedup_multiplier: Optional[float] = None
    ) -> str:
        """
        Generates a voice-over of a prompt, and applies a random accent
        from the English language
        """
        file_path = "%s.mp3" % os.path.join(path, 'post_audio')
        random_accent_index = random.randint(0, len(ACCENTS_ENGLISH) - 1)
        random_accent = ACCENTS_ENGLISH[random_accent_index]
        print(f"Using accent: '{random_accent}'")

        audio = gTTS(text=content, lang=language, slow=False, tld=random_accent)
        audio.save(file_path)

        if speedup_multiplier is not None:
            # Speed-up the voice a bit (gtts doesn't allow that natively yet)
            audio = AudioSegment.from_mp3(file_path)
            a = audio.speedup(playback_speed=speedup_multiplier)
            a.export(file_path, format="mp3")

        return file_path

    def get_duration(self, file_path):
        audio = MP3(file_path)
        return audio.info.length
