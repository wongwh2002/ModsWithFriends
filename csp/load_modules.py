from collections import defaultdict
import requests
import json


def load_mods(modules: list[str]) -> tuple[dict, dict, dict]:
    abbreviations = {
        "Lecture": "LEC",
        "Laboratory": "LAB",
        "Tutorial": "TUT",
        "Packaged Lecture": "PLEC",
        "Packaged Tutorial": "PTUT",
        "Sectional Teaching": "SEC"
    }
    return_dict = defaultdict(lambda: defaultdict(dict)) 
    start_time_dict = defaultdict(lambda: defaultdict(list))
    end_time_dict = defaultdict(lambda: defaultdict(list))
    for mod in modules:
        print(f"loading data for {mod}")
        data = requests.get(f"https://api.nusmods.com/v2/2024-2025/modules/{mod}.json").json()

        sem2_timetable: list = data["semesterData"][0]["timetable"] if data["semesterData"][0]["semester"] == 2 else data["semesterData"][1]["timetable"]

        for lesson in sem2_timetable:
            slot_info = {
                "startTime": lesson["startTime"],
                "endTime": lesson["endTime"],
                "weeks": lesson["weeks"],
                "venue": lesson["venue"],
                "day": lesson["day"],
            }
            lessonType = lesson["lessonType"]
            lessonType_key = abbreviations[lessonType]
            if lesson["classNo"] in return_dict[mod][lessonType_key]:
                return_dict[mod][lessonType_key][lesson["classNo"]]["slots"].append(slot_info)
            else:
                return_dict[mod][lessonType_key][lesson["classNo"]] = {
                "size": lesson["size"],
                "lessonType": lesson["lessonType"],
                "slots": [slot_info]
            }

            # Starttime dict
            start_time_dict[lesson["day"]][lesson["startTime"]].append((mod, lessonType_key, lesson["classNo"]))
            end_time_dict[lesson["day"]][lesson["endTime"]].append((mod, lessonType_key, lesson["classNo"]))
        print(f"loaded data for {mod}")
    return return_dict, start_time_dict, end_time_dict


def main():
    modules = ['CS2113', 'CG2023', 'EE2211', 'CDE2501', 'EE2026']
    # modules = ['IE2141', 'CG2023', 'CS3281', 'MA3205', 'CG2027', 'CG2028']
    data = load_mods(modules)
    with open("storage/data3.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
