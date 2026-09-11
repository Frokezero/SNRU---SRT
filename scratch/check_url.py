import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    with urllib.request.urlopen("http://127.0.0.1:5000/api/majors") as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Successfully queried http://127.0.0.1:5000/api/majors!")
        print("Response data:")
        print(data)
except Exception as e:
    print(f"Error querying localhost: {e}")
