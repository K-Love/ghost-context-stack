import krakenex
import json
import os
import time

def load_creds():
    creds_path = os.path.expanduser('~/.openclaw/credentials/kraken.json')
    with open(creds_path, 'r') as f:
        return json.load(f)

def get_usd_balance(k):
    res = k.query_private('Balance')
    if 'error' in res and res['error']: return 0.0
    return float(res['result'].get('ZUSD', 0.0))

def run_moonshot_scan():
    creds = load_creds()
    k = krakenex.API(key=creds['api_key'], secret=creds['api_secret'])
    
    # 1. Check Balance and Positions
    balance = get_usd_balance(k)
    print(f"Checking targets... (Current Balance: ${balance:.2f} USD)")
    
    # --- POSITION MONITORING (EXIT LOGIC) ---
    try:
        # Get current holdings
        open_positions = k.query_private('Balance')['result']
        # Filter for assets we actually hold (excluding USD)
        holdings = {k: float(v) for k, v in open_positions.items() if float(v) > 0 and k != 'ZUSD'}
        
        if holdings:
            print(f"Monitoring {len(holdings)} open positions for exits...")
            # Note: Kraken 'Balance' uses 'XETH' etc, Ticker uses 'XETHZUSD'
            # We'll fetch all closed orders once to find our entries
            closed_orders = k.query_private('ClosedOrders', {'trades': True})['result']['closed']
            
            for asset, vol in holdings.items():
                pair = f"{asset}USD"
                try:
                    # Get latest price
                    ticker = k.query_public('Ticker', {'pair': pair})['result'][pair]
                    current_price = float(ticker['c'][0])
                    
                    # Find our entry price for THIS asset in closed orders
                    entry_price = 0.0
                    for oid, odata in closed_orders.items():
                        if odata['descr']['pair'] == pair and odata['descr']['type'] == 'buy':
                            entry_price = float(odata['price'])
                            break # Assume most recent is our base

                    if entry_price > 0:
                        change = (current_price - entry_price) / entry_price
                        print(f"Position {pair}: {change*100:.2f}% (Price: {current_price} | Entry: {entry_price})")
                        
                        # %%% EXIT RULE 1: Initial Investment Pull (100% Gain) %%%
                        if change >= 1.0:
                            print(f"!!! TAKE PROFIT: {pair} hit 100% gain. Selling 50% to secure capital.")
                            k.query_private('AddOrder', {
                                'pair': pair, 'type': 'sell', 'ordertype': 'market', 'volume': str(vol / 2.0)
                            })
                            
                        # %%% EXIT RULE 2: Stop Loss (30% Drop) %%%
                        elif change <= -0.30:
                            print(f"!!! STOP LOSS: {pair} dropped 30%. Cutting loss.")
                            k.query_private('AddOrder', {
                                'pair': pair, 'type': 'sell', 'ordertype': 'market', 'volume': str(vol)
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"Monitoring error: {e}")

    # 2. Scanning for NEW entries
    if balance < 5.0:
        print("Balance too low for new entry. Skipping scan...")
        return

    # Get available pairs
    res = k.query_public('AssetPairs')
    pairs = [p for p in res['result'].keys() if p.endswith('USD')]
    
    # 3. Pull Ticker info in smaller batches
    batch_size = 20
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        try:
            ticker_res = k.query_public('Ticker', {'pair': ','.join(batch)})
            if 'error' in ticker_res and ticker_res['error']:
                print(f"Error fetching batch {i//batch_size}: {ticker_res['error']}")
                continue

            for pair, data in ticker_res['result'].items():
                try:
                    last_price = float(data['c'][0])
                    open_price = float(data['o'])
                    day_gain = (last_price - open_price) / open_price
                    
                    # Target: 10% gain threshold
                    if day_gain >= 0.10:
                        print(f"TARGET MATCH: {pair} | Gain: {day_gain*100:.2f}%")
                        
                        # Execute $10 Market Buy
                        order_params = {
                            'pair': pair,
                            'type': 'buy',
                            'ordertype': 'market',
                            'volume': str(10.0 / last_price)
                        }
                        order_res = k.query_private('AddOrder', order_params)
                        
                        if 'error' in order_res and order_res['error']:
                            print(f"Order failed for {pair}: {order_res['error']}")
                        else:
                            txid = order_res['result'].get('txid', ['unknown'])[0]
                            print(f"EXECUTION: Bought {pair}. TXID: {txid}")
                            return # Exit after one success

                except Exception:
                    continue
            
            time.sleep(0.5) # Anti-throttle

        except Exception as e:
            print(f"Batch {i//batch_size} failed: {e}")
            continue
    
    print("No targets met the criteria.")
    
if __name__ == "__main__":
    run_moonshot_scan()
