from collections import defaultdict
import copy
import json
import math
import os
from load_modules import load_mods
from timetable import Timetable
from config import CONFIG


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


days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


class Csp:
    def __init__(self, modules, config):

        self.data, self.start_time_dict, self.end_time_dict = load_mods(modules)

        # For reference
        folder_path = "storage"
        try:
            os.makedirs(folder_path, exist_ok=True)
        except OSError as e:
            print(str(e))
        with open("storage/data.json", "w") as f:
            json.dump(self.data, f, indent=2)
        with open("storage/start_time.json", "w") as f:
            json.dump(self.start_time_dict, f, indent=2)
        with open("storage/end_time.json", "w") as f:
            json.dump(self.end_time_dict, f, indent=2)

        self.config = config
        self.assigned: set[tuple[str, str, str]] = set()
        # set where each element is (module_code, lesson_type, class_no)
        self.unassigned: set[tuple[str, str]] = set()
        # set where each element is (module_code, lesson_type)
        self.domains = defaultdict(lambda: defaultdict(list))
        for mod, mod_info in self.data.items():
            for lesson_type, lesson_type_info in mod_info.items():
                self.unassigned.add((mod, lesson_type))
                for class_no in lesson_type_info:
                    self.domains[mod][lesson_type].append((class_no, 0))
        self.all_solutions = []
        self.reached_states: set[tuple[tuple[str, str, str]]] = set()

        self.max_solutions = None 
        self.lunch_days = None
        self.possible_lunch_start_times = None
        self.has_lesson_in_window = {}

        if self.config["enable_lunch_break"]:
            self.lunch_days = [days_of_the_week[i] for i in range(7) if i not in self.config["lunch_except_days"]]
            self.possible_lunch_start_times = self.get_start_times(self.config["lunch_window"])
            for day in self.lunch_days:
                self.has_lesson_in_window[day] = [False] * len(self.possible_lunch_start_times)
    
    @staticmethod
    def get_start_times(lunch_window: tuple[int, int]) -> list[str]:
        start, end = lunch_window
        list = [_ for _ in range(start, end, 30)]
        return [mins_to_str(i) for i in list]



def assign(csp, mod, lesson_type, class_no):
    csp.assigned.add((mod, lesson_type, class_no))
    csp.unassigned.remove((mod, lesson_type))


def unassign(csp, mod, lesson_type, class_no):
    csp.unassigned.add((mod, lesson_type))
    csp.assigned.remove((mod, lesson_type, class_no))


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


def update_lunch_window(csp: Csp, affected_days: list[tuple[str, str, str]]):
    assert(csp.config["enable_lunch_break"])
    for day, start_time, end_time in affected_days:
        if day in csp.lunch_days:
            blocked_timings = Csp.get_start_times((str_to_mins(start_time), str_to_mins(end_time)))
            for i in range(len(csp.possible_lunch_start_times)):
                if csp.possible_lunch_start_times[i] in blocked_timings:
                    csp.has_lesson_in_window[day][i] = True


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



def update_domains(csp, mod, lesson_type, class_no) -> bool:
    affected_days = [(slot["day"], slot["startTime"], slot["endTime"]) for slot in csp.data[mod][lesson_type][class_no]["slots"]]
    if csp.config["enable_lunch_break"]:
        update_lunch_window(csp, affected_days)
        # Check if there is a lunch break within lunch window
        min_no_of_consecutive_slots = math.ceil(csp.config["lunch_duration"] / 30)
        for affected_day, start_time, end_time in affected_days:
            if affected_day in csp.lunch_days:
                if not has_consecutive_slots(csp.has_lesson_in_window[affected_day], min_no_of_consecutive_slots):
                    return False
    # Returns False if there is a new domain that is empty, True otherwise
    for (unassigned_mod, unassigned_lesson_type) in csp.unassigned:
        for unassigned_class_no, score in csp.domains[unassigned_mod][unassigned_lesson_type][:]:
            if has_clash(csp, mod, lesson_type, class_no, unassigned_mod, unassigned_lesson_type, unassigned_class_no):
                csp.domains[unassigned_mod][unassigned_lesson_type].remove((unassigned_class_no, score))
            else:
                for slot in csp.data[unassigned_mod][unassigned_lesson_type][unassigned_class_no]["slots"]:
                    for day, start, end in affected_days:
                        if slot["day"] == day:
                            if slot["startTime"] > end:
                                mins_apart = str_to_mins(slot["startTime"]) - str_to_mins(end)
                            else:
                                mins_apart = str_to_mins(start) - str_to_mins(slot["endTime"])
                            for index, domain_item in enumerate(csp.domains[unassigned_mod][unassigned_lesson_type]):
                                if domain_item[0] == unassigned_class_no:
                                    new_tuple = (unassigned_class_no, domain_item[1] + (1440 - mins_apart))
                                    csp.domains[unassigned_mod][unassigned_lesson_type][index] = new_tuple


        if len(csp.domains[unassigned_mod][unassigned_lesson_type]) == 0:
            return False
    return True


def get_current_state(assigned: set[tuple[str, str, str]]) -> tuple[tuple[str, str, str]]:
    return tuple(sorted(assigned))


def backtrack(csp: Csp) -> None:
    if len(csp.unassigned) == 0:
        csp.all_solutions.append((copy.deepcopy(csp.assigned)))
        return
    curr_mod, curr_lesson_type = next(iter(csp.unassigned)) # Take any element from unassigned
    csp.domains[curr_mod][curr_lesson_type] = sorted(csp.domains[curr_mod][curr_lesson_type], key=lambda x: -x[1])
    domain = csp.domains[curr_mod][curr_lesson_type]
    for class_no, score in domain:
        # Assign
        assign(csp, curr_mod, curr_lesson_type, class_no)
        if get_current_state(csp.assigned) in csp.reached_states:
            continue
        # Check for empty domains
        prev_domains = copy.deepcopy(csp.domains)
        prev_lunch = copy.deepcopy(csp.has_lesson_in_window)
        is_valid = update_domains(csp, curr_mod, curr_lesson_type, class_no)
        # If not empty, continue
        if is_valid:
            csp.reached_states.add(get_current_state(csp.assigned))
            backtrack(csp)
            if csp.max_solutions is not None and len(csp.all_solutions) >= csp.max_solutions:
                return
        unassign(csp, curr_mod, curr_lesson_type, class_no)
        csp.domains.clear()
        csp.domains.update(prev_domains)
        csp.has_lesson_in_window.clear()
        csp.has_lesson_in_window.update(prev_lunch)
    return

def main():
    modules = CONFIG["modules"]

    csp = Csp(modules, CONFIG)

    earliest_start_time = csp.config["earliest_start"] if csp.config["enable_early_start"] else None
    latest_end_time = csp.config["latest_end"] if csp.config["enable_early_end"] else None
    # Loop through, if domain only has 1 element then assign
    for mod_key, mod_val in csp.domains.items():
        for lesson_type_key, lesson_type_val in mod_val.items():
            
            # Remove slots on days not selected by user
            school_days_strings = [days_of_the_week[day_index] for day_index in csp.config["school_days"]]
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
                print(json.dumps(csp.domains, indent=2))
                print("no solution")
                return

            # Assign slots that only have 1 possible value
            if len(lesson_type_val) == 1:
                assign(csp, mod_key, lesson_type_key, lesson_type_val[0][0])
                is_valid = update_domains(csp, mod_key, lesson_type_key, lesson_type_val[0][0])
                if not is_valid:
                    print("no solution after assigning lectures")
                    return


    backtrack(csp)
    if len(csp.all_solutions) == 0:
        print("no solution, len=0")
        return
    with open("output.txt", "w") as f:
        for i, solution in enumerate(csp.all_solutions):
            timetable = Timetable()
            for assigned_class in solution:
                timetable.add_class(assigned_class[0], assigned_class[1], assigned_class[2])
            f.write(f"Solution {i + 1}:\n  {timetable.get_url()}\n")


if __name__ == "__main__":
    main()
