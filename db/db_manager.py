# Import external libraries
import csv
from typing import List

# Import internal libraries
from path import PROJECT_PATH
import sqlite3


class DB_Manager:

    DB_NAME = f'{PROJECT_PATH}/db/database.sqlite'

    def __init__(self):
        # Here, we use two try-catch to handle the creation and population of the database.
        # First, we try to connect to the db. If it does not exist, we catch the exception and we create the db.
        # Then, we execute a simple query to verify if the db is populated. If not, we catch the exception and we
        # populate it. This is done for the sake of this project. In this way, when you run the gateway,
        # it automatically creates and populates the db.
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
        # For simplicity, we use a SQLite db. In a real scenario, I would probably use a PostgreSQL db.
        # As the SQLite does not support Date data type, we store cut-off times as text. In a real case,
        # where we would use a PostgreSQL db, we would use a Date type.
        # Moreover, we are creating only one table to store currencies and cut-off times. This is perfectly fine, as
        # there is a 1-1 relationship. However, in a broader scope, we would probably use two different tables for
        # currencies and cut-off times. This would improve scalability.
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

    # We use a static method to get the cache. Note that we instantiate a new DB_Manager inside the method.
    # This is done to avoid opening a connection in the gateway and keep it open even though it's not used because
    # we already have the necessary data in the cache. Here, we open a connection, we use it to query the db, and
    # we close it.
    # As properly explained in the README, we decided to store te cut-off times in memory to speed up response time.
    # This can be done because the table is small and it is not frequently updated.
    @staticmethod
    def get_cache() -> dict:
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

    # This method is used to convert the cut-off time. We replace 'Never possible' and 'Always possible' with
    # 'n' and 'a', respectively. As such, we speed up the check when we execute queries. Indeed, we only need to check\
    # a character rather than a string.
    @staticmethod
    def __convert_cut_off_time(cut_off_time: str) -> str:
        if cut_off_time == 'Never possible':
            return 'n'
        elif cut_off_time == 'Always possible':
            return 'a'
        else:
            return cut_off_time

    # In the cache, we convert the cut-off time to a float. As such, we speed up the calculation of the cut-off time
    # between two currencies. As we convert 'Never possible' to -inf and 'Always possible' to +inf, we simply need to
    # find the min between the two cut-off times.
    @staticmethod
    def __convert_cut_off_time_to_float(cut_off_time: str) -> float:
        if cut_off_time == 'n':
            return float('-inf')
        elif cut_off_time == 'a':
            return float('inf')
        else:
            return float(cut_off_time)
