# Video Bot
A bot that uses ChatGPT-generated prompts and creates social media-ready videos with AI-generated captions and voice-overs. The prompts are stored in and queried from an SQLite database, and then used to generate a voice-over using gTTS (Google Text-to-Speech). The prompt topic is then used to search and download a relevant background for the video, which can be either another video (royalty free via the Pexels API), GIF (Giphy API) or a random image from a given directory. Finally, subtitles are generated and added based on the voice-over using OpenAI Whisper. It's all brought together using moviepy.

## Setup (Ubuntu / Windows + WSL2)
1. Create your Python virtual environment

    ```
    python3 -m venv venv && source venv/bin/activate
    ```

1. Install Python requirements

    ```
    pip install -r requirements.txt &&
    pip install stable-ts
    ```

1. Install Ubuntu packages

    ```
    sudo apt-get install imagemagick ffmpeg
    ```
    - Tweak Imagemagick config: https://askubuntu.com/a/879784

1. Create video output directory in root directory of this project
    ```
    mkdir output
    ```
    - If you're on Windows using WSL2, move the SQLite database (`data/post_prompts.db`) to a Windows directory

1. [Optional] Install 'Heavitas' font
    - Ubuntu/WSL2
        - Copy `fonts/Heavitas.ttf` to `/usr/local/share/fonts/`
            - Can also be downloaded from https://www.dafont.com/heavitas.font
        - Run `sudo fc-cache -f -v` to refresh the fonts

1. Generate a vid!
    ```
    export PEXELS_API_KEY="<insert api key here>" && python3 src/main.py --sqllite_path '/path/to/post_prompts.db' --output_dir 'output/'
    ```
    - Can also use `GIPHY_API_KEY` if leveraging `--bg_source giphy`

### More Examples
- Scheduling 2 videos to be posted on TikTok the next day

    ```
    python3 main.py --sqlite_path /path/to/post_bot/data/post_prompts.db --output_dir '/path/to/post_bot/output/' --num_videos 2 --post_date_times 2024-01-25-15-00,2024-01-26-00-00 --tiktok_cookie_path /path/to/tiktok_cookies.txt
    ```

## Parameters
- [Required] sqllite_path: absolute path to the SQLite file containing prompts generated by OpenAI. The gTTS voice-overs are generated based on these.
- [Required] output_dir: directory where video outputs will be written. Folders will be created here named after each video
- title: If specified, will generate a video from the database matching this title
- bg_source: Source to use for background videos. Valid options are: `giphy`, `pexels`
- reuse_prompts: If this flag is provided, videos will not be flagged as used in the database, allowing you to regenerate them. Otherwise, you can only generate a video for a prompt once so theyre not duplicated
- num_videos: Number of videos to generate, usefull for generating vids in bulk.
- pexels_download_link: If you know the video you want to use, you can provide the download link here.
- post_date_times: Comma-delimited list of scheduled naive times to post videos, in the format YYYY-MM-DD-HH-MM. The number of times provided should match the `num_videos` parameter.

## SQLite Database
- [INT] id
- [TEXT] title
- [TEXT] content
- [BOOL] used
