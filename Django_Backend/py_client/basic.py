import requests

# endpoint = "https://httpbin.org/status/200"
# endpoint = "https://httpbin.org/anything"

# endpoint = "http://127.0.0.1:8000/api/"
endpoint = "http://127.0.0.1:8000/api/getCustomer/"
get_response = requests.get(endpoint, json= {"query": "Hello world"}) #HTTP GET requests
print(get_response.json())

