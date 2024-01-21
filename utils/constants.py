"""
Valid 9:16 ratio heights for cropping. When cropping a video,
moviepy requires the height to be a valid 9:16 aspect ratio.
So, we use these valid heights and resize the video height as
little as possible to the closest height in this list.
Sourced from https://www.studio1productions.com/Articles/16x9-Resolution.htm
"""
VIDEO_RATIO_HEIGHTS = [
    16,128,256,384,432,512,640,768,896,
    960,1024,1152,1280,1360,1408,1536,
    1664,1792,1920,2048,2176,2304,2432,
    2560,2688,2816,2944,3072,3200,3328,
    3456,3584,3712,3840,3968,4096
]

ACCENTS_ENGLISH = [
    "com.au",
    "co.uk",
    "us",
    "ca",
    "co.in",
    "ie",
    "co.za"
]