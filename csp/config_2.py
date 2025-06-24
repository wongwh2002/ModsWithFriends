CONFIG = {
    "semester": 2,
    "users": ["A", "B"],
    "A": {
        "modules" : ['GESS1002', 'MA3205', 'CS3281', 'CG2023', 'CG2027', 'CG2028'],
        # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'EE2211', 'CG2027', 'CG2028'], # invalid
        # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'CG2027', 'CG2028'], 

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
            "CG2027": ["Lecture"],
            "CG2028": ["Lecture"],
        },
        "compulsory_classes": {
            # "CG2023": {"Lecture": "01",
            #         "Laboratory": "05"},
        },
        "weights": {  # Weights for optimization criteria
            "morning_class": 1,  # Preference for morning classes
            "afternoon_class": 5,  # Preference for afternoon classes
            "day_length_penalty": -0.01,  # Penalty for long days
            "day_present_penalty": -10,  # Penalty for having classes on a day
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },
    "B": {

        "modules" : ['CS2113', 'CG2023', 'EE2211', 'CDE2501', 'EE2026'],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
        },
        "compulsory_classes": {
            # "CG2023": {"Lecture": "01",
            #         "Laboratory": "05"},
            # "CS2113": {
            #     "Tutorial": "10"
            # }
        },
        "weights": {  # Weights for optimization criteria
            "morning_class": 1,  # Preference for morning classes
            "afternoon_class": 5,  # Preference for afternoon classes
            "day_length_penalty": -0.01,  # Penalty for long days
            "day_present_penalty": -10,  # Penalty for having classes on a day
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },
    "shared": {
        "CG2023": [["A", "B"]],
    }
}