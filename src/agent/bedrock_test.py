import requests

import json
 
# Full URL including stage and route

url = "https://wl0nndsqy1.execute-api.us-east-2.amazonaws.com/iiop-demo-mistral-7b-stage/iiop-demo-mistral-7b-url"
 
payload = {

    "prompt": "Write a Python function to give sum of two numbers.",

}
 
headers = {

    "Content-Type": "application/json"

}
 
response = requests.post(url, json=payload, headers=headers)
 
# Print formatted JSON response

print(json.dumps(response.json(), indent=4))

 