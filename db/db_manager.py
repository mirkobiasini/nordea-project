# Import external libraries
import csv
from typing import List

# Import internal libraries
from path import PROJECT_PATH
import sqlite3


class DB_Manager:

    DB_NAME = f'{PROJECT_PATH}/db/database.sqlite'

    def __init__(self):
        # TODO Explain why try-catch
        res = None
        try:
            self._con = sqlite3.connect(DB_Manager.DB_NAME, timeout=20)
            with self._con:
                res = self._con.execute("SELECT iso FROM cut_off_times LIMIT 1")
        except sqlite3.OperationalError:
            print('Run db_manager and RESET THE DATABASE.')
            self.create_db()
        try:
            assert res.fetchone()
        except (AssertionError, AttributeError):
            self.init_rows()

    def create_db(self):
        # TODO Explain date type not available in SQLite
        with self._con:
            return self._con.execute(
                """
                 CREATE TABLE cut_off_times(
                    iso text PRIMARY KEY,
                    country text NOT NULL,
                    today text NOT NULL,
                    tomorrow text NOT NULL,
                    after_tomorrow text NOT NULL
                );
                """
            )

    def init_rows(self):
        with open(f'{PROJECT_PATH}/data.csv', newline='') as csvfile:
            data_dict = csv.DictReader(csvfile, delimiter=',')
            with self._con:
                self._con.executemany(
                    "INSERT INTO cut_off_times(iso, country, today, tomorrow, after_tomorrow) values (?, ?, ?, ?, ?)",
                    [
                        (
                            row['ISO'],
                            row['Country'],
                            self.__convert_cut_off_time(row['Today']),
                            self.__convert_cut_off_time(row['Tomorrow']),
                            self.__convert_cut_off_time(row['After Tomorrow'])
                        )
                        for row in data_dict
                    ]
                )

    def close(self):
        self._con.close()

    def get_all_cut_off_times(self) -> List[dict]:
        with self._con:
            cursor = self._con.execute("SELECT iso, country, today, tomorrow, after_tomorrow FROM cut_off_times")
            return [{
                'iso': row[0],
                'country': row[1],
                'today': row[2],
                'tomorrow': row[3],
                'after_tomorrow': row[4]
            } for row in cursor.fetchall()]

    @staticmethod
    def get_cache() -> dict:
        # TODO Explain we open and close here to avoid in gateway
        db = DB_Manager()
        cut_off_times = db.get_all_cut_off_times()
        db.close()
        cache = {
            cut_off_time['iso']: {
                'country': cut_off_time['country'],
                'today': DB_Manager.__convert_cut_off_time_to_float(cut_off_time['today']),
                'tomorrow': DB_Manager.__convert_cut_off_time_to_float(cut_off_time['tomorrow']),
                'after_tomorrow': DB_Manager.__convert_cut_off_time_to_float(cut_off_time['after_tomorrow'])
            }
            for cut_off_time in cut_off_times
        }
        return cache

    @staticmethod
    def __convert_cut_off_time(cut_off_time: str) -> str:
        if cut_off_time == 'Never possible':
            return 'n'
        elif cut_off_time == 'Always possible':
            return 'a'
        else:
            return cut_off_time

    @staticmethod
    def __convert_cut_off_time_to_float(cut_off_time: str) -> float:
        if cut_off_time == 'n':
            return float('-inf')
        elif cut_off_time == 'a':
            return float('inf')
        else:
            return float(cut_off_time)
