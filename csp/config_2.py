CONFIG = {
    "semester": 1,
    "users": [
        "A",
        "B",
        "C",
        "D"
    ],
    "A": {
        "modules" : [
            "CG2271",
            "CS2113",
            "ST2334",
            "EE2026",
            "CS1231",
            "ES2631"
        ],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [3, 4, 5],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
            
        },
        "compulsory_classes": {
            "CG2023": {
                "LEC": "04"
            }
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },

    "B": {
        "modules" : [
            'CS3243',
            'EE2211',
            'CS3230',
            # 'CG3207',
            'CS2107',
            'CDE2501',
            # 'MA2108',
        ],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
            "EE2211": ["LEC"],
        },
        "compulsory_classes": {
            # "CS2107": {
            #     "TUT": "07"
            # },
            # "CS3243": {
            #     "TUT": "01"
            # },
            # "EE2211": {
            #     "TUT": "03"
            # },
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },

    "C": {
        "modules" : [
            'CS2040C',
            'CS2107',
            'EE2026',
            'ST2334',
            'ES2631',
        ],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [4],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
        },
        "compulsory_classes": {
            "CG2023": {"LEC": "01",}
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },

    "D": {
        "modules" : [
            "EE2012",
            'EE2211',
            'CS3243',
            'EE3331C',
            'CS2107',
        ],

        "earliest_start": 10 * 60,  # Earliest class start time (10:00 AM in minutes)
        "latest_end": 18 * 60,  # Latest class end time (6:00 PM in minutes)

        "lunch_window": (12 * 60, 14 * 60),  # Preferred lunch window (11AM-1PM)
        "lunch_duration": 60,  # Lunch break duration (60 minutes)
        "days_without_lunch": [4],  # Days where lunch break isn't required
        "days_without_class": [],
        "optional_classes": {  # Classes that can be optionally included
        },
        "compulsory_classes": {
            # "CS2107": {
            #     "TUT": "01"
            # },
        },
        "enable_lunch_break": False,  # Whether to enforce lunch breaks
        "enable_late_start": False,  # Whether to enforce earliest start time
        "enable_early_end": False,  # Whether to enforce latest end time
        "enable_weights": True,  # Whether to minimize day length
    },

    "shared": {
        "CS2107": [["B", "D", "C"]],
        "CS3243": [["B", "D"]],
        "EE2211": [["B", "D"]],
        "EE2026": [["A", "C"]]
        # "CS2107": [["B"]],
        # "CS3243": [["B"]],
        # "EE2211": [["B"]],
    },
}