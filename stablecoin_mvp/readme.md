A step-by-step guide to building, testing, and simulating your USDT wallet MVP for Kibera SMEs from the ground up. We'll use Python (Flask) for the backend, Africa's Talking for USSD, and a mock database for testing.

# A. System Architecture

1. USSD/WhatsApp Interface → 
2. Python Flask Backend (Wallet Logic) → 
3. Mock Database (Dummy Users/Transactions) → 
4. Simulation Lab (Test Flows)

# B. Setup Backend (Python Flask)

```pip install flask africastalking python-dotenv``

/stablecoin_mvp
  ├── ussdt_wallet_app.py          # Flask backend
  ├── config.py       # API keys, settings
  ├── models.py       # Mock database
  ├── tests.py        # Test scripts
  ├── readme.md.   # Read me markdown file, documentation  
  ├── requirements.txt       # requirement file
  └── .env            # Environment variables


