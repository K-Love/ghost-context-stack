import krakenex
import json
import os

def test_connection():
    creds_path = os.path.expanduser('~/.openclaw/credentials/kraken.json')
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
            
        k = krakenex.API(key=creds['api_key'], secret=creds['api_secret'])
        
        # Query private balance
        res = k.query_private('Balance')
        
        if 'error' in res and len(res['error']) > 0:
            print(f"Connection Error: {res['error']}")
            return
            
        balance = res['result']
        print("Successfully connected to Kraken!")
        print(f"Current balances: {balance}")
        
    except Exception as e:
        print(f"Script Error: {str(e)}")

if __name__ == "__main__":
    test_connection()
