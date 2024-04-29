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
                                    id SERIAL PRIMARY KEY, 
                                    user_id INTEGER, 
                                    user_name VARCHAR(50),
                                    UNIQUE(user_id));"""

            self.cursor.execute(sql_query_users)

            sql_query_words = """CREATE TABLE IF NOT EXISTS words(
                                    id SERIAL PRIMARY KEY,
                                    word_en VARCHAR(80),
                                    word_ru VARCHAR(80),
                                    user_id INTEGER REFERENCES user_information(id));"""

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
                        VALUES (%s, %s, 
                        (SELECT id FROM user_information
                        WHERE user_id = %s));
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
                VALUES (%s, %s);
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
                        AND user_id = (SELECT id FROM user_information WHERE user_id = %s);
                    """

            self.cursor.execute(sql_query, (word.lower(), user_id))
            self.connection.commit()
            print("[INFO] Delite successfully.")
        except Exception as err:
            print(f"[ERROR] Failed to create tables: {err}")
        finally:
            self.close_connection()


if __name__ == '__main__':
    newClass = UseDataBase('postgres', '310535', 'enjoy_english')
    # newClass.create_structure()
    # newClass.add_new_user("12345", "katya")
    newClass.del_the_word("1234", "яблоко")
    print(newClass.WORDS_EXAMPLE)
