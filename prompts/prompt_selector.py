"""
Manages selection of the video prompt. The background
and subtitles will be generated based on what this manager
selects
"""
from contextlib import contextmanager
import sqlite3


# Manager for database connection
@contextmanager
def prompt_db_manager(db_path):
    con = sqlite3.connect(db_path)
    try:
        yield con
    finally:
       con.commit()
       con.close()


class PromptSelector:

    def __init__(self, sqllite_path):
        self.sqllite_path = sqllite_path
        print(self.sqllite_path)

    def select_prompt(self):
        prompt = None

        with prompt_db_manager(self.sqllite_path) as prompt_cursor:
            res = prompt_cursor.cursor().execute(
                "SELECT title, content FROM prompts where content != '' and used != 1 ORDER BY RANDOM() LIMIT 1;"
            )
            title, prompt = res.fetchone()
            
        return title, prompt

    def get_all_prompts(self):

        with prompt_db_manager(self.sqllite_path) as prompt_cursor:
            res = prompt_cursor.cursor().execute(
                "SELECT title, content FROM prompts where content != ''"
            )
            return res.fetchall()

    def mark_as_used(self, title):

        with prompt_db_manager(self.sqllite_path) as prompt_cursor:

            prompt_cursor.cursor().execute(
                f"UPDATE prompts SET used=1 WHERE title='{title}'"
            )
