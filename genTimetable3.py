from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
from api import get_module_info
import json

CONFIG = {
    "earliest_start": 10 * 60,  # 24hr clock
    "latest_end": 18 * 60,
    "want_lunch_break": False,
    "lunch_window": (11 * 60, 12 * 60),  # start, end
    "lunch_duration": 60,
    "lunch_except_days": [4],
    "optional_classes": {"CS1010": ["Lecture"], "CG2023": ["Tutorial"]},
    "weights": {
        "morning_class": 1,
        "afternoon_class": 2,
        "day_length_penalty": -0.1,
        "day_present_penalty": -10,
    },
    "enable_early_start": False,  # Toggle for 9am constraint
    "enable_early_end": False,  # Toggle for 6pm constraint
    "enable_compact": False,  # Toggle for compact schedule
}


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
        self.lesson_dict = {
            "Laboratory": "LAB",
            "Lecture": "LEC",
            "Tutorial": "TUT",
            "Sectional Teaching": "SEC",
            "Packaged Lecture": "PLEC",
            "Packaged Tutorial": "PTUT",
        }

    def on_solution_callback(self):
        self._solution_count += 1
        selection_dict = {}
        schedule = defaultdict(list)

        # Process selected classes
        for class_key, var in self._class_vars.items():
            if self.Value(var):
                module, lesson_type, class_no = class_key
                if module in selection_dict:
                    selection_dict[module].append(
                        f"{self.lesson_dict[lesson_type]}:{class_no}"
                    )
                else:
                    selection_dict[module] = [
                        f"{self.lesson_dict[lesson_type]}:{class_no}"
                    ]

                # Add to schedule
                for sid in self._class_groups[class_key]:
                    if self.Value(self._all_sessions[sid]["id"]):
                        session = self._all_sessions[sid]
                        schedule[session["day_name"]].append(
                            {
                                "module": module,
                                "lesson_type": lesson_type,
                                "class_no": class_no,
                                "time": f"{session['start']//60:02d}:{session['start']%60:02d}-{session['end']//60:02d}:{session['end']%60:02d}",
                                "venue": session["venue"],
                                "weeks": session["weeks"],
                            }
                        )

        # Generate NUSMods URL
        url = f"https://nusmods.com/timetable/sem-{self._semester}/share?"
        for key, value in selection_dict.items():
            url += f"{key}={','.join(value)}&"
        url = url[:-1]  # Remove trailing &

        self.solutions.append(
            {
                "solution_number": self._solution_count,
                "nusmods_link": url,
                "schedule": dict(schedule),
                "selected_classes": selection_dict,
            }
        )

        if self._solution_count >= self._solution_limit:
            pprint(list(solution["nusmods_link"] for solution in (self.solutions)))
            self.StopSearch()


def print_and_write_to_file(
    solution_printer, isPrint, file_path="timetable_solution.txt"
):
    if isPrint:
        print(f"Found {len(solution_printer.solutions)} solutions:")
        for solution in solution_printer.solutions:
            print(f"\nSolution {solution['solution_number']}:")
            print("NUSMods Link:", solution["nusmods_link"])
            print("Selected Classes:")
            for module, classes in solution["selected_classes"].items():
                print(f"  {module}: {', '.join(classes)}")
            print("\nSchedule:")
            # for day, sessions in solution['schedule'].items():
            #     print(f"  {day}:")
            #     for session in sessions:
            #         print(f"    {session['time']} {session['module']} {session['lesson_type']} {session['class_no']} at {session['venue']}")

    with open(file_path, "w") as f:
        toWrite = ""

        for index, solution in enumerate(solution_printer.solutions):
            toWrite += f"sol num: {index}: {solution["nusmods_link"]}\n"

        f.write(toWrite)


def gen_sol_no_minimise(
    semester,
    model,
    class_groups,
    class_vars,
    all_sessions,
    TimetableSolutionPrinter,
    solver,
    solution_limit,
):
    solution_printer = TimetableSolutionPrinter(
        class_vars, class_groups, all_sessions, semester, solution_limit
    )
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.random_seed = 88
    solver.Solve(model, solution_printer)
    return solution_printer


def solve_with_ranking(
    semester,
    model,
    class_groups,
    class_vars,
    all_sessions,
    TimetableSolutionPrinter,
    solver,
    objective_var,
    solution_limit=10,
    tolerance=30,
):
    # First solve to find optimal value
    solver.parameters.enumerate_all_solutions = False
    status = solver.Solve(model)

    if status != cp_model.OPTIMAL:
        return []

    optimal_value = solver.Value(objective_var)
    print(f"Optimal value found: {optimal_value}")

    # Add constaint that solutions must be within tolerance of optimal
    model.Add(objective_var <= optimal_value + tolerance)

    # find multiple solutions
    solution_printer = TimetableSolutionPrinter(
        class_vars, class_groups, all_sessions, semester, solution_limit
    )
    solver.parameters.enumerate_all_solutions = True
    solver.Solve(model, solution_printer)

    return solution_printer


def main(
    link="https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6",
    modules=["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026"],
    isLink=False,
    semester=2,
):

    # Your timetable data
    ftt = filter_timetable(modules=modules, isLink=isLink, semester=semester)
    timetable_data = ftt["timetable"]
    semester = ftt["semester"]
    model = cp_model.CpModel()

    # Data structures
    class_groups = defaultdict(list)
    class_vars = {}
    session_to_class = {}
    all_sessions = []
    session_vars = {}
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    time_intervals = defaultdict(list)

    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info["timetable"].items():
            for class_no, sessions in classes.items():
                # Create class variable
                class_key = (module, lesson_type, class_no)
                class_vars[class_key] = model.NewBoolVar(
                    f"class_{module}_{lesson_type}_{class_no}"
                )

                for session in sessions:
                    if session["day"] not in day_map:
                        continue

                    # Create session data
                    start = int(session["startTime"][:2]) * 60 + int(
                        session["startTime"][2:]
                    )
                    end = int(session["endTime"][:2]) * 60 + int(session["endTime"][2:])

                    session_data = {
                        "id": session_id,
                        "module": module,
                        "lesson_type": lesson_type,
                        "class_no": class_no,
                        "day": day_map[session["day"]],
                        "day_name": session["day"],
                        "start": start,
                        "end": end,
                        "weeks": session["weeks"],
                        "venue": session["venue"],
                    }
                    all_sessions.append(session_data)

                    # Link session to class
                    session_vars[session_id] = model.NewBoolVar(f"s_{session_id}")
                    model.Add(session_vars[session_id] == class_vars[class_key])

                    # Grouping
                    class_groups[class_key].append(session_id)
                    session_to_class[session_id] = class_key

                    # Time intervals
                    for week in session["weeks"]:
                        interval_var = model.NewOptionalIntervalVar(
                            start,
                            end - start,
                            end,
                            session_vars[session_id],
                            f"i_{session_id}_w{week}",
                        )
                        time_intervals[(session_data["day"], week)].append(interval_var)

                    session_id += 1

    # Constraints
    # Add only exactly 1 and no overlap
    required_lessons = [
        "Laboratory",
        "Lecture",
        "Tutorial",
        "Sectional Teaching",
        "Packaged Lecture",
        "Packaged Tutorial",
    ]

    for module in timetable_data:
        for lesson_type in required_lessons:
            if lesson_type in timetable_data[module]["timetable"]:
                class_options = [
                    class_vars[key]
                    for key in class_vars
                    if key[0] == module and key[1] == lesson_type
                ]
                if class_options:
                    model.AddExactlyOne(class_options)

    for intervals in time_intervals.values():
        model.AddNoOverlap(intervals)

    # Add earliest start and end time
    for day in range(5):
        day_sessions = [sid for sid, s in enumerate(all_sessions) if s["day"] == day]

        if day_sessions:
            # Create day start/end variables
            min_start = (
                0 if not CONFIG["enable_early_start"] else CONFIG["earliest_start"]
            )
            max_end = (
                24 * 60 if not CONFIG["enable_early_end"] else CONFIG["latest_end"]
            )
            day_start = model.NewIntVar(min_start, max_end, f"day_start_{day}")
            day_end = model.NewIntVar(min_start, max_end, f"day_end_{day}")

            # Link to actual sessions
            for sid in day_sessions:
                session = all_sessions[sid]
                model.Add(day_start <= session["start"]).OnlyEnforceIf(
                    session_vars[sid]
                )
                model.Add(day_end >= session["end"]).OnlyEnforceIf(session_vars[sid])

            # Add to objective to prefer compact schedules
            if CONFIG["enable_compact"]:
                model.Minimize(day_end - day_start)

    if CONFIG["want_lunch_break"]:
        for day in range(5):  # Monday to Friday
            if (
                day in CONFIG["lunch_except_days"]
            ):  # Except certain days, dont need care about lunch
                continue
            # Get all sessions for this day
            day_sessions = [s for s in all_sessions if s["day"] == day]
            if not day_sessions:
                continue  # Skip days with no classes

            # Create lunch time variables for this specific day
            lunch_start = model.NewIntVar(
                CONFIG["lunch_window"][0],
                CONFIG["lunch_window"][1] - CONFIG["lunch_duration"],
                f"lunch_start_{day}",
            )
            lunch_end = lunch_start + CONFIG["lunch_duration"]

            # Create a lunch interval
            lunch_interval = model.NewIntervalVar(
                lunch_start, CONFIG["lunch_duration"], lunch_end, f"lunch_break_{day}"
            )

            # For each session on this day, prevent overlap with lunch
            for s in day_sessions:
                sid = s["id"]
                session_interval = model.NewOptionalIntervalVar(
                    s["start"],
                    s["end"] - s["start"],
                    s["end"],
                    session_vars[sid],
                    f"session_{sid}_interval",
                )
                model.AddNoOverlap([lunch_interval, session_interval])

    # Solve with callback
    solver = cp_model.CpSolver()
    solution_limit = 10  # Number of solutions to find
    # solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    # solver.parameters.enumerate_all_solutions = True
    solution_printer = gen_sol_no_minimise(
        semester,
        model,
        class_groups,
        class_vars,
        all_sessions,
        TimetableSolutionPrinter,
        solver,
        solution_limit,
    )

    isPrint = True
    # Output results
    print_and_write_to_file(solution_printer, isPrint)


if __name__ == "__main__":
    link = "https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A26&CG2023=LAB:03,LEC:02&CG2028=TUT:03,LAB:02,LEC:01&IE2141=TUT:14,LEC:2&LAM1201=LEC:6"
    modules = [
        "CS2113",
        "CG2023",
        "EE2211",
        "CDE2501",
        "EE2026",
        # "CS1010",
    ]
    semester = 2
    isLink = False
    result = main(modules=modules, isLink=isLink, semester=semester)
