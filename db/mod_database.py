import psycopg2
import hashlib
import secrets
import uuid


def create_db(cursor):
    sql = """CREATE database mydb"""
    # Creating a database
    cursor.execute(sql)
    print("Database created successfully........")


def create_student_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS students")
    sql = """CREATE TABLE students(
        student_id VARCHAR PRIMARY KEY,
        password VARCHAR
    )"""
    cursor.execute(sql)


def create_modules_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS modules")
    sql = """CREATE TABLE modules(
    module_id VARCHAR PRIMARY KEY,
    module_name VARCHAR NOT NULL
    )"""
    cursor.execute(sql)


def create_session_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS sessions")
    sql = """CREATE TABLE sessions(
    sessions_id VARCHAR PRIMARY KEY
    )"""
    cursor.execute(sql)


def create_group_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS groups")
    sql = """CREATE TABLE groups(
    group_id VARCHAR PRIMARY KEY,
    module_id VARCHAR NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    sessions_id VARCHAR NOT NULL REFERENCES sessions(sessions_id) ON DELETE CASCADE
    )"""
    cursor.execute(sql)


def create_student_group_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS student_groups")
    sql = """CREATE TABLE student_groups(
    student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
    group_id VARCHAR REFERENCES groups(group_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, group_id)
    )"""
    cursor.execute(sql)


def create_student_session_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS student_sessions")
    sql = """CREATE TABLE student_sessions(
    student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
    sessions_id VARCHAR REFERENCES sessions(sessions_id) ON DELETE CASCADE,
    preference JSONB,
    PRIMARY KEY (student_id, sessions_id)
    )"""
    cursor.execute(sql)


def create_student_session_module_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS student_session_modules")
    sql = """CREATE TABLE student_session_modules(
    student_id VARCHAR REFERENCES students(student_id) ON DELETE CASCADE,
    sessions_id VARCHAR REFERENCES sessions(sessions_id) ON DELETE CASCADE,
    module_id VARCHAR REFERENCES modules(module_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, sessions_id, module_id)
    )"""
    cursor.execute(sql)


def initialise_db(cursor):
    create_db(cursor)
    create_student_table(cursor)
    create_modules_table(cursor)
    create_session_table(cursor)
    create_group_table(cursor)
    create_student_group_table(cursor)
    create_student_session_table(cursor)
    create_student_session_module_table(cursor)


def add_student(student_id, password, cursor):
    if is_student_exists(student_id, cursor):
        print("[Add Student] student already exists")
        return False
    hashed_password = hash_password(password)
    sql = """INSERT INTO students (student_id, password)
            VALUES (%s, %s)
            """
    params = (student_id, hashed_password)
    cursor.execute(sql, params)


def list_students(cursor):
    sql = """SELECT * FROM students"""
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        print(f"[List Students] {row}")


def hash_password(password):
    salt = secrets.token_hex(16)  # 32char salt
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}:{hashed.hex()}"


def verify_password(stored_hash, input_password):
    salt, original_hash = stored_hash.split(":")
    new_hash = hashlib.pbkdf2_hmac(
        "sha256", input_password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return secrets.compare_digest(new_hash, original_hash)


def is_student_exists(student_id, cursor) -> bool:
    cursor.execute("SELECT 1 FROM students WHERE student_id = %s", (student_id,))
    return cursor.fetchone() is not None


def generate_unique_id():
    return str(uuid.uuid4())


def new_session(student_id, password, cursor):  # returns session_id
    session_id = generate_unique_id()
    sql = """INSERT INTO sessions (session_id)
            VALUES(%s)"""
    params = session_id
    cursor.execute(sql, params)


def change_password(student_id, curr_password, new_password, cursor):
    pass


def add_student_to_session():
    pass


def add_module(module_id, module_name):  # add all 1000 mods
    pass


def add_group(session_id, module_id):
    pass


conn = psycopg2.connect(
    database="postgres",
    host="127.0.0.1",
    user="wongwh",
    password="wongwh",
    port="5432",
)
conn.autocommit = True

cursor = conn.cursor()

# add_student("wongwh", "blegh", cursor)
# add_student("weng", "blegh", cursor)
# list_students(cursor)
for i in range(10):
    id = (generate_unique_id()).split("-")[4]
    print(id)

# Closing the connection
conn.close()
