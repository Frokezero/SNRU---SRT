import urllib.request
import urllib.error
import json

url = 'http://127.0.0.1:5000/api/login'
data = {
    'username': '69102101101',
    'password': '101'
}

req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

print("Attempting login via urllib...")
try:
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        body = response.read().decode('utf-8')
        print(f"Status Code: {status_code}")
        print(f"Response: {body}")
except urllib.error.HTTPError as e:
    status_code = e.code
    body = e.read().decode('utf-8')
    print(f"HTTPError Status Code: {status_code}")
    print(f"HTTPError Response: {body}")
except Exception as e:
    print(f"Error connecting: {e}")
