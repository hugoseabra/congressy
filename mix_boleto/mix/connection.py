from pymysql import cursors, connect, DatabaseError


class MixConnection(object):
    """ Gerencia conexões com mysql. """

    def __init__(self, sync_resource_id, host, user, password, db_name):
        self.sync_resource_id = sync_resource_id
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

        self.connection = None
        self.connected = False

    def connect(self):
        if self.connected:
            return

        # Connect to the database
        self.connection = connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db_name,
            charset='utf8mb4',
            cursorclass=cursors.DictCursor
        )
        self.connected = True

    def fetch_one(self, sql):

        self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchone()

        except DatabaseError:
            pass

    def fetch(self, sql):

        self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

        except DatabaseError:
            pass

    def insert(self, sql):

        self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute(sql)

        self.connection.commit()

    def update(self, sql):

        self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute(sql)

        self.connection.commit()

    def close(self):
        self.connection.close()
        self.connected = False
