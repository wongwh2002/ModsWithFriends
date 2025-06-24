class Timetable:
    def __init__(self, semester):
        self.classes = {}
        self.semester = semester
    def add_class(self, module_code: str, lesson_type: str, class_no: str):
        if not module_code in self.classes:
            self.classes[module_code] = {
                lesson_type: class_no
            } 
        elif not lesson_type in self.classes[module_code]:
            self.classes[module_code][lesson_type] = class_no
        else:
            raise Exception(f"2 {lesson_type} selected for {module_code}")
    
    def get_url(self):
        url = "https://nusmods.com/timetable/sem-2/share?" if self.semester == 2 else "https://nusmods.com/timetable/sem-1/share?" 
        first_mod = True
        for module_code in self.classes:
            params = f"{module_code}=" if first_mod else f"&{module_code}="
            first = True
            for lesson_type, class_no in self.classes[module_code].items():
                if not first:
                    params += ","
                params += f"{lesson_type}:{class_no}"
                first = False
            url += params
            first_mod = False
        return url