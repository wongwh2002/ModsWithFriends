from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
from api import get_module_info

def main(link = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6",
        modules = ["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026"],
        isLink = False):
    # Your timetable data
    ftt = filter_timetable(isLink = False)
    timetable_data = ftt["timetable"]
    semester = ftt["semester"]
    model = cp_model.CpModel()
    
    # New data structures
    class_groups = defaultdict(list)  # Maps (module,lesson_type,class_no) to session IDs
    class_vars = {}                   # Decision variables for each logical class
    session_to_class = {}             # Maps session ID to its class variable
    
    # (Keep existing data structures)
    all_sessions = []
    session_vars = {}
    day_map = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4}
    time_intervals = defaultdict(list)

    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info['timetable'].items():
            for class_no, sessions in classes.items():
                # Create a decision variable for the entire class
                class_key = (module, lesson_type, class_no)
                class_vars[class_key] = model.NewBoolVar(
                    f"class_{module}_{lesson_type}_{class_no}"
                )
                
                for session in sessions:
                    if session['day'] not in day_map:
                        continue

                    # Create session data (same as before)
                    start = int(session['startTime'][:2])*60 + int(session['startTime'][2:])
                    end = int(session['endTime'][:2])*60 + int(session['endTime'][2:])
                    
                    session_data = {
                        'id': session_id,
                        'module': module,
                        'lesson_type': lesson_type,
                        'class_no': class_no,
                        'day': day_map[session['day']],
                        'start': start,
                        'end': end,
                        'weeks': session['weeks'],
                        'venue': session['venue']
                    }
                    all_sessions.append(session_data)
                    
                    # Session variable must match class selection
                    session_vars[session_id] = model.NewBoolVar(
                        f"s_{session_id}"
                    )
                    model.Add(session_vars[session_id] == class_vars[class_key])
                    
                    # Grouping
                    class_groups[class_key].append(session_id)
                    session_to_class[session_id] = class_key
                    
                    # Time intervals (same as before)
                    for week in session['weeks']:
                        interval_var = model.NewOptionalIntervalVar(
                            start, end-start, end, session_vars[session_id],
                            f"i_{session_id}_w{week}"
                        )
                        time_intervals[(session_data['day'], week)].append(interval_var)
                    
                    session_id += 1

    # Constraints
    # 1. Select exactly one class per lesson type
    required_lessons = ['Laboratory', 'Lecture', 'Tutorial']
    for module in timetable_data:
        for lesson_type in required_lessons:
            if lesson_type in timetable_data[module]['timetable']:
                # Get all class options for this module+lesson_type
                class_options = [
                    class_vars[key] for key in class_vars 
                    if key[0] == module and key[1] == lesson_type
                ]
                if class_options:
                    model.AddExactlyOne(class_options)

    # 2. No overlapping sessions (same as before)
    for intervals in time_intervals.values():
        model.AddNoOverlap(intervals)

    # Solve and output (same as before)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    lesson_dict = {'Laboratory': "LAB", 
                   'Lecture': "LEC", 
                   'Tutorial': "TUT"}
    selection_dict = {}
    if status == cp_model.OPTIMAL:
        print("Optimal schedule:")
        for class_key, var in class_vars.items():
            if solver.Value(var):
                module, lesson_type, class_no = class_key
                if module in selection_dict:
                    selection_dict[module].append(f"{lesson_dict[lesson_type]}:{class_no}")
                else:
                    selection_dict[module] = [f"{lesson_dict[lesson_type]}:{class_no}"]
                print(f"\n{module} {lesson_type} {class_no}:")
                # for sid in class_groups[class_key]:
                #     session = all_sessions[sid]
                #     if solver.Value(session_vars[sid]):
                #         print(f"  {session['day']}: {session['start']//60:02d}:{session['start']%60:02d}-"
                #               f"{session['end']//60:02d}:{session['end']%60:02d} at {session['venue']}")
    
    url = f"https://nusmods.com/timetable/sem-{semester}/share?"
    for key, value in selection_dict.items():
        url += f"{key}={",".join(value)}&"
    pprint(url[:-1])
                    

if __name__ == "__main__":
    link = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6"
    modules = ["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026"]
    isLink = False
    result = main(modules = modules, isLink = isLink)
    pprint(result)
    print("Solutions saved to timetable_solutions.json")