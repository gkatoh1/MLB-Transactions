import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

# URL for MLB transactions
MLB_TRANSACTIONS_URL = "https://www.mlb.com/transactions"

def get_transactions():
    """Scrape MLB transactions and save them to a JSON file"""
    transactions = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(MLB_TRANSACTIONS_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all transaction descriptions
        transaction_descriptions = soup.select('td.description')
        
        for desc_elem in transaction_descriptions:
            try:
                # Get date
                date_elem = desc_elem.select_one('.mobile-date')
                transaction_date = None
                if date_elem:
                    date_text = date_elem.text.strip()
                    # Parse date in format MM/DD/YY
                    transaction_date = datetime.datetime.strptime(date_text, '%m/%d/%y').date()
                else:
                    # If no date found, skip this transaction
                    continue
                
                # Get team name
                team_elem = desc_elem.select_one('.club-link')
                team = team_elem.text.strip() if team_elem else "Unknown Team"
                
                # Get player name
                player_elem = desc_elem.select_one('.player-link')
                player = player_elem.text.strip() if player_elem else "Unknown Player"
                
                # Get the full text content
                full_text = desc_elem.get_text(strip=True)
                
                # Remove the date part
                if date_elem:
                    full_text = full_text.replace(date_elem.text.strip(), "").strip()
                
                # The details are the complete text, which includes the transaction type and additional info
                details = full_text
                
                transactions.append({
                    'date': transaction_date.isoformat(),
                    'team': team,
                    'details': details,
                    'player': player
                })
                
            except Exception as e:
                print(f"Error processing transaction item: {e}")
                continue
    except Exception as e:
        print(f"Error fetching MLB transactions: {e}")
    
    print(f"Found {len(transactions)} transactions")
    
    # Add timestamp when the data was collected
    data = {
        'last_updated': datetime.datetime.now().isoformat(),
        'transactions': transactions
    }
    
    # Save to JSON file
    with open('transactions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_transactions()