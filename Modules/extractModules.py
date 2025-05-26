import json

modules = []

with open('modules.json', 'r', encoding='utf-8') as f:
    modules = json.load(f)

def extract_modules():
  module_codes = [module["moduleCode"] for module in modules]
  print(module_codes)

extract_modules()