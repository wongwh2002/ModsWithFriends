import requests
from pprint import pprint

def get_module_info(year = 2023, module_code = "CG2023"):
    url = f"https://api.nusmods.com/v2/{year}-{year+1}/modules/{module_code}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        # pprint.pprint(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__=="__main__":
    # Call the function
    module_data = get_module_info(module_code="CS1010")
    semester_data = module_data['semesterData']

    # Print the semester data
    pprint(module_data)