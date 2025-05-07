import sqlite3

class DatabaseHandler:
    def __init__(self, db_file='data.db'):
        self.conn = sqlite3.connect(db_file)
        self.__create_table()

    def __create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS extracted_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            text TEXT
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def insert(self, image_path, text):
        query = 'INSERT INTO extracted_text (image_path, text) VALUES (?, ?)'
        self.conn.execute(query, (image_path, text))
        self.conn.commit()

    def get_all_data(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT image_path, text FROM extracted_text')
        return cursor.fetchall()
