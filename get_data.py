import requests
import copy
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_data(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Assuming the response is in JSON format
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def process_data(data):
    sections = []
    for cl in data["classes"]:
        sections.extend(cl["classSections"])

    times = []
    for sec in sections:
        times.extend(sec["timeLocations"])

    return times

def add_rooms(times, buildings):
    rooms = {building:{} for building in buildings}
    days = {"M":[], "T": [], "W": [], "R": [], "F": []}
    for time in times:
        if time["building"] in buildings:
            rooms[time["building"]][time["room"]] = copy.deepcopy(days)
        else:
            pass

    return rooms

def add_times(times, rooms):
    final_times = copy.deepcopy(rooms)
    for time in times:
        if time["building"] in rooms:
            if time["days"] is None:
                continue
            for day in time["days"].replace(" ", ""):
                final_times[time["building"]][time["room"]][day].append((time["beginTime"], time["endTime"]))

    return final_times

def true_false_array(times):
    pass



def main():
    url = "https://api.ucsb.edu/academics/curriculums/v3/classes/search"
    headers = {"accept": "application/json", "ucsb-api-version": "3.0", "ucsb-api-key": API_KEY}
    params = {"quarter": "20244", "pageNumber": 1, "pageSize": "500", "includeClassSections": "true"}
    data = get_data(url, headers=headers, params=params)
    total = data["total"]
    while total >= 500:
        params["pageNumber"] += 1
        data2 = get_data(url, headers=headers, params=params)
        data["classes"].extend(data2["classes"])
        total -= 500

    times = process_data(data)
    buildings = set([time["building"] for time in times])

    #remove fake buildings
    buildings = [b for b in buildings if b not in ["451", "570", "ON", "NO", "HARDR", "IV", None]]

    #add rooms
    rooms = add_rooms(times, buildings)

    #add times
    final_times = add_times(times, rooms)

    return final_times


# Example usage
if __name__ == "__main__":
    final_times = main()

    build = input("Enter building: ")
    day = input("Enter day: ")

    for room in sorted(list(final_times[build])):
        print(room, final_times[build][room][day])
