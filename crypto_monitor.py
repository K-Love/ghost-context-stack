import krakenex
import pandas as pd
import time

def get_market_data():
    k = krakenex.API()
    
    # Correct way to query public asset pairs
    res = k.query_public('AssetPairs')
    
    if 'error' in res and len(res['error']) > 0:
        print(f"Error: {res['error']}")
        return
    
    pairs = res['result']
    all_pairs = list(pairs.keys())
    
    # Filter for pairs quoted in USD or ZUSD (Kraken's fiat symbol)
    usd_pairs = [p for p in all_pairs if p.endswith('USD') or p.endswith('ZUSD')]
    
    print(f"Total pairs: {len(all_pairs)}")
    print(f"USD pairs: {len(usd_pairs)}")
    print(f"Example USD pairs: {usd_pairs[:10]}")

if __name__ == "__main__":
    get_market_data()
