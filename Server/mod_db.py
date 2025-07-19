import psycopg2
import hashlib
import secrets
import uuid


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

    def _list_students(self):
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
