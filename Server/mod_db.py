import psycopg2
import hashlib
import secrets
import uuid
import random


class mods_database:
    def __init__(self):
        self
        self.conn = self._init_con()
        self.cursor = self.conn.cursor()

    def _init_con(self):
        conn = psycopg2.connect(
            database="postgres",
            host="127.0.0.1",
            user="wongwh",
            password="wongwh",
            port="5432",
        )
        conn.autocommit = True
        return conn

    def _reset_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS student_session_modules")
        self.cursor.execute("DROP TABLE IF EXISTS student_sessions")
        self.cursor.execute("DROP TABLE IF EXISTS student_groups")
        self.cursor.execute("DROP TABLE IF EXISTS groups")
        self._initialise_db()

    def create_db(self):
        sql = """CREATE database mydb"""
        # Creating a database
        self.cursor.execute(sql)
        print("Database created successfully........")

    def _create_student_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS students")
        sql = """CREATE TABLE students(
            student_id VARCHAR PRIMARY KEY,
            password VARCHAR
        )"""
        self.cursor.execute(sql)

    def _create_modules_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS modules")
        sql = """CREATE TABLE modules(
        module_id VARCHAR PRIMARY KEY,
        module_name VARCHAR NOT NULL
        )"""
        self.cursor.execute(sql)

    def _create_session_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS sessions")
        sql = """CREATE TABLE sessions(
        session_id VARCHAR PRIMARY KEY
        )"""
        self.cursor.execute(sql)

    def _create_group_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS groups")
        sql = """CREATE TABLE groups(
        group_id VARCHAR PRIMARY KEY,
        module_id VARCHAR NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
        session_id VARCHAR NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE
        )"""
        self.cursor.execute(sql)

    def _create_student_group_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS student_groups")
        sql = """CREATE TABLE student_groups(
        student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
        group_id VARCHAR REFERENCES groups(group_id) ON DELETE CASCADE,
        PRIMARY KEY (student_id, group_id)
        )"""
        self.cursor.execute(sql)

    def _create_student_session_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS student_sessions")
        sql = """CREATE TABLE student_sessions(
        student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
        session_id VARCHAR REFERENCES sessions(session_id) ON DELETE CASCADE,
        preference JSONB,
        PRIMARY KEY (student_id, session_id)
        )"""
        self.cursor.execute(sql)

    def _create_student_session_module_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS student_session_modules")
        sql = """CREATE TABLE student_session_modules(
        student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
        session_id VARCHAR REFERENCES sessions(session_id) ON DELETE CASCADE,
        module_id VARCHAR REFERENCES modules(module_id) ON DELETE CASCADE,
        PRIMARY KEY (student_id, session_id, module_id)
        )"""
        self.cursor.execute(sql)

    def _initialise_db(self):
        # self.create_db()
        self._create_student_table()
        self._create_modules_table()
        self._create_session_table()
        self._create_group_table()
        self._create_student_group_table()
        self._create_student_session_table()
        self._create_student_session_module_table()

    def add_student(self, student_id, password):
        if self._is_student_exists(student_id):
            print("[Add Student] student already exists")
            return False
        hashed_password = self._hash_password(password)
        sql = """INSERT INTO students (student_id, password)
                VALUES (%s, %s)
                """
        params = (student_id, hashed_password)
        self.cursor.execute(sql, params)

    def list_students(self):
        sql = """SELECT * FROM students"""
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(f"[List Students] {row}")

    def _hash_password(self, password):
        salt = secrets.token_hex(16)  # 32char salt
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"{salt}:{hashed.hex()}"

    def _verify_password(self, stored_hash, input_password):
        salt, original_hash = stored_hash.split(":")
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", input_password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return secrets.compare_digest(new_hash, original_hash)

    def _is_student_exists(self, student_id) -> bool:
        self.cursor.execute(
            "SELECT 1 FROM students WHERE student_id = %s", (student_id,)
        )
        return self.cursor.fetchone() is not None

    def _generate_random_id(self):
        min = 0
        max = 999
        digits = [str(random.randint(min, max)) for i in range(2)]
        digits = [(len(str(max)) - len(digit)) * "0" + digit for digit in digits]
        return "-".join(digits)

    def _is_session_exists(self, id):
        self.cursor.execute("SELECT 1 FROM sessions WHERE session_id = %s", (id,))
        return self.cursor.fetchone() is not None

    def _return_unique_session_id(self):
        while True:
            new_session_id = self._generate_random_id()
            if not self._is_session_exists(new_session_id):
                return new_session_id

    def generate_session_id(self):
        return self._return_unique_session_id()

    """
        to create new session:
        press new session button, generate_session_id
        return session_id to front end
        front end show session_id
        check student usrname and password
    """


if __name__ == "__main__":
    db = mods_database()
    print(db.generate_session_id())
