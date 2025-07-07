from collections import defaultdict
import copy
import json
import math
import os
from load_modules import load_mods, abbreviations, reverse_abbreviations
from solution import Solution
from config_2 import CONFIG


def mins_to_str(mins: int) -> str:
    """
    Takes in mins after midnight, returns string representing time in 24h format
    """

    hours = mins // 60
    mins_str = mins % 60

    return str(hours) + str(mins_str).zfill(2)


def str_to_mins(string: str) -> int:
    """
    Takes in time represented as a string in 24h format, returns number of minutes after midnight
    """
    hours_str = string[:2]
    mins_str = string[2:]

    return int(hours_str) * 60 + int(mins_str)


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
COMMON_LESSON_TYPES = ['LAB', 'TUT']


class Csp:
    def __init__(self, config, max_solutions = None, max_solutions_per_user = None, data = None):

        self.max_solutions = max_solutions
        self.max_solutions_per_user = max_solutions_per_user

        self.config = config
        self.users = self.config["users"]

        self.all_modules = set()
        for user in self.users:
            for mod in self.config[user]["modules"]:
                self.all_modules.add(mod)

        if not data:
            self.data = load_mods(list(self.all_modules), self.config["semester"])

            # For reference
            folder_path = "storage"
            try:
                os.makedirs(folder_path, exist_ok=True)
            except OSError as e:
                print(str(e))
            with open("storage/data.json", "w") as f:
                json.dump(self.data, f, indent=2)
            # with open("storage/start_time.json", "w") as f:
            #     json.dump(self.start_time_dict, f, indent=2)
            # with open("storage/end_time.json", "w") as f:
            #     json.dump(self.end_time_dict, f, indent=2)
        else:
            self.data = data

        self.assigned: set[tuple[str, str, str, str]] = set()
        # set where each element is (user, module_code, lesson_type, class_no)
        self.unassigned: set[tuple[str, str, str]] = set()
        # set where each element is (user, module_code, lesson_type)
        self.domains = defaultdict(lambda: defaultdict(lambda: defaultdict(list[tuple[str, int]])))

        
        for user in self.users:
            for mod in self.config[user]["modules"]:
                for lesson_type, lesson_type_info in self.data[mod].items():
                    self.unassigned.add((user, mod, lesson_type))
                    if (mod in self.config[user]["compulsory_classes"]) and (reverse_abbreviations[lesson_type] in self.config[user]["compulsory_classes"][mod]):
                        lesson_type_str = reverse_abbreviations[lesson_type]
                        self.domains[user][mod][lesson_type] = [(self.config[user]["compulsory_classes"][mod][lesson_type_str], 0)]
                    else:
                        for class_no in lesson_type_info:
                            self.domains[user][mod][lesson_type].append((class_no, 0))
        

        self.all_solutions: list[Solution] = []
        self.reached_states: set[tuple[tuple[str, str, str, str]]] = set()

        self.optional_classes: defaultdict[str, set[tuple[str, str]]] = defaultdict(set)

        for user in self.users:
            for module_code, optional_lesson_types in self.config[user]["optional_classes"].items():
                for lesson_type in optional_lesson_types:
                    self.optional_classes[user].add((module_code, abbreviations[lesson_type]))

        self.lunch_days: dict[str, list[str]] = {}
        for user in self.users:
            self.lunch_days[user] = None

        self.possible_lunch_start_times: dict[str, list[str]] = {}
        for user in self.users:
            self.possible_lunch_start_times[user] = None

        self.has_lesson_in_window: dict[str, dict[str, list[bool]]] = {}
        for user in self.users:
            self.has_lesson_in_window[user] = {}
            
        for user in self.users:
            if self.config[user]["enable_lunch_break"]:
                self.lunch_days[user] = [WEEKDAYS[i] for i in range(5) if (i + 1) not in self.config[user]["days_without_lunch"]]
                self.possible_lunch_start_times[user] = self.get_start_times(self.config[user]["lunch_window"])
                for day in self.lunch_days[user]:
                    self.has_lesson_in_window[user][day] = [False] * len(self.possible_lunch_start_times[user])
        
        self.solutions: dict[str, set[frozenset[tuple[str, str, str]]]] = {} 
        for user in self.users:
            self.solutions[user] = set()

    
    @staticmethod
    def get_start_times(lunch_window: tuple[int, int]) -> list[str]:
        start, end = lunch_window
        list = [_ for _ in range(start, end, 30)]
        return [mins_to_str(i) for i in list]



def assign(csp, user, mod, lesson_type, class_no):
    csp.assigned.add((user, mod, lesson_type, class_no))
    csp.unassigned.discard((user, mod, lesson_type))


def unassign(csp, user, mod, lesson_type, class_no):
    csp.unassigned.add((user, mod, lesson_type))
    csp.assigned.discard((user, mod, lesson_type, class_no))


def are_disjoint(list1: list, list2: list) -> bool:
    for item in list1:
        if item in list2:
            return False
    return True


def are_clashing_slots(slot1, slot2):
    # No clash if weeks are disjoint
    if are_disjoint(slot1["weeks"], slot2["weeks"]):
        return False
    # No clash if days are different
    if slot1["day"] != slot2["day"]:
        return False
    if slot1["startTime"] >= slot2["endTime"]:
        return False
    if slot2["startTime"] >= slot1["endTime"]:
        return False
    return True


def has_clash(csp, mod1, lesson_type1, class_no1, mod2, lesson_type2, class_no2):
    slots1 = csp.data[mod1][lesson_type1][class_no1]["slots"]
    slots2 = csp.data[mod2][lesson_type2][class_no2]["slots"]
    for slot1 in slots1:
        for slot2 in slots2:
            if are_clashing_slots(slot1, slot2):
                return True
    return False


def update_lunch_window(csp: Csp, user: str, affected_days: list[tuple[str, str, str]]):
    assert(csp.config[user]["enable_lunch_break"])
    for day, start_time, end_time in affected_days:
        if day in csp.lunch_days[user]:
            blocked_timings = Csp.get_start_times((str_to_mins(start_time), str_to_mins(end_time)))
            for i in range(len(csp.possible_lunch_start_times[user])):
                if csp.possible_lunch_start_times[user][i] in blocked_timings:
                    csp.has_lesson_in_window[user][day][i] = True


def has_consecutive_slots(arr: list[bool], n: int) -> bool:
    """Checks if the given list has at least n consecutive False values.

    Args:
        arr (list[bool]): List to iterate through
        n (int): Number of consecutive slots to check for 

    Returns:
        bool
    """

    if len(arr) < n:
        return False
    
    if not arr:
        return False
    
    counter = 0
    for val in arr:
        if val == True:
            counter = 0
        else:
            counter += 1
        if counter >= n:
            return True
    
    return False


def update_domains(csp: Csp, user: str, mod: str, lesson_type: str, class_no: str) -> bool:
    # print(f"\nUpdating domains after assigning {user} {mod} {lesson_type} {class_no}")
    # Returns False if there is a new domain that is empty or no lunch break, True otherwise
    affected_days = [(slot["day"], slot["startTime"], slot["endTime"]) for slot in csp.data[mod][lesson_type][class_no]["slots"]]
    if csp.config[user]["enable_lunch_break"] and (mod, lesson_type) not in csp.optional_classes[user]:
        update_lunch_window(csp, user, affected_days)
        # Check if there is a lunch break within lunch window
        min_no_of_consecutive_slots = math.ceil(csp.config[user]["lunch_duration"] / 30)
        for affected_day, start_time, end_time in affected_days:
            if affected_day in csp.lunch_days[user]:
                if not has_consecutive_slots(csp.has_lesson_in_window[user][affected_day], min_no_of_consecutive_slots):
                    # print(f"No lunch slot for {user} on {affected_day}")
                    return False
    for (unassigned_user, unassigned_mod, unassigned_lesson_type) in csp.unassigned:
        if unassigned_user == user:
            for unassigned_class_no, score in csp.domains[unassigned_user][unassigned_mod][unassigned_lesson_type][:]:
                if has_clash(csp, mod, lesson_type, class_no, unassigned_mod, unassigned_lesson_type, unassigned_class_no):
                    csp.domains[user][unassigned_mod][unassigned_lesson_type].remove((unassigned_class_no, score))
                elif (mod, lesson_type) not in csp.optional_classes[user]: # if no clash and not optional
                    for slot in csp.data[unassigned_mod][unassigned_lesson_type][unassigned_class_no]["slots"]:
                        for day, start, end in affected_days:
                            if slot["day"] == day:
                                if slot["startTime"] > end:
                                    mins_apart = str_to_mins(slot["startTime"]) - str_to_mins(end)
                                else:
                                    mins_apart = str_to_mins(start) - str_to_mins(slot["endTime"])
                                for index, domain_item in enumerate(csp.domains[user][unassigned_mod][unassigned_lesson_type]):
                                    if domain_item[0] == unassigned_class_no:
                                        new_tuple = (unassigned_class_no, domain_item[1] + (1440 - mins_apart))
                                        csp.domains[user][unassigned_mod][unassigned_lesson_type][index] = new_tuple


            if len(csp.domains[user][unassigned_mod][unassigned_lesson_type]) == 0:
                # print(f"No available slots for {user} {unassigned_mod} {unassigned_lesson_type}")
                return False
    return True


def get_current_state(assigned: set[tuple[str, str, str]]) -> tuple[tuple[str, str, str]]:
    return tuple(sorted(assigned))


def get_shared_users(csp: Csp, mod: str, user: str, lesson_type: str) -> list[str]:
    if lesson_type not in COMMON_LESSON_TYPES:
        return [user]
    if mod not in csp.config["shared"]:
        return [user]
    for group in csp.config["shared"][mod]:
        for group_user in group:
            if group_user == user:
                return group
    return [user]


def backtrack(csp: Csp) -> None:
    if len(csp.unassigned) == 0:
        # print(len(csp.all_solutions))
        new_solution = Solution(csp.users, csp.config["semester"])
        for assigned_class in csp.assigned:
            new_solution.add_class_for_user(assigned_class[0], assigned_class[1], assigned_class[2], assigned_class[3])
        for user in csp.users:
            csp.solutions[user].add(new_solution.timetables[user].get_assignment())
        csp.all_solutions.append(new_solution)
        return
    next_item_to_assign = next(iter(csp.unassigned))
    curr_user, curr_mod, curr_lesson_type =  next_item_to_assign # Take any element from unassigned
    csp.domains[curr_user][curr_mod][curr_lesson_type] = sorted(csp.domains[curr_user][curr_mod][curr_lesson_type], key=lambda x: -x[1])
    domain = csp.domains[curr_user][curr_mod][curr_lesson_type]
    shared_users = get_shared_users(csp, curr_mod, curr_user, curr_lesson_type)
    for class_no, score in domain:
        prev_domains = copy.deepcopy(csp.domains)
        prev_lunch = copy.deepcopy(csp.has_lesson_in_window)
        # Assign
        # If it is a shared module, lesson type, and user, once the lesson is assigned, it needs to be assigned for all users in the group. Same for unassigning.
        is_valid = True
        for shared_user in shared_users:
            assign(csp, shared_user, curr_mod, curr_lesson_type, class_no)
            if update_domains(csp, shared_user, curr_mod, curr_lesson_type, class_no) == False:
                is_valid = False
        if get_current_state(csp.assigned) in csp.reached_states:
            continue
        if is_valid:
            csp.reached_states.add(get_current_state(csp.assigned))
            backtrack(csp)
            if csp.max_solutions is not None and len(csp.all_solutions) >= csp.max_solutions:
                return
            if csp.max_solutions_per_user is not None and all(len(csp.solutions[user]) >= csp.max_solutions_per_user for user in csp.users):
                return
        # Else unassign and restore 
        for shared_user in shared_users:
            unassign(csp, shared_user, curr_mod, curr_lesson_type, class_no)
        csp.domains.clear()
        csp.domains.update(prev_domains)
        csp.has_lesson_in_window.clear()
        csp.has_lesson_in_window.update(prev_lunch)
    return

def filter_invalid_slots(csp):
    for user in csp.users:
        config = csp.config[user]
        earliest_start_time = config["earliest_start"] if config["enable_late_start"] else None
        latest_end_time = config["latest_end"] if config["enable_early_end"] else None
        school_days_strings = [WEEKDAYS[i] for i in range(5) if (i + 1) not in config["days_without_class"]]

        for mod_key, mod_val in csp.domains[user].items():
            for lesson_type_key, lesson_type_val in mod_val.items():
                if (mod_key, lesson_type_key) not in csp.optional_classes[user]:
            
                    # Remove slots on days not selected by user
                    for class_no, score in lesson_type_val[:]:
                        for slot in csp.data[mod_key][lesson_type_key][class_no]["slots"]:
                            if slot["day"] not in school_days_strings:
                                lesson_type_val.remove((class_no, score))

                    # Remove slots that violate start and end constraints
                    if earliest_start_time or latest_end_time:
                        for class_no, score in lesson_type_val[:]:
                            violates_earliest_start_time = False
                            violates_latest_end_time = False
                            start_times = [str_to_mins(slot["startTime"]) for slot in csp.data[mod_key][lesson_type_key][class_no]["slots"]]
                            end_times = [str_to_mins(slot["endTime"]) for slot in csp.data[mod_key][lesson_type_key][class_no]["slots"]]
                            if earliest_start_time:
                                for start_time in start_times:
                                    if start_time < earliest_start_time:
                                        violates_earliest_start_time = True
                            if latest_end_time:
                                for end_time in end_times:
                                    if end_time > latest_end_time:
                                        violates_latest_end_time = True
                            if violates_latest_end_time or violates_earliest_start_time:
                                lesson_type_val.remove((class_no, score))
                
                    # Check that domain is not empty:
                    if len(lesson_type_val) == 0:
                        # print(f"No slots available for {user} {mod_key} {lesson_type_key}")
                        return False

                # Assign slots that only have 1 possible value
                if len(lesson_type_val) == 1:
                    assign(csp, user, mod_key, lesson_type_key, lesson_type_val[0][0])
                    is_valid = update_domains(csp, user, mod_key, lesson_type_key, lesson_type_val[0][0])
                    if not is_valid:
                        # print(json.dumps(csp.domains, indent=2))
                        # print(f"no solution after assigning {user} {mod_key} {lesson_type_key}")
                        return False
    return True


def solve_for_timetables(config: dict, max_solutions: int = None, max_solutions_per_user: int = None, data=None):
    csp = Csp(config, max_solutions=max_solutions, max_solutions_per_user=max_solutions_per_user, data=data)

    if not filter_invalid_slots(csp):
        print("NO SOLUTION")
            
    backtrack(csp)
    if len(csp.all_solutions) == 0:
        print("no solution, len=0")

    return csp.all_solutions



def main():
    solutions = solve_for_timetables(CONFIG)

    with open("solutions.txt", "w") as f:
        for i, solution in enumerate(solutions):
            f.write(f"\n\nSolution {i + 1}:")
            for user, timetable in solution.timetables.items():
                f.write(f"\n{user}: {timetable.get_url()}")
        print("DONE")



if __name__ == "__main__":
    main()
