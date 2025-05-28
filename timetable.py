from deserialiseUrk import deserialise_timetable
from api import get_module_info
from pprint import pprint

def group_timetable_by_lesson_type(timetable_data):
    grouped = {}

    for session in timetable_data:
        lesson_type = session['lessonType']
        class_no = session['classNo']

        if lesson_type not in grouped:
            grouped[lesson_type] = {}

        if class_no not in grouped[lesson_type]:
            grouped[lesson_type][class_no] = []

        grouped_session = {
            'day': session['day'],
            'startTime': session['startTime'],
            'endTime': session['endTime'],
            'venue': session['venue'],
            'weeks': session['weeks'],
        }
        grouped[lesson_type][class_no].append(grouped_session)
    return grouped

def get_filtered_timetable(module_code, semester, YEAR):
    module_info = get_module_info(YEAR, module_code.upper())
    if not module_info:
        return None
    
    semester_info = [s for s in module_info["semesterData"] if s["semester"] == semester]
    if not semester_info:
        return None
    
    target_semester_info = semester_info[0]
    processed_timetable = group_timetable_by_lesson_type(target_semester_info["timetable"])    
    
    result = {
        "timetable": processed_timetable
    }

    if "examDate" in target_semester_info:
        result.update({
            "examDate": target_semester_info["examDate"],
            "examDuration": target_semester_info["examDuration"]
        })
    return result
        
    # all_timetables[module] = {"timetable": target_semester_info["timetable"]}
    # if "examDate" in target_semester_info.keys():
    #     all_timetables[module] += {"examDate": target_semester_info["examDate"],
    #                             "examDuration": target_semester_info["examDuration"]}

def filter_timetable(LINK = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6", 
         YEAR = 2024):
    semester, timetable = deserialise_timetable(LINK)
    semester = int(semester)
    all_timetables = {}
    for module_code, selected_classes in timetable.items():
        module_data = get_filtered_timetable(module_code, semester, YEAR)
        if module_data:
            all_timetables[module_code] = module_data
    return(all_timetables)
if __name__ == "__main__":
    pprint(filter_timetable())

