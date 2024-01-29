"""
Handle arguments from user input
"""

import argparse
import datetime

def process_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--sqlite_path',
        type=str,
        required=True,
        help='Absolute path to SQLite file with prompts'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Absolute path to where video directories will be made'
    )
    parser.add_argument(
        '--reuse_prompts',
        action='store_true',
        help='If used, prompts will not be flagged as used in database and can be reused later'
    )
    parser.add_argument(
        '--title',
        type=str,
        help='Specific title to query out of the prompts db and use for the video'
    )
    parser.add_argument(
        '--bg_source',
        type=str,
        default="pexels",
        help='Source of the background video. Current accepted values: giphy, pexels (default)'
    )
    parser.add_argument(
        '--num_videos',
        type=int,
        default=1,
        help='Number of videos to generate'
    )
    parser.add_argument(
        '--pexels_download_link',
        type=str,
        help='Direct link to video to use as a background from Pexels'
    )
    parser.add_argument(
        '--post_date_times',
        type=lambda s: [datetime.datetime.strptime(dt, '%Y-%m-%d-%H-%M') for dt in s.split(",")] if s else None,
        help=(
            'Comma-delimited list of scheduled naive times to post videos, in the format YYYY-MM-DD-HH-MM. '
            'The number of times provided should match the `num_videos` parameter.'
        )
    )
    parser.add_argument(
        '--tiktok_cookie_path',
        type=str,
        help='Path to file storing TikTok session cookie for posting authentication'
    )
    args = parser.parse_args()
    return args
