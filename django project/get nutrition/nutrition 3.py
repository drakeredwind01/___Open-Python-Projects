'''






'''
import requests
import json
import urllib.request

api_key = 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2'
api_key2 = 'Dui2EkKe7wOzTVZOVTVCENxQBchaEqfZmuIneUEA'
food = 'banana'



#     https: // fdc.nal.usda.gov / fdc - app.html  # /?query=banana
url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}'
response = requests.get(url) #old

# request = urllib.request.Request('https://api.nal.usda.gov/fdc/v1/foods/search?api_key=Dui2EkKe7wOzTVZOVTVCENxQBchaEqfZmuIneUEA')
request = urllib.request.Request({url})
request.add_header('content-type', 'application/json')
request.data = b'{"query": "banana", "dataType": ["Foundation"]}'


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
