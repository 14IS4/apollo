from psycopg2 import connect
from apollo.secrets import PG

class postgres:
    def __init__(self):
        self.conn = connect(
            host=PG['HOST'],
            port=PG['PORT'],
            database=PG['DB'],
            user=PG['USER'],
            password=PG['PASS'],
            options=f"-c search_path={PG['SCH']}",
        )
        self.cur = self.conn.cursor()

    def query(self, qry: str) -> None:
        self.cur.execute(qry)
        self.conn.commit()

    def return_one(self, qry: str) -> str:
        '''
        Returns the first column of first row of given query.

        Intended to have a single value selected and return that value as a
        variable. It defaults to a string and then can cast to the proper
        data type on function run.

        Example: SELECT job_name FROM jobs WHERE id = job_id
        '''
        self.cur.execute(qry)
        value = self.cur.fetchone()[0]
        self.conn.commit()
        return value

    def insert_into(self, qry: str, columns: list, values: list) -> None:
        '''
        Inserts data from a query string and a columns and values list.
        
        Takes a query along with a list of column names and their corresponding
        values and formulates an insert into statement. Uses the AsIs extension
        of psycopg2 to format the column names correctly.

        https://www.psycopg.org/docs/extensions.html#psycopg2.extensions.AsIs

        Example insert into query:
        INSERT INTO table_name (%s) VALUES %s;
        '''
        from psycopg2.extensions import AsIs
        self.cur.execute(qry, (AsIs(','.join(columns)), tuple(values)))
        self.conn.commit()

    def dict_to_table(self, d: dict, table: str) -> None:
        '''
        Takes a dictionary along with a table name and inserts into the database.
        
        The dictionary keys are not modified, they need to match the column names
        in the database or the insert will fail. The order of the dictionary keys
        is not important as the column to value mapping is explicit.
        '''
        
        # Iterable Unpacking to force columns into a list. As of Python 3.3
        # calling dictionary.keys() returns an object of dict_keys. This is
        # not ideal when defining type hints as defined in PEP 484
        # https://www.python.org/dev/peps/pep-0484/
        columns = [*d.keys()]
        values = [d[column] for column in columns]
        qry = f"INSERT INTO {table} (%s) VALUES %s"
        self.insert_into(qry, columns, values)

    def close(self) -> None:
        self.cur.close()
        self.conn.close()    