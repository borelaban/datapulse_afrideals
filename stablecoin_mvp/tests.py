import requests

def test_ussd_flow():
    # Add proper headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    # Initial menu request
    response = requests.post(
        "http://localhost:5000/ussd",
        headers=headers,
        data={
            "phoneNumber": "254722000000",  # Key change from sessionId to phoneNumber
            "text": "",
        }
    )
    print("Menu Response:", response.text)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    # Send USDT request
    print("\nTEST 2: Sending USDT...")
    response = requests.post(
        "http://localhost:5000/ussd",
        headers=headers,
        data={
            "phoneNumber": "254722000000",
            "text": "1 254722111111 10",
        }
    )
    print("Transaction Response:", response.text)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

test_ussd_flow()