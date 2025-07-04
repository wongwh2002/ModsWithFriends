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
    "lunch_window": (11 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
    "lunch_duration": 60,  # Lunch break duration (60 minutes)
    "days_without_lunch": [],  # Days where lunch break isn't required
    "days_without_class": [],
    "optional_classes": {  # Classes that can be optionally included
        # "EE2026": ["Lecture"],
        # "EE2211": ["Lecture"],
        # "IE2141": ["Lecture"],
        # "CG2027": ["Lecture"],
        # "CG2028": ["Lecture"],
        # "GESS1002": ["Lecture"],
        # "CS3281": ["Lecture"],
    },
    "compulsory_classes": {
        # "CG2023": {"Lecture": "01"},
        # "CDE3301": {"Laboratory": "G10"},
    },
    "teaching_assistant": {"CG2111A": {"Laboratory": "L03"}},
    "weights": {  # Weights for optimization criteria
        "morning_class": 100,  # Preference for morning classes
        "afternoon_class": 500,  # Preference for afternoon classes
        "day_length_penalty": -1,  # Penalty for long days
        "day_present_penalty": -1000,  # Penalty for having classes on a day
    },
    "enable_lunch_break": False,  # Whether to enforce lunch breaks
    "enable_late_start": False,  # Whether to enforce earliest start time
    "enable_early_end": False,  # Whether to enforce latest end time
    "enable_weights": True,  # Whether to minimize day length
}


def print_and_write_to_file(
    solution_printer, best_solution, isPrint, file_path="timetable_solution.txt"
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
        for solution in best_solution.solutions:
            print(f"\nSolution {solution['solution_number']}:")
            print("NUSMods Link:", solution["nusmods_link"])
            print("Selected Classes:")
            for module, classes in solution["selected_classes"].items():
                print(f"  {module}: {', '.join(classes)}")
            print(solution["score"])
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

        # Combine and sort all solutions by score (descending)
        all_solutions = best_solution.solutions + solution_printer.solutions
        sorted_solutions = sorted(
            all_solutions, key=lambda s: s.get("score", float("-inf")), reverse=True
        )

        for index, solution in enumerate(sorted_solutions):
            toWrite += f"sol num: {index}: {solution['nusmods_link']}\n"
            if "score" in solution:
                toWrite += f"Score: {solution['score']}\n"

        f.write(toWrite)


class TimetableSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """
    Custom solution printer that collects and formats timetable solutions.
    Also calculates objective scores for each solution.
    """

    def __init__(
        self, class_vars, class_groups, all_sessions, semester, limit, config, model
    ):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._class_vars = class_vars
        self._class_groups = class_groups
        self._all_sessions = all_sessions
        self._semester = semester
        self._config = config
        self._solution_count = 0
        self._solution_limit = limit
        self.solutions = []
        self.seen_solutions = set()
        self.model = model

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

        # Generate a tuple to uniquely identify the solution
        solution_signature = tuple(
            sorted((k, tuple(sorted(v))) for k, v in selection_dict.items())
        )

        # Skip if already seen
        if solution_signature in self.seen_solutions:
            return
        self.seen_solutions.add(solution_signature)
        # pprint(self.seen_solutions)
        self._solution_count += 1
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
                "score": round(score, 2),  # Include the calculated score
            }
        )

        if self._solution_count >= self._solution_limit:
            self.StopSearch()

        # exclusion = []
        # for class_key, var in self._class_vars.items():
        #     if self.Value(var):
        #         exclusion.append(var)
        # self.model.AddBoolOr([var.Not() for var in exclusion])

    def get_last_exclusion_clause(self):
        exclusion = []
        for class_key, var in self._class_vars.items():
            if self.Value(var):
                exclusion.append(var)
        return exclusion


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
    ftt = filter_timetable(link=link, modules=modules, isLink=isLink, semester=semester)
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
    session_groups = defaultdict(list)  # Groups sessions by similar time slots

    session_id = 0
    # Create variables and constraints
    for module, module_info in timetable_data.items():
        # For each lesson type (Lecture, Tutorial, etc.) in the module
        for lesson_type, classes in module_info["timetable"].items():
            # For each class number (1, 2, etc.) in the lesson type
            for class_no, sessions in classes.items():
                # Create a unique key for this class and a decision variable
                class_key = (module, lesson_type, class_no)
                class_vars[class_key] = model.NewBoolVar(
                    f"class_{module}_{lesson_type}_{class_no}"
                )

                # Process each session in this class
                for session in sessions:
                    if session["day"] not in day_map:
                        continue  # Skip sessions on unsupported days

                    # Convert time from "HHMM" format to minutes since midnight
                    start = int(session["startTime"][:2]) * 60 + int(
                        session["startTime"][2:]
                    )
                    end = int(session["endTime"][:2]) * 60 + int(session["endTime"][2:])

                    # Store all session data in a dictionary
                    session_data = {
                        "id": session_id,
                        "module": module,
                        "lesson_type": lesson_type,
                        "class_no": class_no,
                        "day": day_map[session["day"]],  # Convert day name to number
                        "day_name": session["day"],  # Keep original day name
                        "start": start,  # Start time in minutes
                        "end": end,  # End time in minutes
                        "weeks": session["weeks"],  # List of weeks this session occurs
                        "venue": session["venue"],  # Location of the session
                    }
                    all_sessions.append(session_data)

                    # Create a variable for this session that's tied to its class selection
                    session_vars[session_id] = model.NewBoolVar(f"s_{session_id}")
                    # Constraint: session is active iff its class is selected
                    model.Add(session_vars[session_id] == class_vars[class_key])

                    # Group sessions by their class for later constraints
                    class_groups[class_key].append(session_id)
                    # Map session ID back to its class for easy lookup
                    session_to_class[session_id] = class_key

                    # Create time intervals for each week this session occurs
                    for week in session["weeks"]:
                        # Optional interval that's only active if session is selected
                        interval_var = model.NewOptionalIntervalVar(
                            start,  # Start time
                            end - start,  # Duration
                            end,  # End time
                            session_vars[session_id],  # Activation variable
                            f"i_{session_id}_w{week}",  # Unique name
                        )
                        # Store interval by day and week for no-overlap constraints
                        time_intervals[(session_data["day"], week)].append(interval_var)

                    # Group sessions by similar time slots (for group key functionality)
                    group_key = (
                        module,
                        lesson_type,
                        day_map[session["day"]],
                        start,
                        end,
                    )
                    session_groups[group_key].append(session_data)

                    session_id += 1  # Increment session ID counter

    for group_key, sessions in session_groups.items():
        # Skip groups with only one option
        if len(sessions) <= 1:
            continue

        # Sort sessions by class number (ascending)
        sessions_sorted = sorted(sessions, key=lambda x: x["class_no"])

        # Get the class variables in order
        class_vars_sorted = [
            class_vars[(s["module"], s["lesson_type"], s["class_no"])]
            for s in sessions_sorted
        ]

        # Force selection of smallest available class number
        for i in range(1, len(class_vars_sorted)):
            # If any larger class is selected, force the smallest to be selected instead
            model.AddImplication(class_vars_sorted[i], class_vars_sorted[0])

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

        # Time-based grouping (for no-overlap)
    for group_key, sessions in session_groups.items():
        # No need for group_var or AddExactlyOne here!
        # Just ensure no two classes in the same group are selected
        class_vars_in_group = [
            class_vars[(s["module"], s["lesson_type"], s["class_no"])] for s in sessions
        ]
        model.AddAtMostOne(class_vars_in_group)  # No double-booking

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
                0 if not CONFIG["enable_late_start"] else CONFIG["earliest_start"]
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
            if day in CONFIG["days_without_lunch"]:
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

    def int_sum(objective_terms):
        sum = 0
        pprint(objective_terms)
        for i in objective_terms:
            sum += i
        return int(sum)

    # Set objective to maximize
    if CONFIG["enable_weights"]:
        model.Maximize(sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    solution_limit = 100

    # First solve to find optimal solution
    solver.parameters.random_seed = 88
    solver.parameters.enumerate_all_solutions = False  # Disable for first solve
    solver.parameters.max_time_in_seconds = 10.0

    status = solver.Solve(model)
    best_solution_printer = TimetableSolutionPrinter(
        class_vars,
        class_groups,
        all_sessions,
        semester,
        solution_limit,
        CONFIG,
        model,
    )

    print_and_write_to_file(best_solution_printer, best_solution_printer, True)

    if status == cp_model.OPTIMAL:
        best_val = solver.ObjectiveValue()
        print(f"Optimal solution found with objective value: {best_val}")

        # Add constraint for future solutions
        tolerance = 0.5  # 10% tolerance
        upper_bound = int(best_val * (1 + tolerance))

        # Create a new variable for the total objective

        model.ClearObjective()

        solver = cp_model.CpSolver()
        solver.parameters.random_seed = 42  # Change seed to vary solutions
        solver.parameters.use_phase_saving = False  # Disable heuristic memory
        solver.parameters.enumerate_all_solutions = False  # Disable for first solve
        solver.parameters.max_time_in_seconds = 300.0

        # model.Add(sum(objective_terms) >= -20000)

        # Now find multiple solutions within the range

        solver.parameters.enumerate_all_solutions = True
        solution_printer = TimetableSolutionPrinter(
            class_vars,
            class_groups,
            all_sessions,
            semester,
            solution_limit,
            CONFIG,
            model,
        )
        solver.Solve(model, solution_printer)
        print_and_write_to_file(solution_printer, best_solution_printer, isPrint=False)
    else:
        print("No optimal solution found.")


if __name__ == "__main__":
    # Example usage
    modules = ["CS2107", "CS3243", "EE2211", "EE2012", "EE3331C"]
    result = main(
        link="https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A4&CDE2310=LEC:1,LAB:1&CDE3301=LEC:1,LAB:G10&CG2023=LEC:03,LAB:05&LEC:01&CS3240=LEC:1,TUT:3&EE2026=TUT:05,LEC:01,LAB:03&EE4204=PLEC:01,PTUT:01&IE2141=TUT:09,LEC:2",
        isLink=False,
        modules=modules,
        semester=1,
    )
