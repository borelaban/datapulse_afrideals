from flask import Flask, request
from flask import make_response
import africastalking
from config import AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
csrf = CSRFProtect(app)  # Still initialize but disabled 


# Initialize Africa's Talking
africastalking.initialize(AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY)
sms = africastalking.SMS

# Initialize with test users
users = {
    "254722000000": {"balance": 500, "usdt_balance": 50},
    "254722111111": {"balance": 200, "usdt_balance": 20},
}

# @app.route('/')
# def home():
#     return "USDT Wallet MVP is running! Use POST /ussd for USSD calls."

print(f"\n=== INCOMING REQUEST ===")
print(f"Headers: {request.headers}")
print(f"Form Data: {request.form}")
print(f"Values: {request.values}")
print(f"Args: {request.args}")

@app.route('/ussd', methods=['POST'])
def ussd():
    phone_number = request.values.get("phoneNumber")
    text = request.values.get("text", "").strip()

    print(f"Received request - Phone: {phone_number}, Text: '{text}'")  # Debug log

    if not phone_number:
        return make_response("END Error: Missing phone number", 200)

    # Initialize user if not exists
    if phone_number not in users:
        users[phone_number] = {"balance": 0, "usdt_balance": 0}

    if text == "":
        return make_response("CON Welcome to USDT Wallet:\n1. Send USDT\n2. Check Balance\n3. Cash Out")
    elif text == "1":
        return make_response("CON Enter recipient phone and amount (e.g., 0722111222 10)")
    elif text.startswith("1 "):
        try:
            _, recipient, amount = text.split()
            amount = float(amount)
            if recipient not in users:
                return make_response("END Error: Recipient not found")
            if amount > users[phone_number]["usdt_balance"]:
                return make_response("END Error: Insufficient balance")
            
            users[phone_number]["usdt_balance"] -= amount
            users[recipient]["usdt_balance"] += amount
            return make_response(f"END Sent {amount} USDT to {recipient}")
        except:
            return make_response("END Error: Invalid format. Use: 1 [phone] [amount]")
    elif text == "2":
        return make_response(f"END Your balance: {users[phone_number]['usdt_balance']} USDT")
    elif text == "3":
        return make_response("END Visit agent to cash out USDT.")
    else:
        return make_response("END Invalid option")

if __name__ == "__main__":
    app.run(debug=True)