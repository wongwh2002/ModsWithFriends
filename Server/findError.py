import json

data = {}
with open('./../Modules/modules.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

errors = []
for mod in data:
    if "moduleCode" not in mod:
        errors.append(mod)

print(errors)