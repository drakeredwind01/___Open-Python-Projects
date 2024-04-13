'''

2023.05.11.14.14.53.660
nutrition with pandas 4.py
    added 
    food_list = []
    food_list.append('apple')
    food_list.append('broccoli')
    food_list.append('chicken')
            name = nutrient['nutrientName']
            value = nutrient['value']
            unit = nutrient['unitName']

replaced
    for result in data['foods'][:20]:
    for
    for result in data['foods']:



'''

import pandas as pd
import requests

api_key = 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2'
food_list = []

food_list.append('Apples')
food_list.append('Bananas')
food_list.append('Oranges')

url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food_list}'
response = requests.get(url)

if response.status_code == 200: #means that the request was successful
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
