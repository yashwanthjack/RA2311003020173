import urllib.request
import json

# =========================================================
# 1. UPDATE THESE FIELDS WITH YOUR EXACT DETAILS
# =========================================================
EMAIL = "yr2262@srmist.edu.in"  # Must match what you used in the Google Form
NAME = "Yashwanth R"                  # Must match the Google Form
MOBILE_NO = "9047889889"                  # Must match the Google Form
ACCESS_CODE = "QkbpxH"     # Paste from your email
# =========================================================

url = "http://20.207.122.201/evaluation-service/register"
headers = {
    "Content-Type": "application/json"
}

data = {
    "email": EMAIL,
    "name": NAME,
    "mobileNo": MOBILE_NO,
    "githubUsername": "yashwanthjack",
    "rollNo": "RA2311003020173",
    "accessCode": ACCESS_CODE
}

print(f"Sending registration request for rollNo: {data['rollNo']}...")

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode('utf-8'))
        print("\n=== SUCCESS: REGISTRATION COMPLETE ===")
        print("IMPORTANT: Save the following details securely. You CANNOT retrieve them again!")
        print(f"ClientID: {response_data.get('clientID')}")
        print(f"ClientSecret: {response_data.get('clientSecret')}")
        print("======================================\n")
        
        # Save to a local file automatically so you don't lose it
        with open("credentials.json", "w") as f:
            json.dump(response_data, f, indent=4)
        print("Your credentials have also been safely stored in 'credentials.json' in this folder.")
        
except urllib.error.HTTPError as e:
    print(f"\n=== REGISTRATION FAILED ===")
    print(f"HTTP Error: {e.code}")
    error_message = e.read().decode('utf-8')
    print(f"Response: {error_message}")
except Exception as e:
    print(f"\n=== ERROR ===")
    print(str(e))
