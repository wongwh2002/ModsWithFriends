from config_2 import CONFIG
from csp_timetable import solve_for_timetables
from load_modules import load_mods
import time

SHARED_LESSON_TYPES = ['TUT', 'LAB']

def set_compulsory_class(config, user, mod, lesson_type, class_no):

    """
    Sets the specified class as compulsory for the user in config. 
    Returns True if successful, returns False if user already has a compulsory class 
    set for the mod and lesson type
    """

    user_config = config[user]
    if mod not in user_config["compulsory_classes"]:
        user_config["compulsory_classes"][mod] = {
            lesson_type: class_no
        }
        return True
    if lesson_type not in user_config["compulsory_classes"][mod]:
        user_config["compulsory_classes"][mod][lesson_type] = class_no
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
                recently_set_compulsory = set()
                # Check if valid
                for user, mod, lt, cn in current:
                    is_valid = set_compulsory_class(config, user, mod, lt, cn)
                    if is_valid:
                        recently_set_compulsory.add((user, mod, lt, cn))
                    if not is_valid:
                        for compulsory_class in recently_set_compulsory:
                            user, mod, lt, cn = compulsory_class
                            remove_compulsory_class(config, user, mod, lt, cn)

                if is_valid:
                    if len(solve_for_timetables(config, max_solutions=1, data=data)) == 0:
                        is_valid = False

                if is_valid:
                    all_permutations.append(current)
                
                for user, mod, lt, cn in recently_set_compulsory:
                    remove_compulsory_class(config, user, mod, lt, cn)
            
            continue

        group, mod, lesson_type, class_nos = unassigned[index]

        for class_no in class_nos:
            new_set = current.copy()
            for user in group:
                new_set.add((user, mod, lesson_type, class_no))
            stack.append((index + 1, new_set))
    
    return all_permutations



def main():
    all_modules = set()
    for user in CONFIG["users"]:
        for mod in CONFIG[user]["modules"]:
            all_modules.add(mod)
    data = load_mods(list(all_modules), CONFIG["semester"])

    start_time = time.time()
    permutations = permutate_shared_mods(CONFIG, data)
    time_taken = time.time() - start_time
    print(f"{time_taken:.4f} seconds")

    print(len(permutations))

    for permutation in permutations:
        print("\n")
        for assignment in permutation:
            print(f"{assignment[0]}: {assignment[1]} {assignment[2]} {assignment[3]}")

if __name__ == "__main__":
    main()
