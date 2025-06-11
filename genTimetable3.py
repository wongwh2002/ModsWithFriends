from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
from api import get_module_info
import json

def main(link = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6",
        modules = ["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026"],
        isLink = False):
    # Your timetable data
    ftt = filter_timetable(isLink=False)
    timetable_data = ftt["timetable"]
    semester = ftt["semester"]
    model = cp_model.CpModel()
    
    # Data structures
    class_groups = defaultdict(list)
    class_vars = {}
    session_to_class = {}
    all_sessions = []
    session_vars = {}
    day_map = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4}
    time_intervals = defaultdict(list)

    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info['timetable'].items():
            for class_no, sessions in classes.items():
                # Create class variable
                class_key = (module, lesson_type, class_no)
                class_vars[class_key] = model.NewBoolVar(
                    f"class_{module}_{lesson_type}_{class_no}"
                )
                
                for session in sessions:
                    if session['day'] not in day_map:
                        continue

                    # Create session data
                    start = int(session['startTime'][:2])*60 + int(session['startTime'][2:])
                    end = int(session['endTime'][:2])*60 + int(session['endTime'][2:])
                    
                    session_data = {
                        'id': session_id,
                        'module': module,
                        'lesson_type': lesson_type,
                        'class_no': class_no,
                        'day': day_map[session['day']],
                        'day_name': session['day'],
                        'start': start,
                        'end': end,
                        'weeks': session['weeks'],
                        'venue': session['venue']
                    }
                    all_sessions.append(session_data)
                    
                    # Link session to class
                    session_vars[session_id] = model.NewBoolVar(f"s_{session_id}")
                    model.Add(session_vars[session_id] == class_vars[class_key])
                    
                    # Grouping
                    class_groups[class_key].append(session_id)
                    session_to_class[session_id] = class_key
                    
                    # Time intervals
                    for week in session['weeks']:
                        interval_var = model.NewOptionalIntervalVar(
                            start, end-start, end, session_vars[session_id],
                            f"i_{session_id}_w{week}"
                        )
                        time_intervals[(session_data['day'], week)].append(interval_var)
                    
                    session_id += 1

    # Constraints
    required_lessons = ['Laboratory', 'Lecture', 'Tutorial']
    for module in timetable_data:
        for lesson_type in required_lessons:
            if lesson_type in timetable_data[module]['timetable']:
                class_options = [
                    class_vars[key] for key in class_vars 
                    if key[0] == module and key[1] == lesson_type
                ]
                if class_options:
                    model.AddExactlyOne(class_options)

    for intervals in time_intervals.values():
        model.AddNoOverlap(intervals)

    # Solution printer callback
    class TimetableSolutionPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, class_vars, class_groups, all_sessions, semester, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._class_vars = class_vars
            self._class_groups = class_groups
            self._all_sessions = all_sessions
            self._semester = semester
            self._solution_count = 0
            self._solution_limit = limit
            self.solutions = []
            self.lesson_dict = {'Laboratory': "LAB", 'Lecture': "LEC", 'Tutorial': "TUT"}

        def on_solution_callback(self):
            self._solution_count += 1
            selection_dict = {}
            schedule = defaultdict(list)
            
            # Process selected classes
            for class_key, var in self._class_vars.items():
                if self.Value(var):
                    module, lesson_type, class_no = class_key
                    if module in selection_dict:
                        selection_dict[module].append(f"{self.lesson_dict[lesson_type]}:{class_no}")
                    else:
                        selection_dict[module] = [f"{self.lesson_dict[lesson_type]}:{class_no}"]
                    
                    # Add to schedule
                    for sid in self._class_groups[class_key]:
                        if self.Value(self._all_sessions[sid]['id']):
                            session = self._all_sessions[sid]
                            schedule[session['day_name']].append({
                                'module': module,
                                'lesson_type': lesson_type,
                                'class_no': class_no,
                                'time': f"{session['start']//60:02d}:{session['start']%60:02d}-{session['end']//60:02d}:{session['end']%60:02d}",
                                'venue': session['venue'],
                                'weeks': session['weeks']
                            })
            
            # Generate NUSMods URL
            url = f"https://nusmods.com/timetable/sem-{self._semester}/share?"
            for key, value in selection_dict.items():
                url += f"{key}={','.join(value)}&"
            url = url[:-1]  # Remove trailing &
            
            self.solutions.append({
                'solution_number': self._solution_count,
                'nusmods_link': url,
                'schedule': dict(schedule),
                'selected_classes': selection_dict
            })
            
            if self._solution_count >= self._solution_limit:
                with open("timetable_solution.txt", "w") as f:
                    toWrite = ""
                    
                    for index, solution in enumerate(self.solutions):
                        toWrite += f"sol num: {index}: {solution["nusmods_link"]}\n"
                    
                    f.write(toWrite)

                self.StopSearch()

    

    # Solve with callback
    solver = cp_model.CpSolver()
    solution_limit = 10  # Number of solutions to find
    # solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    solution_printer = TimetableSolutionPrinter(
        class_vars, class_groups, all_sessions, semester, solution_limit
    )
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.random_seed = 88
    solver.Solve(model, solution_printer)

    isPrint = False
    # Output results
    if isPrint:
        print(f"Found {len(solution_printer.solutions)} solutions:")
        for solution in solution_printer.solutions:
            print(f"\nSolution {solution['solution_number']}:")
            print("NUSMods Link:", solution['nusmods_link'])
            print("Selected Classes:")
            for module, classes in solution['selected_classes'].items():
                print(f"  {module}: {', '.join(classes)}")
            print("\nSchedule:")
            for day, sessions in solution['schedule'].items():
                print(f"  {day}:")
                for session in sessions:
                    print(f"    {session['time']} {session['module']} {session['lesson_type']} {session['class_no']} at {session['venue']}")

    # with open("timetable_solution.txt", "w") as f:
    #     toWrite = ""
        
    #     for index, solution in enumerate(solution_printer.solutions):
    #         toWrite += f"sol num: {index}: {solution["nusmods_link"]}\n"
        
    #     f.write(toWrite)

if __name__ == "__main__":
    link = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6"
    modules = ["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026"]
    isLink = False
    result = main(modules = modules, isLink = isLink)
    pprint(result)
    print("Solutions saved to timetable_solution.json")