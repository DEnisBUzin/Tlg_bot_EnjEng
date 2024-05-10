import psycopg2 as pc2


class WorkDB:
    """Класс соединения базы данных"""
    def __init__(self, user, password, name_db):
        self.cursor = None
        self.connection = None
        self.user = user
        self.password = password
        self.name_db = name_db

    def connect_db(self):
        """Функция соединения базы данных"""
        self.connection = pc2.connect(user=self.user, password=self.password, database=self.name_db)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """Функция закрытия соединения базы данных"""
        self.cursor.close()
        self.connection.close()
        print("[INFO] Connection is closed")


class UseDataBase(WorkDB):
    WORDS_DICT = {
        "Apple": "Яблоко",
        "Book": "Книга",
        "Car": "Машина",
        "Dog": "Собака",
        "House": "Дом",
        "Tree": "Дерево",
        "Water": "Вода",
        "Cat": "Кошка",
        "Sun": "Солнце",
        "Chair": "Стул"
    }

    WORDS_EXAMPLE = set(word.lower() for word in WORDS_DICT.keys())

    def create_structure(self):
        """Создаем структуру"""
        try:
            self.connect_db()

            sql_query_users = """CREATE TABLE IF NOT EXISTS user_information(
                                    user_id INTEGER PRIMARY KEY, 
                                    user_name VARCHAR(50),
                                    UNIQUE(user_id));"""

            self.cursor.execute(sql_query_users)

            sql_query_words = """CREATE TABLE IF NOT EXISTS words(
                                    id SERIAL PRIMARY KEY,
                                    word_en VARCHAR(80),
                                    word_ru VARCHAR(80),
                                    user_id INTEGER REFERENCES user_information(user_id));"""

            self.cursor.execute(sql_query_words)
            self.connection.commit()
            print("[INFO] Tables created successfully.")
        except Exception as er:
            print(f"[ERROR] Failed to insert record into publisher table: {er}")
        finally:
            self.close_connection()

    def add_new_word(self, word_en, word_ru, user_id):
        """Функция добавления нового слова для пользователя"""
        self.WORDS_EXAMPLE.add(word_en.lower())
        try:
            self.connect_db()
            sql_query_word = """
                        INSERT INTO words(word_en, word_ru, user_id)
                        VALUES (%s, %s, %s);
                    """
            self.cursor.execute(sql_query_word, (word_en, word_ru, user_id))
            self.connection.commit()
            print("[INFO] Add words as successfully.")
        except Exception as err:
            print(f"[ERROR] Failed to create tables: {err}")
        finally:
            self.close_connection()

    def add_new_user(self, user_id, user_name):
        """Функция добавления нового пользователя + 10 основных слов"""
        try:
            self.connect_db()

            sql_query = """
                INSERT INTO user_information(user_id, user_name)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """

            self.cursor.execute(sql_query, (user_id, user_name))
            self.connection.commit()

            for word_en, word_ru in self.WORDS_DICT.items():
                self.add_new_word(word_en.lower(), word_ru.lower(), user_id)

            print("[INFO] Add new user as successfully.")
        except Exception as err:
            print(f"[ERROR] Failed to create tables: {err}")
        finally:
            self.close_connection()

    def del_the_word(self, user_id, word):
        """Функция удаления слова у пользователя"""
        try:
            self.connect_db()

            sql_query = """
                        DELETE FROM words
                        WHERE word_ru = %s
                        AND user_id = %s;
                    """

            self.cursor.execute(sql_query, (word.lower(), user_id))
            self.connection.commit()
            print("[INFO] Delite success!")
        except Exception as err:
            print(f"[ERROR] Failed to create tables: {err}")
        finally:
            self.close_connection()

    def get_word(self, user_id):
        """Функция получения всех слов пользователя"""
        try:
            self.connect_db()

            sql_query = """
                            SELECT word_en, word_ru
                            FROM words
                            WHERE user_id = %s;
                        """

            self.cursor.execute(sql_query, (user_id, ))
            answer = self.cursor.fetchall()
            return answer
        except Exception as err:
            print(f"[ERROR] Failed: {err}")
        finally:
            self.close_connection()

    def get_other_word(self, user_id, word):
        """Функция получения других слов пользователя"""
        try:
            self.connect_db()
            sql_query = """
                            SELECT DISTINCT word_en
                            FROM words
                            WHERE user_id = %s
                            AND word_ru != %s;
                        """
            self.cursor.execute(sql_query, (user_id, word))
            answer = self.cursor.fetchall()
            return answer
        except Exception as err:
            print(f"[ERROR] Failed: {err}")
        finally:
            self.close_connection()

    def get_the_word(self, user_id, word):
        """Функция получения конкретного слова пользователя"""
        try:
            self.connect_db()
            sql_query = """
                            SELECT word_en
                            FROM words
                            WHERE user_id = %s
                            AND word_ru = %s;
                        """
            self.cursor.execute(sql_query, (user_id, word))
            answer = self.cursor.fetchall()
            return answer
        except Exception as err:
            print(f"[ERROR] Failed: {err}")
            return False
        finally:
            self.close_connection()


if __name__ == '__main__':
    newClass = UseDataBase('postgres', '310535', 'enjoy_english')
    # newClass.create_structure()
    print(newClass.WORDS_EXAMPLE)
    print(newClass.get_word('463243140'))
    print(newClass.get_other_word('463243140', 'собака'))