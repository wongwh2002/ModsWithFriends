CONFIG = {
    "semester": 2,
    "users": ["wx", "weng", "nigel"],
    "wx": {
        "modules" : ['GESS1002', 'MA3205', 'CS3281', 'CG2023', 'CG2027', 'CG2028'],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 16 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [5],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
            "CG2027": ["Lecture"],
            "CG2028": ["Lecture"],
        },
        "compulsory_classes": {
            "CG2023": {
                "Lecture": "04"
            }
        },
        "weights": {  # Weights for optimization criteria
            "morning_class": 1,  # Preference for morning classes
            "afternoon_class": 5,  # Preference for afternoon classes
            "day_length_penalty": -0.01,  # Penalty for long days
            "day_present_penalty": -10,  # Penalty for having classes on a day
        },
        "enable_lunch_break": True,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },

    "nigel": {
        "modules" : ['CDE2000', 'CDE2310', 'CDE3301', 'CG2023', 'CS3240', 'IE2141', 'EE2026', 'EE4204'],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
        },
        "compulsory_classes": {
            "CG2023": {
                "Lecture": "03",
            }
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

    "weng": {
        "modules" : ['CG2027', 'CG2028', 'LAM1201', 'CG2023', 'IE2141', 'CDE2000', 'CDE3301'],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
        },
        "compulsory_classes": {
            "CG2023": {"Lecture": "01",}
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
        "CG2023": [["wx", "nigel"]], # Assume wont have the case where [["A", "B"], ["A", "C"]] cuz in this case it would be [["A", "B", "C"]]
        "CG2027": [["wx", "weng"]],
        "CG2028": [["wx", "weng"]],
        "IE2141": [["weng", "nigel"]]
    },
}