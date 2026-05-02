import urllib.request
import json
import os

def get_access_token():
    # Load credentials from the registration step
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found. Run register.py first.")
        return

    with open('credentials.json', 'r') as f:
        creds = json.load(f)

    url = "http://20.207.122.201/evaluation-service/auth"
    headers = {
        "Content-Type": "application/json"
    }
    
    # The Auth API requires the same fields used in registration + clientID/Secret
    data = {
        "email": creds.get("email"),
        "name": creds.get("name"),
        "rollNo": creds.get("rollNo"),
        "accessCode": creds.get("accessCode"),
        "clientID": creds.get("clientID"),
        "clientSecret": creds.get("clientSecret")
    }

    print("Requesting access token from test server...")

    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode('utf-8'))
            
            # Save the token for future use
            with open('token.json', 'w') as f:
                json.dump(token_data, f, indent=4)
            
            print("\n=== AUTHENTICATION SUCCESS ===")
            print(f"Token Type: {token_data.get('token_type')}")
            print(f"Expires In: {token_data.get('expires_in')}")
            print("Access token saved to 'token.json'.")
            print("==============================\n")

    except urllib.error.HTTPError as e:
        print(f"\n=== AUTHENTICATION FAILED ===")
        print(f"HTTP Status: {e.code}")
        print(f"Details: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(str(e))

if __name__ == "__main__":
    get_access_token()
