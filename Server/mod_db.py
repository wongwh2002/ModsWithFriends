from collections import defaultdict
import json
from pprint import pprint
import psycopg2
import hashlib
import secrets
import uuid
import random
import datetime
import requests
import os
from dotenv import load_dotenv
import string

load_dotenv()


SEM1 = "sem1"
SEM2 = "sem2"


class mods_database:
    def __init__(self):
        self.conn = self._init_con()
        self.cursor = self.conn.cursor()
        self.sem1_data = None
        self.sem2_data = None
        self.all_module_data = None

    def _init_con(self):
        database_url = os.getenv("POSTGRES_URL_NON_POOLING")
        pprint(database_url)
        conn = psycopg2.connect(database_url)
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
        semester_no INT
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
        return True

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

    def authenticate_student(self, student_id, password):
        """Authenticate a student with their ID and password"""
        sql = """SELECT password FROM students WHERE student_id = %s"""
        self.cursor.execute(sql, (student_id,))
        result = self.cursor.fetchone()

        if not result:
            return False

        stored_hash = result[0]
        return self._verify_password(stored_hash, password)

    def join_session(self, student_id, password, session_id):
        if self._is_student_exists(student_id):
            if not self.authenticate_student(student_id, password):
                return False
        else:
            self.add_student(student_id, password)
        self.add_student_sessions(student_id, session_id, json.dumps({}))
        return True

    def _generate_random_id(self):
        min = 0
        max = 999
        choice = string.ascii_uppercase + string.ascii_lowercase
        digits = [str(random.randint(min, max)) for i in range(2)]
        digits = [(len(str(max)) - len(digit)) * "0" + digit for digit in digits]
        return "-".join(digits) + random.choice(choice)

    def is_session_exists(self, id):
        self.cursor.execute("SELECT 1 FROM sessions WHERE session_id = %s", (id,))
        return self.cursor.fetchone() is not None

    def _is_group_exists(self, id):
        self.cursor.execute("SELECT 1 FROM groups WHERE group_id = %s", (id,))
        return self.cursor.fetchone() is not None

    def _return_unique_session_id(self):
        while True:
            new_session_id = self._generate_random_id()
            if not self.is_session_exists(new_session_id):
                return new_session_id

    def _return_unique_group_id(self):
        while True:
            new_group_id = uuid.uuid4()
            if not self._is_group_exists(new_group_id):
                return new_group_id

    def generate_session_id(self):
        return self._return_unique_session_id()

    def generate_group_id(self):
        return self._return_unique_group_id()

    """
        to create new session:
        press new session button, generate_session_id
        return session_id to front end
        front end show session_id
        check student usrname and password
    """

    def add_new_session(self, new_session_id, semester_no):
        self.cursor.execute(
            "INSERT INTO sessions (session_id, semester_no) VALUES (%s, %s)",
            (new_session_id, semester_no),
        )

    def list_sessions(self):
        sql = """SELECT * FROM sessions"""
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(f"[List Sessions] {row}")

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

        # print(f"loading data for {mod} semester {semester}")
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

        # print(f"loaded data for {mod}")
        return return_dict

    def _load_modules_data(self):
        SEM_1 = 1
        SEM_2 = 2
        year, _ = self._get_year_and_sem()
        all_modules = self._get_all_modules_names(year)
        print(f"[TOTAL MODULES] len: {len(all_modules)}")
        module_dict = {}
        for module in all_modules[6400:]:  # has a limit, must do 800 at a time
            modulecode = module["moduleCode"]
            module_dict[modulecode] = {
                "title": module["title"],
                SEM1: self._load_mod_data(modulecode, year, SEM_1),
                SEM2: self._load_mod_data(modulecode, year, SEM_2),
            }
        return module_dict

    def _populate_modules_db(self):
        all_modules_dict = self._load_modules_data()
        for modulecode, module_info in all_modules_dict.items():
            title = module_info["title"]
            sem1 = module_info[SEM1]
            sem1_json = json.dumps(sem1) if sem1 else None
            sem2 = module_info[SEM2]
            sem2_json = json.dumps(sem2) if sem2 else None
            sql = """INSERT INTO MODULES (module_id, title, sem1_json, sem2_json) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (module_id) DO NOTHING
                """
            params = (
                modulecode,
                title,
                sem1_json,
                sem2_json,
            )
            self.cursor.execute(sql, params)

    def get_modules_db(self):
        sql = """SELECT * FROM modules"""
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        module_data = {}
        for row in rows:
            module_data[row[0]] = {"title": row[1], SEM1: row[2], SEM2: row[3]}
        # print(f"[MODULE_DATA] Length: {len(module_data)}")
        self.all_module_data = module_data

    def _get_sem_data(self, sem):
        if self.all_module_data is None:
            self.get_modules_db()
        return_data = {}
        for module_code, mod_info in self.all_module_data.items():
            sem_data = mod_info.get(sem)
            if not sem_data or sem_data == {}:
                continue  # Skip modules with no sem_data
            merged = {"title": mod_info.get("title")}
            if isinstance(sem_data, dict):
                merged.update(
                    sem_data.get(module_code, {})
                )  # flatten nested module_code dict
            return_data[module_code] = merged
        return return_data

    def get_sem1_data(self):
        if self.sem1_data == None:
            self.sem1_data = self._get_sem_data(SEM1)
        return self.sem1_data

    def get_sem2_data(self):
        if self.sem2_data == None:
            self.sem2_data = self._get_sem_data(SEM2)
        return self.sem2_data

    def add_group(self, module_id, session_id):
        new_group_id = self.generate_group_id()
        sql = """INSERT INTO groups (group_id, module_id, session_id)
                VALUES (%s, %s, %s)"""
        params = (new_group_id, module_id, session_id)
        self.cursor.execute(sql, params)
        return new_group_id

    def get_group_id(self, module_id, session_id):
        sql = """SELECT group_id FROM groups 
                WHERE module_id = %s AND session_id = %s"""
        self.cursor.execute(sql, (module_id, session_id))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_student_group(self, student_id, group_id):
        sql = """INSERT INTO student_groups (student_id, group_id)
                VALUES (%s, %s)
                ON CONFLICT (student_id, group_id) DO NOTHING"""
        self.cursor.execute(sql, (student_id, group_id))

    def get_student_group(self, student_id):
        sql = """SELECT group_id FROM student_groups WHERE student_id = %s"""
        self.cursor.execute(sql, (student_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_student_sessions(self, student_id, session_id, preference_json):
        sql = """INSERT INTO student_sessions (student_id, session_id, preference)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id, session_id) 
                DO UPDATE SET preference = EXCLUDED.preference"""
        self.cursor.execute(sql, (student_id, session_id, json.dumps(preference_json)))

    def get_preference_from_student_sessions(self, student_id, session_id):
        sql = """SELECT preference FROM student_sessions 
                WHERE student_id = %s AND session_id = %s"""
        self.cursor.execute(sql, (student_id, session_id))
        result = self.cursor.fetchone()
        return json.loads(result[0]) if result and result[0] else None

    def add_student_modules(self, student_id, session_id, module_id):
        sql = """INSERT INTO student_session_modules (student_id, session_id, module_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (student_id, session_id, module_id) DO NOTHING"""
        self.cursor.execute(sql, (student_id, session_id, module_id))

    def get_modules_from_student_session_modules(self, student_id, session_id):
        sql = """SELECT module_id FROM student_session_modules 
                WHERE student_id = %s AND session_id = %s"""
        self.cursor.execute(sql, (student_id, session_id))
        return [row[0] for row in self.cursor.fetchall()]

    def get_session_semester(self, session_id):
        sql = """SELECT semester_no FROM sessions
                WHERE session_id = %s"""
        self.cursor.execute(sql, (session_id,))
        result = self.cursor.fetchone()
        return result[0] if (result and result[0]) else None


def temp():
    sessionId = db.generate_session_id()
    db.add_new_session(sessionId, 1)


if __name__ == "__main__":
    db = mods_database()
    # module_data = db.get_modules_db()
    # print(db.generate_group_id())
    # sem2 = db.get_sem2_data()
    # pprint(sem2["CG2023"])
    db.list_sessions()
    sem1 = db.get_sem1_data()
    print(sem1.get("CG2028"))
    print(sem1.get("CG2023"))
    sem2 = db.get_sem2_data()
    print(sem2.get("CG2023"))
