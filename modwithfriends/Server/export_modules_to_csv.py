import psycopg2
import csv
import os
from dotenv import load_dotenv

load_dotenv()


def export_modules_to_csv():

    conn = psycopg2.connect(
        database="postgres",
        host="127.0.0.1",
        user="wongwh",
        password="wongwh",
        port="5432",
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modules")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    with open("modules_export.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(colnames)
        writer.writerows(rows)
    print("Exported modules table to modules_export.csv")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    export_modules_to_csv()
