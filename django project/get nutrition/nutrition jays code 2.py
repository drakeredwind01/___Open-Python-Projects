import pandas as pd
import json
import urllib.request

request = urllib.request.Request('https://api.nal.usda.gov/fdc/v1/foods/search?api_key=Dui2EkKe7wOzTVZOVTVCENxQBchaEqfZmuIneUEA')
request.add_header('content-type', 'application/json')
request.data = b'{"query": "banana", "dataType": ["Foundation"]}'

r = urllib.request.urlopen(request)
response = json.loads(r.read().decode('utf-8'))
food_df = pd.DataFrame.from_dict(response['foods'])
food_df
banana_nutrients = pd.DataFrame.from_records(food_df['foodNutrients']).transpose()
banana_nutrients
banana_nutrients[1].apply(pd.Series)
