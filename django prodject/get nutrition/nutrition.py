import requests

api_key = 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2'
food = 'banana'

curl -H 'wkFMcAoVtbSF0H6WcGcC2gpscOmLKsvWFcF2Kxg2: DEMO_KEY' 'https://developer.nrel.gov/api/alt-fuel-stations/v1.json?limit=1'
url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food}'
response = requests.get(url)

if response.ok:
    data = response.json()
    if data['totalHits'] > 0:
        first_result = data['foods'][0]
        print(f"Name: {first_result['description']}")
        print(f"Calories: {first_result['foodNutrients'][1]['value']} {first_result['foodNutrients'][1]['unitName']}")
        print(f"Protein: {first_result['foodNutrients'][3]['value']} {first_result['foodNutrients'][3]['unitName']}")
        print(f"Fat: {first_result['foodNutrients'][4]['value']} {first_result['foodNutrients'][4]['unitName']}")
        print(f"Carbohydrates: {first_result['foodNutrients'][6]['value']} {first_result['foodNutrients'][6]['unitName']}")
    else:
        print(f"No results found for {food}.")
else:
    print("An error occurred while making the request.")
