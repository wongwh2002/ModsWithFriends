from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
from api import get_module_info

def time_to_minutes(time_str):
    """Convert time string (e.g., '0900') to minutes since midnight"""
    return int(time_str[:2]) * 60 + int(time_str[2:])

def minutes_to_time(minutes):
    """Convert minutes since midnight to time string (e.g., '09:00')"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def main():
    # Your timetable data
    timetable_data = filter_timetable(link = False)

    # pprint(timetable_data)

    # Initialize model
    model = cp_model.CpModel()

    # Data structures
    all_sessions = []
    session_vars = {}
    module_lesson_map = defaultdict(list)
    day_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}
    time_intervals = defaultdict(list)  # For no-overlap constraints

    # 1. Process all sessions and create variables
    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info['timetable'].items():
            for class_no, sessions in classes.items():
                for session in sessions:
                    if session['day'] not in day_map:
                        continue  # Skip weekends

                    # Create session data
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

                    # Create decision variable
                    session_vars[session_id] = model.NewBoolVar(
                        f"s_{module}_{lesson_type}_{class_no}_{session['day']}"
                    )

                    # Map to module and lesson type
                    module_lesson_map[(module, lesson_type)].append(session_id)
                    
                    # Create interval variable for each week
                    for week in session['weeks']:
                        interval_var = model.NewOptionalIntervalVar(
                            start,
                            end - start,
                            end,
                            session_vars[session_id],
                            f"i_{session_id}_d{session_data['day']}_w{week}"
                        )
                        time_intervals[(session_data['day'], week)].append(interval_var)

                    session_id += 1
    pprint(timetable_data["CG2023"])
    # pprint(all_sessions)
    # pprint(all_sessions)

    # 2. Add constraints
    # 2.1 Must select exactly one of each required lesson type per module
    required_lessons = ['Laboratory', 'Lecture', 'Tutorial']
    for module in timetable_data:
        for lesson_type in required_lessons:
            if lesson_type in timetable_data[module]['timetable']:
                session_ids = module_lesson_map.get((module, lesson_type), [])
                if session_ids:
                    model.AddExactlyOne(session_vars[sid] for sid in session_ids)

    # 2.2 No overlapping sessions
    for (day, week), intervals in time_intervals.items():
        model.AddNoOverlap(intervals)

    # 3. Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)
    # solver.parameters.enumerate_all_solutions = True

    # 4. Print solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Optimal schedule found:\n")
        
        # Group selected sessions by day
        day_schedule = defaultdict(list)
        for session in all_sessions:
            if solver.Value(session_vars[session['id']]):
                day_name = next(k for k,v in day_map.items() if v == session['day'])
                day_schedule[day_name].append(session)
        
        # Print schedule by day
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            if day in day_schedule:
                print(f"{day}:")
                for session in sorted(day_schedule[day], key=lambda x: x['start']):
                    start = f"{session['start']//60:02d}:{session['start']%60:02d}"
                    end = f"{session['end']//60:02d}:{session['end']%60:02d}"
                    print(f"  {start}-{end}: {session['module']} {session['lesson_type']} "
                          f"{session['class_no']} at {session['venue']} (weeks: {session['weeks']})")
                print()
    else:
        print("No solution found")

    print("\nSolver statistics:")
    print(f"  - Conflicts: {solver.NumConflicts()}")
    print(f"  - Branches : {solver.NumBranches()}")
    print(f"  - Wall time: {solver.WallTime()} s")

if __name__ == "__main__":
    main()