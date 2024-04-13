'''






'''

import pandas as pd
import requests

api_key = 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2'
food = 'banana'

url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    food_nutrients = []
    for result in data['foods'][:20]:
        nutrients = result['foodNutrients']
        for nutrient in nutrients:
            name = nutrient['nutrientName']
            value = nutrient['value']
            unit = nutrient['unitName']
            food_nutrients.append([name, value, unit])
    df = pd.DataFrame(food_nutrients, columns=['Nutrient Name', 'Value', 'Unit'])
    df.to_csv('banana_nutrition.csv', index=False)
    print('Data saved to banana_nutrition.csv')
else:
    print('Error retrieving data')
