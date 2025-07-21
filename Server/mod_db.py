from collections import defaultdict
from pprint import pprint
import psycopg2
import hashlib
import secrets
import uuid
import random
import datetime
import requests


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
        title TEXT,
        sem1_json JSONB,
        sem2_json JSONB
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

    def add_new_session(self, new_session_id):
        self.cursor.execute(
            "INSERT INTO sessions (session_id) VALUES (%s)", (new_session_id,)
        )

    def _get_all_modules_names(self, year):
        all_modules = requests.get(
            f"https://api.nusmods.com/v2/{year}-{year + 1}/moduleList.json"
        ).json()
        return all_modules

    def _get_year_and_sem(self):
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        if month < 6:
            year -= 1
            sem = 2
        else:
            sem = 1
        return (year, sem)

    def _load_mod_data(self, mod, year, semester) -> tuple[dict, dict, dict]:
        return_dict = {}

        print(f"loading data for {mod} semester {semester}")
        data = requests.get(
            f"https://api.nusmods.com/v2/{year}-{year + 1}/modules/{mod}.json"
        ).json()
        semesters = data["semesterData"]
        if len(semesters) == 1:
            if semester != semesters[0]["semester"]:
                return None

        if semester == 2:
            semester_timetable: list = (
                data["semesterData"][0]["timetable"]
                if data["semesterData"][0]["semester"] == 2
                else data["semesterData"][1]["timetable"]
            )
        elif semester == 1:
            semester_timetable: list = (
                data["semesterData"][0]["timetable"]
                if data["semesterData"][0]["semester"] == 1
                else data["semesterData"][1]["timetable"]
            )

        for lesson in semester_timetable:
            slot_info = {
                "startTime": lesson["startTime"],
                "endTime": lesson["endTime"],
                "weeks": lesson["weeks"],
                "day": lesson["day"],
            }
            lesson_type = lesson["lessonType"]
            class_no = lesson["classNo"]

            if mod not in return_dict:
                return_dict[mod] = {}

            if lesson_type not in return_dict[mod]:
                return_dict[mod][lesson_type] = {}

            if class_no not in return_dict[mod][lesson_type]:
                return_dict[mod][lesson_type][class_no] = {"slots": []}

            return_dict[mod][lesson_type][class_no]["slots"].append(slot_info)

        print(f"loaded data for {mod}")
        return return_dict

    def _load_modules_data(self):
        SEM_1 = 1
        SEM_2 = 2
        year, _ = self._get_year_and_sem()
        all_modules = self._get_all_modules_names(year)
        module_dict = {}
        for module in all_modules[:1]:

            modulecode = module["moduleCode"]
            pprint(module)
            module_dict[modulecode] = {
                "title": module["title"],
                "sem1": self._load_mod_data(modulecode, year, SEM_1),
                "sem2": self._load_mod_data(modulecode, year, SEM_2),
            }
        return module_dict

    def _populate_modules_db(self):
        all_modules_dict = self._load_modules_data()
        for module, module_info in all_modules_dict.items():
            


if __name__ == "__main__":
    db = mods_database()

    pprint(db._reset_db())
