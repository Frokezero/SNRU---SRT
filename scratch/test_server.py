import urllib.request
import json

def test_server():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:5000/api/events")
        data = response.read().decode('utf-8')
        events = json.loads(data)
        print("Success! Server is up and running. Found events count:", len(events))
    except Exception as e:
        print("Error connecting to server:", e)

if __name__ == "__main__":
    test_server()
