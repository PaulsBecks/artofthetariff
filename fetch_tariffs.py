import json
import re
import requests

from pycountry import countries
 
# load current tariffs from https://hts.usitc.gov
request = requests.get("https://hts.usitc.gov/reststop/exportList?from=9903.01.00&to=9903.01.99.99&format=JSON&styles=true")
if request.status_code != 200:
    print(request.status_code)
    raise Exception("Failed to fetch tariffs")
notes = request.json()

# local copy
# with open("tariffs.json", "r") as f:
#     notes = json.load(f)

with open("eu_country_codes.json", "r") as f:
    eu_country_codes = json.load(f)
    
with open("non_mfn_country_codes.json", "r") as f:
    non_mfn_country_codes = json.load(f)

def get_value_from_description(description):
    """
    Extracts the value from the description string.
    """
    value = re.findall(r'\d+', description)
    print(value, description)
    if len(value) == 1:
        return value[0]
    return None


tariffs = {}
# Iterate through the notes and extract the tariff values
for note in notes:
    print(f"Processing: {note["htsno"]}")
    description = note["description"]
    # If the description contains "any country" or "European Union", set the tariff for all countries
    if "any country" in description:
        if value := get_value_from_description(note["general"]):
            for country in countries:
                # Only set the tariff for countries that are not in the non-MFN list
                # and are not the USA
                if country.alpha_3 not in non_mfn_country_codes and country.alpha_3 not in ["USA"]:                
                    tariffs[country.alpha_3] = value
        # TODO: check if a tariff value is set in the "other" field and add it to the non_mfn_country codes
        continue
    if "European Union" in description:
        if value := get_value_from_description(note["general"]):
            for code in eu_country_codes:
                tariffs[code] = value 
    # Check if the description contains any of the country names
    for country in countries:
        try:
            common_name = country.common_name 
        except AttributeError:
            common_name = country.name
        try:
            official_name = country.official_name
        except AttributeError:
            official_name = country.name
        if country.name in description or official_name in description or common_name in description:
            if value := get_value_from_description(note["general"]):
                tariffs[country.alpha_3] = value

json.dumps(tariffs, indent=4)
open("dist/data.json", "w").write(json.dumps(tariffs, indent=4))
