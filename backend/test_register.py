import urllib.request
import json

URL = "http://localhost:5000/api/auth/register"
DATA = {
    "email": "111025015@live.asia.edu.tw",
    "name": "Test User",
    "password": "password123"
}

with open("register_output.txt", "w", encoding="utf-8") as f:
    try:
        req = urllib.request.Request(URL)
        req.add_header('Content-Type', 'application/json')
        jsondata = json.dumps(DATA)
        jsondataasbytes = jsondata.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))
        
        f.write(f"Attempting to register to {URL}...\n")
        with urllib.request.urlopen(req, jsondataasbytes) as response:
            f.write(f"Status Code: {response.status}\n")
            f.write(f"Response: {response.read().decode('utf-8')}\n")
    except urllib.error.HTTPError as e:
        f.write(f"HTTP Error: {e.code}\n")
        f.write(f"Response: {e.read().decode('utf-8')}\n")
    except Exception as e:
        f.write(f"Request failed: {e}\n")
