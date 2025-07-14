import psycopg2


def create_db(cursor):
    sql = """CREATE database mydb"""
    # Creating a database
    cursor.execute(sql)
    print("Database created successfully........")


def create_student_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS STUDENT")
    sql = """CREATE TABLE STUDENT(
        Student_ID VARCHAR PRIMARY KEY,
        Password VARCHAR
    )"""
    cursor.execute(sql)


def create_modules_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS MODULE")
    sql = """CREATE TABLE MODULE(
    Module_ID VARCHAR PRIMARY KEY,
    Module_Name VARCHAR NOT NULL
    )"""
    cursor.execute(sql)


def create_session_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS SESSIONS")
    sql = """CREATE TABLE SESSIONS(
    Session_ID VARCHAR PRIMARY KEY,
    )"""
    cursor.execute(sql)


def create_group_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS GROUPS")
    sql = """CREATE TABLE GROUPS(
    Group_ID VARCHAR PRIMARY KEY,
    Module_ID VARCHAR NOT NULL REFERENCES MODULES(Module_ID),
    SESSION_ID VARCHAR NOT NULL REFERENCES SESSION(Session_ID)
    )"""
    cursor.execute(sql)


def create_student_group_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS STUDENT_GROUP")
    sql = """CREATE TABLE STUDENT_GROUP(
    Student_ID VARCHAR REFERENCES STUDENT(Student_ID),
    Group_ID VARCHAR REFERENCES GROUPS(Group_ID),
    PRIMARY KEY (Student_ID, Group_ID)
    )"""
    cursor.execute(sql)


def create_student_session_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS STUDENT_SESSION")
    sql = """CREATE TABLE STUDENT_SESSION(
    Student_ID VARCHAR REFERENCES STUDENT(Student_ID),
    Session_ID VARCHAR REFERENCES SESSIONS(Session_ID),
    Preference JSONB
    PRIMARY KEY (Student_ID, Session_ID)
    )"""
    cursor.execute(sql)


def create_student_module_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS STUDENT_MODULE")
    sql = """CREATE TABLE STUDENT_MODULE(
    Student_ID VARCHAR REFERENCES STUDENT(Student_ID),
    Session_ID VARCHAR REFERENCES SESSIONs(Session_ID),
    Module_ID VARCHAR REFERENCES MODULE(Module_ID)
    PRIMARY KEY (Student_ID, Session_ID)
    )"""
    cursor.execute(sql)


conn = psycopg2.connect(
    database="postgres",
    host="127.0.0.1",
    user="wongwh",
    password="wongwh",
    port="5432",
)
conn.autocommit = True

cursor = conn.cursor()


# Closing the connection
conn.close()
