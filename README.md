# Video Bot
This is a bot that chooses a ChatGPT-generated prompt
from an SQLite datbase, generates a voiceover using Whisper, queries and chooses a random background image from Giphy, generates captions using
gTTS, and finally combines them into a video

## Setup (Ubuntu / Windows + WSL2)
1. Create your Python virtual environment

    ```
    python3 -m venv venv && source venv/bin/activate
    ```

2. Install Python requirements

    ```
    pip install -r requirements.txt &&
    pip install git+https://github.com/openai/whisper.git
    ```

3. Install Ubuntu packages

    ```
    sudo apt-get install imagemagick ffmpeg
    ```
    3a. Tweak Imagemagick config: https://askubuntu.com/a/879784

4. Create video output directory in root directory of this project
    ```
    mkdir output
    ```
    4a. If you're on Windows using WSL2, move the SQLite database (`data/post_prompts.db`) to a Windows directory

5. Generate a vid!
    ```
    export GIPHY_API_KEY="<insert api key here>" && python3 src/main.py --sqllite_path '/path/to/post_prompts.db' --output_dir 'output/'
    ```

## SQLite Database

- [TEXT] title
- [TEXT] prompt
- [TEXT] content
- [BOOL] used
