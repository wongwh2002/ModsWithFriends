from timetable import Timetable

class Solution:
    def __init__(self, users: list[str], sem):
        self.timetables: dict[str, Timetable] = {}
        for user in users:
            self.timetables[user] = Timetable(sem)
    
    def add_class_for_user(self, user, mod, lesson_type, class_no):
        self.timetables[user].add_class(mod, lesson_type, class_no)

    def __str__(self):
        string = ""
        for user, timetable in self.timetables.items():
            string += f"{user}: {timetable.get_url()}\n"
        return string

