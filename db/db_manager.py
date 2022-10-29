# Import internal libraries
from path import PROJECT_PATH


class DB_Manager:

    DB_NAME = f'{PROJECT_PATH}/db/database.sqlite'

    def __init__(self):
        try:
            self._con = sqlite3.connect(DB_Manager.DB_NAME, timeout=20)
        except FileNotFoundError:
            logger.critical('Run db_api and RESET THE DATABASE.')
        self._con.row_factory = sqlite3.Row
        self.__check_is_thread_safe()
        self.pools = self._Pools(db_manager=self)
        self.contracts = self._Contracts(db_manager=self)
        self.orders = self._Orders(db_manager=self)
        self.prices = self._Prices(db_manager=self)
        logger.debug(
            f'I am running SQLITE Version: {[v[0] for v in self._fetchall(query="SELECT sqlite_version();")]}'
        )

