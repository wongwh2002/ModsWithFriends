from get_timetable import filter_timetable
from ortools.sat.python import cp_model
from pprint import pprint
from collections import defaultdict
import json

CONFIG = {
    "earliest_start": 9 * 60,  # 9am
    "latest_end": 18 * 60,  # 6pm
    "want_lunch_break": True,
    "lunch_window": (11 * 60, 14 * 60),  # 11am-2pm
    "lunch_duration": 60,
    "optional_classes": {"CG2023": ["Tutorial"]},  # Only make CG2023 tutorials optional
    "weights": {
        "morning_class": 3,
        "afternoon_class": 1,
        "day_length_penalty": -0.1,
        "day_present_penalty": -10,
    },
    "enable_early_start": True,  # Toggle for 9am constraint
    "enable_early_end": True,  # Toggle for 6pm constraint
    "enable_compact": True,  # Toggle for compact schedule
}


def main(modules=["CS2113", "CG2023", "EE2211"]):
    # Load timetable data
    ftt = filter_timetable(modules=modules, isLink=False)
    timetable_data = ftt["timetable"]
    semester = ftt["semester"]
    model = cp_model.CpModel()

    # Data structures
    class_groups = defaultdict(list)
    class_vars = {}
    all_sessions = []
    session_vars = {}
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    time_intervals = defaultdict(list)
    day_present_vars = []  # For tracking days on campus

    # Create toggle variables
    toggle_early_start = model.NewBoolVar("toggle_early_start")
    toggle_early_end = model.NewBoolVar("toggle_early_end")
    toggle_compact = model.NewBoolVar("toggle_compact")
    toggle_lunch = model.NewBoolVar("toggle_lunch")

    # Process all sessions
    session_id = 0
    for module, module_info in timetable_data.items():
        for lesson_type, classes in module_info["timetable"].items():
            # Check if this lesson type is optional
            is_optional = (
                module in CONFIG["optional_classes"]
                and lesson_type in CONFIG["optional_classes"][module]
            )

            for class_no, sessions in classes.items():
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

                    class_groups[class_key].append(session_id)

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
    required_lessons = ["Laboratory", "Lecture", "Tutorial"]
    for module in timetable_data:
        for lesson_type in required_lessons:
            if lesson_type in timetable_data[module]["timetable"]:
                class_options = [
                    class_vars[key]
                    for key in class_vars
                    if key[0] == module and key[1] == lesson_type
                ]
                if class_options:
                    # Use AtMostOne for optional classes, ExactlyOne otherwise
                    if (
                        module in CONFIG["optional_classes"]
                        and lesson_type in CONFIG["optional_classes"][module]
                    ):
                        model.AddAtMostOne(class_options)
                    else:
                        model.AddExactlyOne(class_options)

    # No overlapping sessions
    for intervals in time_intervals.values():
        model.AddNoOverlap(intervals)

    # Day start/end constraints
    for day in range(5):
        day_sessions = [sid for sid, s in enumerate(all_sessions) if s["day"] == day]

        # Track if any sessions on this day
        day_present = model.NewBoolVar(f"day_{day}_present")
        model.AddMaxEquality(day_present, [session_vars[sid] for sid in day_sessions])
        day_present_vars.append(day_present)

        if day_sessions:
            # Day start/end variables
            day_start = model.NewIntVar(0, 24 * 60, f"day_start_{day}")
            day_end = model.NewIntVar(0, 24 * 60, f"day_end_{day}")

            # Link to actual sessions
            for sid in day_sessions:
                session = all_sessions[sid]
                model.Add(day_start <= session["start"]).OnlyEnforceIf(
                    session_vars[sid]
                )
                model.Add(day_end >= session["end"]).OnlyEnforceIf(session_vars[sid])

            # Apply time windows if toggled on
            model.Add(day_start >= CONFIG["earliest_start"]).OnlyEnforceIf(
                toggle_early_start.And(day_present)
            )
            model.Add(day_end <= CONFIG["latest_end"]).OnlyEnforceIf(
                toggle_early_end.And(day_present)
            )

            # Compact schedule objective
            if CONFIG["enable_compact"]:
                day_length = day_end - day_start
                model.Add(day_length >= 0)  # Ensure valid duration

    # Lunch break constraints
    if CONFIG["want_lunch_break"]:
        for day in range(5):
            day_sessions = [
                sid for sid, s in enumerate(all_sessions) if s["day"] == day
            ]
            if day_sessions:
                lunch_start = model.NewIntVar(
                    CONFIG["lunch_window"][0],
                    CONFIG["lunch_window"][1] - CONFIG["lunch_duration"],
                    f"lunch_start_{day}",
                )
                lunch_end = lunch_start + CONFIG["lunch_duration"]
                lunch_interval = model.NewIntervalVar(
                    lunch_start, CONFIG["lunch_duration"], lunch_end, f"lunch_{day}"
                )

                # Ensure no overlap if lunch is enabled
                for sid in day_sessions:
                    session = all_sessions[sid]
                    temp_interval = model.NewIntervalVar(
                        session["start"],
                        session["end"] - session["start"],
                        session["end"],
                        f"temp_{sid}",
                    )
                    model.AddNoOverlap([lunch_interval, temp_interval]).OnlyEnforceIf(
                        toggle_lunch.And(session_vars[sid])
                    )

    # Objective function
    objective_terms = []

    # 1. Class time preferences
    for sid, session in enumerate(all_sessions):
        if session["start"] < 12 * 60:  # Morning class
            objective_terms.append(
                session_vars[sid] * CONFIG["weights"]["morning_class"]
            )
        else:
            objective_terms.append(
                session_vars[sid] * CONFIG["weights"]["afternoon_class"]
            )

    # 2. Compact schedules
    if CONFIG["enable_compact"]:
        for day in range(5):
            day_sessions = [
                sid for sid, s in enumerate(all_sessions) if s["day"] == day
            ]
            if day_sessions:
                day_start = model.GetIntVarFromIndex(f"day_start_{day}")
                day_end = model.GetIntVarFromIndex(f"day_end_{day}")
                objective_terms.append(
                    (day_end - day_start) * CONFIG["weights"]["day_length_penalty"]
                )

    # 3. Minimize days on campus
    objective_terms.extend(
        day_var * CONFIG["weights"]["day_present_penalty"]
        for day_var in day_present_vars
    )

    model.Maximize(sum(objective_terms))

    # Configure solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.random_seed = 42  # For reproducibility
    solver.parameters.num_search_workers = 8  # Use multiple cores

    # Solution printer
    class TopSolutionsPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, class_vars, all_sessions, class_groups, limit=5):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._class_vars = class_vars
            self._all_sessions = all_sessions
            self._class_groups = class_groups
            self._limit = limit
            self.solutions = []
            self.lesson_abbr = {
                "Laboratory": "LAB",
                "Lecture": "LEC",
                "Tutorial": "TUT",
            }

        def on_solution_callback(self):
            current_score = self.ObjectiveValue()
            solution = {
                "score": current_score,
                "schedule": defaultdict(list),
                "selected": defaultdict(list),
                "days_present": 0,
            }

            # Process selected classes
            for class_key, var in self._class_vars.items():
                if self.Value(var):
                    module, lesson_type, class_no = class_key
                    solution["selected"][module].append(
                        f"{self.lesson_abbr.get(lesson_type, lesson_type)}:{class_no}"
                    )

                    # Add sessions to schedule
                    for sid in self._class_groups[class_key]:
                        if self.Value(sid):
                            session = self._all_sessions[sid]
                            solution["schedule"][session["day_name"]].append(
                                {
                                    "module": module,
                                    "type": lesson_type,
                                    "class": class_no,
                                    "start": f"{session['start']//60:02d}{session['start']%60:02d}",
                                    "end": f"{session['end']//60:02d}{session['end']%60:02d}",
                                    "venue": session["venue"],
                                }
                            )

            # Count days present
            solution["days_present"] = sum(
                1 for day in solution["schedule"] if solution["schedule"][day]
            )

            # Generate NUSMods link
            url_parts = []
            for module, classes in solution["selected"].items():
                url_parts.append(f"{module}={'+'.join(classes)}")
            solution["nusmods_link"] = (
                f"https://nusmods.com/timetable/sem-{semester}/share?{'&'.join(url_parts)}"
            )

            # Store solution (maintain top N)
            self.solutions.append(solution)
            self.solutions.sort(key=lambda x: -x["score"])
            if len(self.solutions) > self._limit:
                self.solutions = self.solutions[: self._limit]

            if len(self.solutions) >= self._limit:
                self.StopSearch()

    # Solve
    solution_printer = TopSolutionsPrinter(
        class_vars, all_sessions, class_groups, limit=5
    )
    solver.Solve(model, solution_printer)

    # Output results
    print(f"\nFound {len(solution_printer.solutions)} optimal solutions:")
    for i, solution in enumerate(solution_printer.solutions, 1):
        print(f"\nSolution #{i} (Score: {solution['score']:.1f})")
        print(f"NUSMods Link: {solution['nusmods_link']}")
        print(f"Days on campus: {solution['days_present']}")

        print("\nSchedule:")
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if day in solution["schedule"]:
                print(f"  {day}:")
                for session in solution["schedule"][day]:
                    print(
                        f"    {session['start']}-{session['end']} {session['module']} "
                        f"{session['type']} {session['class']} at {session['venue']}"
                    )

    # Save to file
    with open("timetable_solutions.json", "w") as f:
        json.dump(
            {"config": CONFIG, "solutions": solution_printer.solutions}, f, indent=2
        )


if __name__ == "__main__":
    main(modules=["CS2113", "CG2023", "EE2211"])
