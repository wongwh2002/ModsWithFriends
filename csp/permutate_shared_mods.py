import copy
import json
from config_2 import CONFIG
from csp_timetable import solve_for_timetables
from load_modules import load_mods, abbreviations, reverse_abbreviations
import time

SHARED_LESSON_TYPES = ['TUT', 'LAB']

def set_compulsory_class(config, user, mod, lesson_type, class_no):

    """
    Sets the specified class as compulsory for the user in config. 
    Returns True if successful, returns False if user already has a compulsory class 
    set for the mod and lesson type
    """

    lesson_type_key = reverse_abbreviations[lesson_type]

    user_config = config[user]
    if mod not in user_config["compulsory_classes"]:
        user_config["compulsory_classes"][mod] = {
            lesson_type_key: class_no
        }
        return True
    if lesson_type_key not in user_config["compulsory_classes"][mod]:
        user_config["compulsory_classes"][mod][lesson_type_key] = class_no
        return True
    if user_config["compulsory_classes"][mod][lesson_type_key] == class_no:
        return True
    return False


def remove_compulsory_class(config, user, mod, lesson_type, class_no):
    del config[user]["compulsory_classes"][mod][lesson_type]
    if len(config[user]["compulsory_classes"][mod]) == 0:
        del config[user]["compulsory_classes"][mod]


def permutate_shared_mods(config, data):
    visited = set()
    unassigned = []
    for mod in config["shared"]:
        for group in config["shared"][mod]:
            for lesson_type in SHARED_LESSON_TYPES:
                if lesson_type not in data[mod]:
                    continue
                class_nos = list(data[mod][lesson_type].keys())
                unassigned.append((group, mod, lesson_type, class_nos))

    stack: list[tuple[int, set[tuple[str, str, str, str]]]] = [(0, set())]
    all_permutations = []

    while stack:
        index, current = stack.pop()

        if index == len(unassigned):
            frozen = frozenset(current)
            if frozen not in visited:
                is_valid = True
                visited.add(frozen)
                new_config = copy.deepcopy(config)
                # Check if valid
                for user, mod, lt, cn in current:
                    if set_compulsory_class(new_config, user, mod, lt, cn) == False:
                        is_valid = False

                if is_valid:
                    solutions = solve_for_timetables(new_config, max_solutions=1, data=copy.deepcopy(data))
                    if len(solutions) == 0:
                        is_valid = False

                if is_valid:
                    all_permutations.append(current)
            
            continue

        group, mod, lesson_type, class_nos = unassigned[index]

        for class_no in class_nos:
            new_set = current.copy()
            for user in group:
                new_set.add((user, mod, lesson_type, class_no))
            stack.append((index + 1, new_set))
    
    return all_permutations


def edit_config_for_one_person(config, user, assignment):
    config["shared"] = {}
    config["users"] = [user]
    for assigned_mod, assigned_lt, assigned_cn in assignment:
        assert set_compulsory_class(config, user, assigned_mod, assigned_lt, assigned_cn) == True




def main():
    all_modules = set()
    for user in CONFIG["users"]:
        for mod in CONFIG[user]["modules"]:
            all_modules.add(mod)
    data = load_mods(list(all_modules), CONFIG["semester"])

    permutations = permutate_shared_mods(CONFIG, data)

    print(len(permutations))
    for permutation in permutations:
        print("\n")
        for assignment in permutation:
            print(f"{assignment[0]}: {assignment[1]} {assignment[2]} {assignment[3]}")

    for user in CONFIG["users"]:
        print(f"{user}:")
        user_specific_assignments = set()

        for permutation in permutations:
            assignment_for_user = frozenset(
                (mod, lt, cn)
                for assigned_user, mod, lt, cn in permutation
                if assigned_user == user
            )
            if assignment_for_user:
                user_specific_assignments.add(assignment_for_user)
        
        if len(user_specific_assignments) == 0:
            user_specific_assignments.add(frozenset())

        for i, assignment in enumerate(user_specific_assignments):
            print(f"Solution {i}:")
            for mod, lt, cn in assignment:
                print(f"{mod} {lt} {cn}")

            user_config = copy.deepcopy(CONFIG)
            edit_config_for_one_person(user_config, user, assignment)

            results = solve_for_timetables(user_config, max_solutions=10, data=data)
            for result in results:
                print(str(result))



if __name__ == "__main__":
    main()
