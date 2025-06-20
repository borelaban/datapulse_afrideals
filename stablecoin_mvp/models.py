# Mock Database 
# Mock user data
# users = {
#     "254722000000": {"balance": 500, "usdt_balance": 50},  # Test user 1
#     "254722111111": {"balance": 200, "usdt_balance": 20},  # Test user 2
# }

# # Mock transactions
# transactions = []

# models.py
class User:
    def __init__(self, phone, balance, usdt_balance):
        self.phone = phone
        self.balance = balance
        self.usdt_balance = usdt_balance

# Mock data
users = {
    "254722000000": {"balance": 500, "usdt_balance": 50},
    "254722111111": {"balance": 200, "usdt_balance": 20},
}

transactions = []