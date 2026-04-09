import requests
import json

r = requests.get('http://127.0.0.1:8000/api/sections/sample/')
if r.ok:
    data = r.json()
    print("Response keys:", list(data.keys()))
    
    # Check transformed_data
    if 'transformed_data' in data and data['transformed_data']:
        print(f"\ntransformed_data type: {type(data['transformed_data'])}")
        print(f"transformed_data: {json.dumps(data['transformed_data'][:2], indent=2) if isinstance(data['transformed_data'], list) else list(data['transformed_data'].keys())[:5]}")
    
    # Check _performance
    if '_performance' in data and data['_performance']:
        print(f"\n_performance type: {type(data['_performance'])}")
        print(f"_performance keys: {list(data['_performance'].keys()) if isinstance(data['_performance'], dict) else 'list'}")
        if isinstance(data['_performance'], list) and data['_performance']:
            print(f"First _performance item: {json.dumps(data['_performance'][0], indent=2)}")

