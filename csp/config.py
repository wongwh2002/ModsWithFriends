CONFIG = {
    # "modules" : ['CS2113', 'CG2023', 'EE2211', 'CDE2501', 'EE2026'],
    # "modules" : ['CG2023', 'EE2211', 'CDE2501', 'CS3281', 'GESS1002'],
    # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'CG2023', 'CG2027', 'CG2028'],
    # "modules" : ['CDE2000', 'CDE2310', 'CDE3301', 'CG2023', 'CS3240', 'IE2141', 'EE2026', 'EE4204'],
    # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'EE2211', 'CG2027', 'CG2028'], # invalid
    "semester": 1,
    "modules": ['CS2113', 'CG2271', 'CS1231', 'ST2334', 'ES2631', 'EE2026'],

    "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
    "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

    "lunch_window": (12 * 60, 16 * 60),  # Preferred lunch window (11AM-1PM)
    "lunch_duration": 60,  # Lunch break duration (60 minutes)
    "days_without_lunch": [],  # Days where lunch break isn't required
    "days_without_class": [],
    "optional_classes": {  # Classes that can be optionally included
        # "EE2026": ["Lecture"],
        # "EE2211": ["Lecture"],
        # "IE2141": ["Lecture"],
        "CG2027": ["Lecture"],
        "CG2028": ["Lecture"],
        "GESS1002": ["Lecture"],
        # "CS3281": ["Lecture"],
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
    "enable_lunch_break": True,  # Whether to enforce lunch breaks
    "enable_late_start": False,  # Whether to enforce earliest start time
    "enable_early_end": False,  # Whether to enforce latest end time
    "enable_weights": True,  # Whether to minimize day length
}

