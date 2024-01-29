from tiktok_uploader.upload import upload_video
from utils.constants import TIKTOK_HASHTAGS
import datetime

class TikTokUploader:

    def post_video(
        self,
        video_path: str,
        description: str,
        cookie_file: str,
        post_date_time: datetime.datetime = None
    ):
        """
        :param post_date_time: Scheduled time of post in a naive daitetime
        """
        universal_hashtags = " ".join(TIKTOK_HASHTAGS)
        description += f" {universal_hashtags}"

        upload_video(
            filename=video_path,
            description=description,
            cookies=cookie_file,
            schedule=post_date_time
        )
