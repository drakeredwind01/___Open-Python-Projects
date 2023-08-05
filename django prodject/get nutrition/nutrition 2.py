'''






'''

import requests

api_key = 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2'
food = 'banana'

#     https: // fdc.nal.usda.gov / fdc - app.html  # /?query=banana
url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food}'
response = requests.get(url)

print(food)
if response.status_code == 200:
    data = response.json()
    for result in data['foods']:
        nutrients = result['foodNutrients']
        for nutrient in nutrients:
            name = nutrient['nutrientName']
            value = nutrient['value']
            unit = nutrient['unitName']
            print(f'{name}, {value}, {unit}')
else:
    print('Error retrieving data')
