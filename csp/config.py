CONFIG = {
    # "modules" : ['CS2113', 'CG2023', 'EE2211', 'CDE2501', 'EE2026'],
    # "modules" : ['CG2023', 'EE2211', 'CDE2501', 'CS3281', 'GESS1002'],
    # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'CG2023', 'CG2027', 'CG2028'],
    "modules" : ['CDE2000', 'CDE2310', 'CDE3301', 'CG2023', 'CS3240', 'IE2141', 'EE2026', 'EE4204'],
    # "modules" : ['GESS1002', 'MA3205', 'CS3281', 'EE2211', 'CG2027', 'CG2028'], # invalid

    "earliest_start": 10 * 60,  # 24hr clock
    "latest_end": 18 * 60,
    "lunch_window": (14 * 60, 16 * 60),  # start, end
    "lunch_duration": 60,
    "lunch_except_days": [6, 0],
    "optional_classes": {"CS1010": ["Lecture"], "CG2023": ["Lecture"]},
    "weights": {
        "morning_class": 1,
        "afternoon_class": 2,
        "day_length_penalty": -0.1,
        "day_present_penalty": -10,
    },
    "enable_lunch_break": False,
    "enable_early_start": False,  # Toggle for start constraint
    "enable_early_end": False,  # Toggle for end constraint
    "enable_compact": False,  # Toggle for minimise

    "school_days": [1, 2, 3, 4, 5] # User only wants lessons on mon, tues, thurs, fri
}
