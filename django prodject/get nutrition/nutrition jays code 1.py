
'''
to scs
'''
import json
import urllib.request

request = urllib.request.Request('https://api.nal.usda.gov/fdc/v1/foods/search?api_key=Dui2EkKe7wOzTVZOVTVCENxQBchaEqfZmuIneUEA')
request.add_header('content-type', 'application/json')
request.data = b'{"query": "banana", "dataType": ["Foundation"]}'

r = urllib.request.urlopen(request)
response = json.loads(r.read().decode('utf-8'))

for food in response['foods']:
    print(food['fdcId'], food['description'])
