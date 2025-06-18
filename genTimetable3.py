from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
from api import get_module_info
import json

# Configuration settings for the timetable solver
CONFIG = {
    "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
    "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)
    "lunch_window": (11 * 60, 13 * 60),  # Preferred lunch window (11AM-1PM)
    "lunch_duration": 60,  # Lunch break duration (60 minutes)
    "lunch_except_days": [],  # Days where lunch break isn't required
    "days_without_class": [],
    "optional_classes": {  # Classes that can be optionally included
        "EE2026": ["Lecture"],
        "EE2211": ["Lecture"],
        "IE2141": ["Lecture"],
        "CG2027": ["Lecture"],
        "CG2028": ["Lecture"],
    },
    "compulsory_classes": {
        "CG2023": {"Lecture": "01"},
        "CDE3301": {"Laboratory": "G10"},
    },
    "weights": {  # Weights for optimization criteria
        "morning_class": 1,  # Preference for morning classes
        "afternoon_class": 5,  # Preference for afternoon classes
        "day_length_penalty": -0.01,  # Penalty for long days
        "day_present_penalty": -10,  # Penalty for having classes on a day
    },
    "enable_lunch_break": False,  # Whether to enforce lunch breaks
    "enable_early_start": False,  # Whether to enforce earliest start time
    "enable_early_end": False,  # Whether to enforce latest end time
    "enable_compact": False,  # Whether to minimize day length
}


def print_and_write_to_file(
    solution_printer, isPrint, file_path="timetable_solution.txt"
):
    """
    Prints and writes solutions to a file.

    Args:
        solution_printer: The solution printer callback containing solutions
        isPrint: Whether to print solutions to console
        file_path: Path to write solutions to
    """
    if isPrint:
        print(f"Found {len(solution_printer.solutions)} solutions:")
        for solution in solution_printer.solutions:
            print(f"\nSolution {solution['solution_number']}:")
            print("NUSMods Link:", solution["nusmods_link"])
            print("Selected Classes:")
            for module, classes in solution["selected_classes"].items():
                print(f"  {module}: {', '.join(classes)}")
            print(solution["score"])
            # Uncomment to print detailed schedule
            # for day, sessions in solution['schedule'].items():
            #     print(f"  {day}:")
            #     for session in sessions:
            #         print(f"    {session['time']} {session['module']} {session['lesson_type']} {session['class_no']} at {session['venue']}")

    # Write solutions to file
    with open(file_path, "w") as f:
        toWrite = ""
        for index, solution in enumerate(solution_printer.solutions):
            toWrite += f"sol num: {index}: {solution['nusmods_link']}\n"
            if "score" in solution:  # Print score if available
                toWrite += f"Score: {solution['score']}\n"
        f.write(toWrite)


class TimetableSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """
    Custom solution printer that collects and formats timetable solutions.
    Also calculates objective scores for each solution.
    """

    def __init__(self, class_vars, class_groups, all_sessions, semester, limit, config):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._class_vars = class_vars
        self._class_groups = class_groups
        self._all_sessions = all_sessions
        self._semester = semester
        self._config = config
        self._solution_count = 0
        self._solution_limit = limit
        self.solutions = []
        # Mapping from lesson types to abbreviations
        self.lesson_dict = {
            "Laboratory": "LAB",
            "Lecture": "LEC",
            "Tutorial": "TUT",
            "Sectional Teaching": "SEC",
            "Packaged Lecture": "PLEC",
            "Packaged Tutorial": "PTUT",
        }

        # Precompute optional class keys for faster lookup
        self.optional_class_keys = set()
        for module, lesson_types in config["optional_classes"].items():
            for lesson_type in lesson_types:
                self.optional_class_keys.update(
                    key
                    for key in class_vars
                    if key[0] == module and key[1] == lesson_type
                )

    def calculate_solution_score(self, selected_classes, schedule):
        """
        Calculates the objective score for a solution.
        """
        score = 0
        day_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
        }

        # Track day information for calculating penalties
        day_info = {
            day: {"present": False, "start": 24 * 60, "end": 0}
            for day in day_map.keys()
        }

        # Process all sessions in the schedule
        for day, sessions in schedule.items():
            day_idx = day_map[day]

            for session in sessions:
                class_key = (
                    session["module"],
                    session["lesson_type"],
                    session["class_no"],
                )
                if class_key in self.optional_class_keys:
                    continue  # Skip optional classes for scoring

                # Parse time
                start_str, end_str = session["time"].split("-")
                start = int(start_str.split(":")[0]) * 60 + int(start_str.split(":")[1])
                end = int(end_str.split(":")[0]) * 60 + int(end_str.split(":")[1])

                # Add morning/afternoon weights
                if start >= 12 * 60:  # Afternoon
                    score += self._config["weights"]["afternoon_class"]
                else:
                    score += self._config["weights"]["morning_class"]

                # Track day bounds
                day_info[day]["start"] = min(day_info[day]["start"], start)
                day_info[day]["end"] = max(day_info[day]["end"], end)
                day_info[day]["present"] = True

        # Add day penalties
        for day, info in day_info.items():
            if info["present"]:
                # Day length penalty
                day_length = info["end"] - info["start"]
                score += self._config["weights"]["day_length_penalty"] * day_length

                # Day presence penalty
                score += self._config["weights"]["day_present_penalty"]

        return score

    def on_solution_callback(self):
        """Called whenever a new solution is found."""
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
                                "module": session["module"],
                                "lesson_type": session["lesson_type"],
                                "class_no": session["class_no"],
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

        # Calculate score for this solution
        score = self.calculate_solution_score(selection_dict, schedule)

        # Store solution
        self.solutions.append(
            {
                "solution_number": self._solution_count,
                "nusmods_link": url,
                "schedule": dict(schedule),
                "selected_classes": selection_dict,
                "score": score,  # Include the calculated score
            }
        )

        if self._solution_count >= self._solution_limit:
            self.StopSearch()


def main(link=None, modules=None, isLink=False, semester=2):
    """
    Main function to generate timetable solutions.

    Args:
        link: NUSMods shareable link
        modules: List of module codes
        isLink: Whether input is a link or module list
        semester: Semester number (1 or 2)
    """
    if modules is None:
        modules = ["CS2113", "CG2023", "EE2211", "CDE2501", "EE2026", "CS1010"]

    # Get timetable data
    ftt = filter_timetable(modules=modules, isLink=isLink, semester=semester)
    timetable_data = ftt["timetable"]
    semester = ftt["semester"]

    # Create CP model
    model = cp_model.CpModel()

    # Data structures
    class_groups = defaultdict(list)  # Maps class keys to session IDs
    class_vars = {}  # Decision variables for class selection
    session_to_class = {}  # Maps session IDs to class keys
    all_sessions = []  # List of all session data
    session_vars = {}  # Decision variables for session selection
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    time_intervals = defaultdict(list)  # Time intervals for no-overlap constraints

    # Create variables and constraints
    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info["timetable"].items():
            for class_no, sessions in classes.items():
                # Create class selection variable
                class_key = (module, lesson_type, class_no)
                class_vars[class_key] = model.NewBoolVar(
                    f"class_{module}_{lesson_type}_{class_no}"
                )

                for session in sessions:
                    if session["day"] not in day_map:
                        continue  # Skip sessions on unsupported days

                    # Convert time to minutes
                    start = int(session["startTime"][:2]) * 60 + int(
                        session["startTime"][2:]
                    )
                    end = int(session["endTime"][:2]) * 60 + int(session["endTime"][2:])

                    # Store session data
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

                    # Link session to class selection variable
                    session_vars[session_id] = model.NewBoolVar(f"s_{session_id}")
                    model.Add(session_vars[session_id] == class_vars[class_key])

                    # Group sessions by class
                    class_groups[class_key].append(session_id)
                    session_to_class[session_id] = class_key

                    # Create time intervals for no-overlap constraints
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
    # 1. Exactly one class must be selected for each lesson type of each module
    # (including optional classes, but they'll be excluded from scoring)
    for module in timetable_data:
        for lesson_type in timetable_data[module]["timetable"]:
            class_options = [
                class_vars[key]
                for key in class_vars
                if key[0] == module and key[1] == lesson_type
            ]
            if class_options:
                model.AddExactlyOne(class_options)

    # 2. No overlapping sessions
    for intervals in time_intervals.values():
        model.AddNoOverlap(intervals)

    # add compulsory classes
    for module, lesson_info in CONFIG["compulsory_classes"].items():
        for lesson_type, class_no in lesson_info.items():
            class_key = (module, lesson_type, class_no)
            if class_key in class_vars:
                model.Add(class_vars[class_key] == 1)
            else:
                print(
                    f"Warning: Compulsory class not found - {module} {lesson_type} {class_no}"
                )

    # Create set of optional class keys for quick lookup
    optional_class_keys = set()
    for module, lesson_types in CONFIG["optional_classes"].items():
        for lesson_type in lesson_types:
            optional_class_keys.update(
                key for key in class_vars if key[0] == module and key[1] == lesson_type
            )

    # add constraints for days without class
    for day in CONFIG["days_without_class"]:
        day_sessions = [
            sid
            for sid, session_info in enumerate(all_sessions)
            if session_info["day"] == day
        ]  # find all sessions that is on day
        for sid in day_sessions:
            model.Add(session_vars[sid] == 0)

    # Objective function terms
    objective_terms = []

    # 1. Day start/end times and penalties (excluding optional classes)
    for day in range(5):
        day_sessions = [
            sid
            for sid, s in enumerate(all_sessions)
            if s["day"] == day and session_to_class[sid] not in optional_class_keys
        ]

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

            # Add day length penalty to objective
            day_length = model.NewIntVar(0, 24 * 60, f"day_length_{day}")
            model.Add(day_length == day_end - day_start)
            objective_terms.append(CONFIG["weights"]["day_length_penalty"] * day_length)

            # Add day presence penalty
            day_present = model.NewBoolVar(f"day_present_{day}")
            model.AddMaxEquality(
                day_present, [session_vars[sid] for sid in day_sessions]
            )
            objective_terms.append(
                CONFIG["weights"]["day_present_penalty"] * day_present
            )

    # 2. Morning/afternoon class preferences (excluding optional classes)
    for session_id, session in enumerate(all_sessions):
        class_key = session_to_class[session_id]
        if class_key in optional_class_keys:
            continue  # Skip optional classes

        is_afternoon = session["start"] >= 11 * 60  # Afternoon if starts at/after 11AM
        weight = (
            CONFIG["weights"]["afternoon_class"]
            if is_afternoon
            else CONFIG["weights"]["morning_class"]
        )
        objective_terms.append(weight * session_vars[session_id])

    # 3. Lunch break constraints (if enabled)
    if CONFIG["enable_lunch_break"]:
        for day in range(5):  # Monday to Friday
            if day in CONFIG["lunch_except_days"]:
                continue  # Skip days where lunch isn't required

            # Get non-optional sessions for this day
            day_sessions = [
                s
                for s in all_sessions
                if s["day"] == day
                and session_to_class[s["id"]] not in optional_class_keys
            ]
            if not day_sessions:
                continue  # Skip days with no required classes

            # Create lunch time variables
            lunch_start = model.NewIntVar(
                CONFIG["lunch_window"][0],
                CONFIG["lunch_window"][1] - CONFIG["lunch_duration"],
                f"lunch_start_{day}",
            )
            lunch_end = lunch_start + CONFIG["lunch_duration"]

            # Create lunch interval
            lunch_interval = model.NewIntervalVar(
                lunch_start, CONFIG["lunch_duration"], lunch_end, f"lunch_break_{day}"
            )

            # Prevent overlap between lunch and classes
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

    # Set objective to maximize
    model.Maximize(sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    solution_limit = 10  # Number of solutions to find

    # Configure solver parameters
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.random_seed = 88  # For reproducibility
    num_runs = 3

    # # Create and use solution printer
    # solution_printer = TimetableSolutionPrinter(
    #     class_vars, class_groups, all_sessions, semester, solution_limit, CONFIG
    # )
    # solver.Solve(model, solution_printer)

    # # Output results
    # print_and_write_to_file(solution_printer, isPrint=True)

    all_solutions = []

    for run in range(num_runs):
        print(f"\nRunning optimization attempt {run+1}/{num_runs}")

        # Configure solver parameters with different random seeds
        solver.parameters.enumerate_all_solutions = True
        solver.parameters.random_seed = 88 + run  # Different seed each run

        # Create solution printer
        solution_printer = TimetableSolutionPrinter(
            class_vars, class_groups, all_sessions, semester, solution_limit, CONFIG
        )

        # Solve the model
        status = solver.Solve(model, solution_printer)

        if status == cp_model.OPTIMAL:
            print(f"Run {run+1} found {len(solution_printer.solutions)} solutions")
            all_solutions.extend(solution_printer.solutions)
        else:
            print(f"Run {run+1} did not find optimal solution")

    unique_solutions = []
    seen = set()
    for sol in all_solutions:
        # Create a unique identifier for the solution
        ident = tuple(sorted((k, tuple(v)) for k, v in sol["selected_classes"].items()))
        if ident not in seen:
            seen.add(ident)
            unique_solutions.append(sol)
    all_solutions = unique_solutions

    # Sort all solutions by score (highest first)
    all_solutions.sort(key=lambda x: x["score"], reverse=True)

    # Create a final solution printer with the sorted solutions
    final_printer = TimetableSolutionPrinter(
        class_vars, class_groups, all_sessions, semester, len(all_solutions), CONFIG
    )
    final_printer.solutions = all_solutions

    # Output results
    print_and_write_to_file(final_printer, isPrint=True)


if __name__ == "__main__":
    # Example usage
    modules = [
        # "CS2113",
        # "CG2023",
        # "EE2211",
        # "CDE2501",
        # "EE2026",
        # "CS1010",
        "CG2027",
        "CG2028",
        "LAM1201",
        "CG2023",
        "CDE2000",
        "IE2141",
        "CDE3301",
    ]
    result = main(modules=modules, semester=2)
