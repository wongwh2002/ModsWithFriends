from urllib.parse import parse_qs, urlparse
from pprint import pprint

def deserialise_timetable(url):
    # https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&IE2141=TUT:14,LEC:2
    parsed = urlparse(url)
    semester = parsed.path.split("/")[2].split("-")[1]
    query = parse_qs(parsed.query)

    timetable_data = {}
    for module, class_info in query.items():
        lessons = {}
        for part in class_info[0].split(","):
            lesson_type, class_no = part.split(":")
            lessons[lesson_type] = class_no
        timetable_data[module] = lessons
    return semester, timetable_data

if __name__=="__main__":
    tmp = deserialise_timetable("https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6")
    pprint(tmp)