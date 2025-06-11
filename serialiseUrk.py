from urllib.parse import parse_qs, urlparse
from pprint import pprint

def serialise_timetable(semester):
    
    initial_url = "https://nusmods.com/timetable/sem-2/share?"
