# bluejays_transactions.py
import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import logging
import sys
import ssl
from typing import List, Dict, Any, Optional, Tuple

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_FILE = "last_check.json"
MLB_TRANSACTIONS_URL = "https://www.mlb.com/transactions"
TEAM_NAME = "Toronto Blue Jays"
TEAM_ABBREVIATION = "TOR"

# Email configuration - IMPORTANT: Update these with your email credentials
EMAIL_TO = "gkatoh@ymail.com"
EMAIL_FROM = "gkatoh@ymail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")  # Get from environment variable for security
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 465  # Change to 465 for Yahoo SSL
EMAIL_ENABLED = True

# Team name mapping (common abbreviations and full names)
TEAM_MAPPING = {
    'TOR': 'Toronto Blue Jays',
    'NYY': 'New York Yankees',
    'BOS': 'Boston Red Sox',
    'TBR': 'Tampa Bay Rays',
    'BAL': 'Baltimore Orioles',
    'DET': 'Detroit Tigers',
    'CLE': 'Cleveland Guardians',
    'CHW': 'Chicago White Sox',
    'KCR': 'Kansas City Royals',
    'MIN': 'Minnesota Twins',
    'HOU': 'Houston Astros',
    'LAA': 'Los Angeles Angels',
    'OAK': 'Oakland Athletics',
    'SEA': 'Seattle Mariners',
    'TEX': 'Texas Rangers',
    'ATL': 'Atlanta Braves',
    'MIA': 'Miami Marlins',
    'NYM': 'New York Mets',
    'PHI': 'Philadelphia Phillies',
    'WSN': 'Washington Nationals',
    'CHC': 'Chicago Cubs',
    'CIN': 'Cincinnati Reds',
    'MIL': 'Milwaukee Brewers',
    'PIT': 'Pittsburgh Pirates',
    'STL': 'St. Louis Cardinals',
    'ARI': 'Arizona Diamondbacks',
    'COL': 'Colorado Rockies',
    'LAD': 'Los Angeles Dodgers',
    'SDP': 'San Diego Padres',
    'SFG': 'San Francisco Giants',
    # Alternative names
    'TB': 'Tampa Bay Rays',
    'KC': 'Kansas City Royals',
    'CWS': 'Chicago White Sox',
    'SD': 'San Diego Padres',
    'SF': 'San Francisco Giants',
    'WSH': 'Washington Nationals',
    'ATH': 'Oakland Athletics',  # This appears in the schedule
}

# Full Toronto Blue Jays 2025 season schedule
# Format: (date, opponent, is_home_game)
BLUE_JAYS_SCHEDULE = [
    ("Thursday, Mar 27", "BAL", True),
    ("Friday, Mar 28", "BAL", True),
    ("Saturday, Mar 29", "BAL", True),
    ("Sunday, Mar 30", "BAL", True),
    ("Monday, Mar 31", "WSN", True),
    ("Tuesday, Apr 1", "WSN", True),
    ("Wednesday, Apr 2", "WSN", True),
    ("Friday, Apr 4", "NYM", False),
    ("Saturday, Apr 5", "NYM", False),
    ("Sunday, Apr 6", "NYM", False),
    ("Monday, Apr 7", "BOS", False),
    ("Tuesday, Apr 8", "BOS", False),
    ("Wednesday, Apr 9", "BOS", False),
    ("Thursday, Apr 10", "BOS", False),
    ("Saturday, Apr 12", "BAL", False),
    ("Sunday, Apr 13", "BAL", False),
    ("Monday, Apr 14", "ATL", True),
    ("Tuesday, Apr 15", "ATL", True),
    ("Wednesday, Apr 16", "ATL", True),
    ("Friday, Apr 18", "SEA", True),
    ("Saturday, Apr 19", "SEA", True),
    ("Sunday, Apr 20", "SEA", True),
    ("Monday, Apr 21", "HOU", False),
    ("Tuesday, Apr 22", "HOU", False),
    ("Wednesday, Apr 23", "HOU", False),
    ("Friday, Apr 25", "NYY", False),
    ("Saturday, Apr 26", "NYY", False),
    ("Sunday, Apr 27", "NYY", False),
    ("Tuesday, Apr 29", "BOS", True),
    ("Wednesday, Apr 30", "BOS", True),
    ("Thursday, May 1", "BOS", True),
    ("Friday, May 2", "CLE", True),
    ("Saturday, May 3", "CLE", True),
    ("Sunday, May 4", "CLE", True),
    ("Tuesday, May 6", "LAA", False),
    ("Wednesday, May 7", "LAA", False),
    ("Thursday, May 8", "LAA", False),
    ("Friday, May 9", "SEA", False),
    ("Saturday, May 10", "SEA", False),
    ("Sunday, May 11", "SEA", False),
    ("Tuesday, May 13", "TBR", True),
    ("Wednesday, May 14", "TBR", True),
    ("Thursday, May 15", "TBR", True),
    ("Friday, May 16", "DET", True),
    ("Saturday, May 17", "DET", True),
    ("Sunday, May 18", "DET", True),
    ("Tuesday, May 20", "SDP", True),
    ("Wednesday, May 21", "SDP", True),
    ("Thursday, May 22", "SDP", True),
    ("Friday, May 23", "TBR", False),
    ("Saturday, May 24", "TBR", False),
    ("Sunday, May 25", "TBR", False),
    ("Monday, May 26", "TEX", False),
    ("Tuesday, May 27", "TEX", False),
    ("Wednesday, May 28", "TEX", False),
    ("Thursday, May 29", "ATH", True),
    ("Friday, May 30", "ATH", True),
    ("Saturday, May 31", "ATH", True),
    ("Sunday, Jun 1", "ATH", True),
    ("Tuesday, Jun 3", "PHI", True),
    ("Wednesday, Jun 4", "PHI", True),
    ("Thursday, Jun 5", "PHI", True),
    ("Friday, Jun 6", "MIN", False),
    ("Saturday, Jun 7", "MIN", False),
    ("Sunday, Jun 8", "MIN", False),
    ("Monday, Jun 9", "STL", False),
    ("Tuesday, Jun 10", "STL", False),
    ("Wednesday, Jun 11", "STL", False),
    ("Friday, Jun 13", "PHI", False),
    ("Saturday, Jun 14", "PHI", False),
    ("Sunday, Jun 15", "PHI", False),
    ("Tuesday, Jun 17", "ARI", True),
    ("Wednesday, Jun 18", "ARI", True),
    ("Thursday, Jun 19", "ARI", True),
    ("Friday, Jun 20", "CHW", True),
    ("Saturday, Jun 21", "CHW", True),
    ("Sunday, Jun 22", "CHW", True),
    ("Tuesday, Jun 24", "CLE", False),
    ("Wednesday, Jun 25", "CLE", False),
    ("Thursday, Jun 26", "CLE", False),
    ("Friday, Jun 27", "BOS", False),
    ("Saturday, Jun 28", "BOS", False),
    ("Sunday, Jun 29", "BOS", False),
    ("Monday, Jun 30", "NYY", True),
    ("Tuesday, Jul 1", "NYY", True),
    ("Wednesday, Jul 2", "NYY", True),
    ("Thursday, Jul 3", "NYY", True),
    ("Friday, Jul 4", "LAA", True),
    ("Saturday, Jul 5", "LAA", True),
    ("Sunday, Jul 6", "LAA", True),
    ("Monday, Jul 7", "CHW", False),
    ("Tuesday, Jul 8", "CHW", False),
    ("Wednesday, Jul 9", "CHW", False),
    ("Friday, Jul 11", "ATH", False),
    ("Saturday, Jul 12", "ATH", False),
    ("Sunday, Jul 13", "ATH", False),
    ("Friday, Jul 18", "SFG", True),
    ("Saturday, Jul 19", "SFG", True),
    ("Sunday, Jul 20", "SFG", True),
    ("Monday, Jul 21", "NYY", True),
    ("Tuesday, Jul 22", "NYY", True),
    ("Wednesday, Jul 23", "NYY", True),
    ("Thursday, Jul 24", "DET", False),
    ("Friday, Jul 25", "DET", False),
    ("Saturday, Jul 26", "DET", False),
    ("Sunday, Jul 27", "DET", False),
    ("Monday, Jul 28", "BAL", False),
    ("Tuesday, Jul 29", "BAL", False),
    ("Wednesday, Jul 30", "BAL", False),
    ("Friday, Aug 1", "KCR", True),
    ("Saturday, Aug 2", "KCR", True),
    ("Sunday, Aug 3", "KCR", True),
    ("Monday, Aug 4", "COL", False),
    ("Tuesday, Aug 5", "COL", False),
    ("Wednesday, Aug 6", "COL", False),
    ("Friday, Aug 8", "LAD", False),
    ("Saturday, Aug 9", "LAD", False),
    ("Sunday, Aug 10", "LAD", False),
    ("Tuesday, Aug 12", "CHC", True),
    ("Wednesday, Aug 13", "CHC", True),
    ("Thursday, Aug 14", "CHC", True),
    ("Friday, Aug 15", "TEX", True),
    ("Saturday, Aug 16", "TEX", True),
    ("Sunday, Aug 17", "TEX", True),
    ("Monday, Aug 18", "PIT", False),
    ("Tuesday, Aug 19", "PIT", False),
    ("Wednesday, Aug 20", "PIT", False),
    ("Friday, Aug 22", "MIA", False),
    ("Saturday, Aug 23", "MIA", False),
    ("Sunday, Aug 24", "MIA", False),
    ("Monday, Aug 25", "MIN", True),
    ("Tuesday, Aug 26", "MIN", True),
    ("Wednesday, Aug 27", "MIN", True),
    ("Friday, Aug 29", "MIL", True),
    ("Saturday, Aug 30", "MIL", True),
    ("Sunday, Aug 31", "MIL", True),
    ("Monday, Sep 1", "CIN", False),
    ("Tuesday, Sep 2", "CIN", False),
    ("Wednesday, Sep 3", "CIN", False),
    ("Friday, Sep 5", "NYY", False),
    ("Saturday, Sep 6", "NYY", False),
    ("Sunday, Sep 7", "NYY", False),
    ("Tuesday, Sep 9", "HOU", True),
    ("Wednesday, Sep 10", "HOU", True),
    ("Thursday, Sep 11", "HOU", True),
    ("Friday, Sep 12", "BAL", True),
    ("Saturday, Sep 13", "BAL", True),
    ("Sunday, Sep 14", "BAL", True),
    ("Monday, Sep 15", "TBR", False),
    ("Tuesday, Sep 16", "TBR", False),
    ("Wednesday, Sep 17", "TBR", False),
    ("Thursday, Sep 18", "TBR", False),
    ("Friday, Sep 19", "KCR", False),
    ("Saturday, Sep 20", "KCR", False),
    ("Sunday, Sep 21", "KCR", False),
    ("Tuesday, Sep 23", "BOS", True),
    ("Wednesday, Sep 24", "BOS", True),
    ("Thursday, Sep 25", "BOS", True),
    ("Friday, Sep 26", "TBR", True),
    ("Saturday, Sep 27", "TBR", True),
    ("Sunday, Sep 28", "TBR", True),
]

def parse_date(date_str: str) -> Optional[datetime.date]:
    """
    Parse date from the schedule
    Example: "Sunday, Apr 20"
    """
    try:
        # Since we know the format is consistent, we can extract parts directly
        parts = date_str.split(", ")
        day_of_week = parts[0]
        month_day = parts[1]
        
        # Parse month and day
        month_str, day_str = month_day.split(" ")
        
        # Convert month name to number
        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        month_num = month_map.get(month_str, None)
        
        if not month_num:
            return None
            
        # Assume current year (2025)
        year = 2025
        
        # Create date object
        return datetime.date(year, month_num, int(day_str))
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None

def get_blue_jays_schedule() -> List[str]:
    """
    Get the Toronto Blue Jays schedule for the next 5 days based on the hardcoded schedule
    Returns a list of opponent team names and abbreviations
    """
    today = datetime.datetime.now(pytz.timezone('America/Toronto')).date()
    logger.info(f"Current date: {today}")
    
    upcoming_opponents = []
    
    for game_date_str, opponent, is_home in BLUE_JAYS_SCHEDULE:
        # Parse the date
        game_date = parse_date(game_date_str)
        
        if not game_date:
            continue
            
        # Check if the game is within the next 5 days
        days_difference = (game_date - today).days
        if 0 <= days_difference <= 5:
            upcoming_opponents.append(opponent)
            
            # Add full team name if available
            if opponent in TEAM_MAPPING:
                upcoming_opponents.append(TEAM_MAPPING[opponent])
    
    # Remove duplicates
    unique_opponents = list(set(upcoming_opponents))
    logger.info(f"Found upcoming opponents for the next 5 days: {unique_opponents}")
    
    # If we somehow didn't find any opponents, use AL East rivals as fallback
    if not unique_opponents:
        logger.warning("No opponents found in schedule, using AL East rivals as fallback")
        unique_opponents = ["NYY", "BOS", "TBR", "BAL", "New York Yankees", "Boston Red Sox", "Tampa Bay Rays", "Baltimore Orioles"]
    
    return unique_opponents

def get_transactions(since_date: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
    """
    Get MLB transactions since the specified date
    If no date is provided, get transactions from today
    Returns a list of transaction objects
    """
    if since_date:
        logger.info(f"Getting transactions since {since_date}")
    else:
        # If no date specified, get today's transactions
        since_date = datetime.datetime.now().date()
        logger.info(f"Getting today's transactions ({since_date})")
    
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
                
                if transaction_date < since_date:
                    # Skip transactions before the specified date
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
                
                logger.debug(f"Processed transaction: {transaction_date} - {team} - {details}")
                
            except Exception as e:
                logger.error(f"Error processing transaction item: {e}")
                logger.error(f"HTML content: {desc_elem}")
                continue
    except Exception as e:
        logger.error(f"Error fetching MLB transactions: {e}")
    
    logger.info(f"Found {len(transactions)} transactions since {since_date}")
    return transactions

def parse_transaction_date(date_text: str) -> Optional[datetime.date]:
    """
    Parse transaction date from MLB format to date object
    """
    try:
        # Example formats: "April 15, 2023" or "April 15"
        if "," in date_text:
            # Full date with year
            return datetime.datetime.strptime(date_text, '%B %d, %Y').date()
        else:
            # Date without year, add current year
            current_year = datetime.datetime.now().year
            return datetime.datetime.strptime(f"{date_text}, {current_year}", '%B %d, %Y').date()
    except ValueError as e:
        logger.error(f"Error parsing transaction date '{date_text}': {e}")
        return None

def get_last_check_time() -> datetime.datetime:
    """
    Get the timestamp of the last transaction check
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return datetime.datetime.fromisoformat(data.get('last_check', '2000-01-01T00:00:00'))
        else:
            # If no previous check, return a date far in the past
            logger.info("No previous check found, using default date")
            return datetime.datetime.fromisoformat('2000-01-01T00:00:00')
    except Exception as e:
        logger.error(f"Error getting last check time: {e}")
        return datetime.datetime.fromisoformat('2000-01-01T00:00:00')

def update_last_check_time() -> None:
    """
    Update the timestamp of the last transaction check
    """
    try:
        current_time = datetime.datetime.now().isoformat()
        data = {'last_check': current_time}
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
            
        logger.info(f"Updated last check time to {current_time}")
    except Exception as e:
        logger.error(f"Error updating last check time: {e}")

def filter_relevant_transactions(transactions: List[Dict[str, Any]], upcoming_opponents: List[str]) -> List[Dict[str, Any]]:
    """
    Filter transactions to include only upcoming opponents (exclude Blue Jays)
    """
    # Only include upcoming opponents, explicitly exclude Blue Jays
    relevant_teams = upcoming_opponents
    relevant_transactions = []
    
    for transaction in transactions:
        team = transaction['team']
        # Exclude Blue Jays transactions
        if TEAM_NAME in team or TEAM_ABBREVIATION in team:
            continue
            
        # Include only upcoming opponents
        if any(re.search(f"\\b{re.escape(team_name)}\\b", team, re.IGNORECASE) for team_name in relevant_teams):
            relevant_transactions.append(transaction)
    
    logger.info(f"Filtered to {len(relevant_transactions)} relevant transactions from opponents")
    return relevant_transactions

def format_transaction_details(details: str) -> str:
    """
    Format transaction details for improved readability
    """
    # Add space between team name and action
    details = re.sub(r'(\w)(optioned|selected|recalled|placed|designated|reinstated|released|signed|traded|claimed)', 
                    r'\1 \2', details)
    
    # Add space after position abbreviations
    details = re.sub(r'(RHP|LHP|CF|RF|LF|SS|2B|3B|1B|C|DH)(\w)', r'\1 \2', details)
    
    # Ensure space after player name
    details = re.sub(r'([A-Z][a-z]+)([A-Z][a-z]+)(\w)', r'\1 \2 \3', details)
    
    return details

def generate_report(transactions: List[Dict[str, Any]], upcoming_opponents: List[str]) -> str:
    """
    Generate a report of relevant transactions (only opposing teams)
    """
    if not transactions:
        return f"No new transactions for upcoming opponents ({', '.join(upcoming_opponents)}) since last check."
    
    # Changed the heading to be more concise
    report = f"Transaction updates since last check:\n\n"
    
    # Group transactions by team
    team_transactions = {}
    for transaction in transactions:
        team = transaction['team']
        if team not in team_transactions:
            team_transactions[team] = []
        team_transactions[team].append(transaction)
    
    # Build report
    for team, team_trans in sorted(team_transactions.items()):
        report += f"{team}:\n"
        # Sort by date, newest first
        sorted_trans = sorted(team_trans, key=lambda x: x['date'], reverse=True)
        for t in sorted_trans:
            # Format details for readability
            details = format_transaction_details(t['details'])
            report += f"  {t['date']}: {details}\n"
        report += "\n"
    
    return report

def generate_email_subject(relevant_transactions: List[Dict[str, Any]]) -> str:
    """
    Generate email subject with team names that had updates
    Format: "[Team1, Team2, ...] TRANSACTION UPDATE"
    """
    # Get unique team names from transactions
    teams_with_updates = set()
    for transaction in relevant_transactions:
        teams_with_updates.add(transaction['team'])
    
    # Sort team names alphabetically and limit to first 3 teams if there are many
    sorted_teams = sorted(teams_with_updates)
    if len(sorted_teams) > 3:
        teams_display = sorted_teams[:3]
        teams_str = ", ".join(teams_display) + f" +{len(sorted_teams)-3} more"
    else:
        teams_str = ", ".join(sorted_teams)
    
    if sorted_teams:
        return f"[{teams_str}] TRANSACTION UPDATE"
    else:
        return "TRANSACTION UPDATE"

def send_email(subject: str, body: str) -> bool:
    """
    Send an email notification using Yahoo Mail with SSL
    Returns True if successful, False otherwise
    """
    if not EMAIL_ENABLED:
        logger.info("Email notifications are disabled")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SSL context for secure connection
        context = ssl.create_default_context()
        
        # Use SMTP_SSL for Yahoo Mail
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            # Authenticate with Yahoo
            if EMAIL_PASSWORD and EMAIL_PASSWORD != "your-password":
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
            else:
                print("\n*** ERROR: You need to set your email password! ***")
                print("Set the EMAIL_PASSWORD environment variable or update the script.")
                return False
                
            server.send_message(msg)
            
        logger.info(f"Email sent to {EMAIL_TO}")
        print(f"Email successfully sent to {EMAIL_TO}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        # Add more detailed error info for debugging
        import traceback
        logger.error(traceback.format_exc())
        print(f"\nError sending email: {e}")
        print("Please check your email settings in the script.")
        return False

def main(today_only=False):
    """
    Main function to run the bot once
    If today_only is True, only check for today's transactions
    """
    try:
        # Get Blue Jays upcoming opponents from hardcoded schedule
        upcoming_opponents = get_blue_jays_schedule()
        
        # Get transactions
        if today_only:
            # Get only today's transactions
            today = datetime.datetime.now().date()
            transactions = get_transactions(today)
        else:
            # Get transactions since last check
            last_check_time = get_last_check_time()
            transactions = get_transactions(last_check_time.date())
        
        # Filter for relevant transactions (only opponents)
        relevant_transactions = filter_relevant_transactions(transactions, upcoming_opponents)
        
        # Generate report
        report = generate_report(relevant_transactions, upcoming_opponents)
        
        # Check if we have new transactions
        has_new_transactions = len(relevant_transactions) > 0
        
        # Print report to console
        print("\n" + report)
        
        # Send email only if there are new transactions since the last check
        if has_new_transactions and EMAIL_ENABLED:
            subject = generate_email_subject(relevant_transactions)
            send_email(subject, report)
            logger.info("Email sent with new transactions")
        else:
            if not has_new_transactions:
                logger.info("No email sent (no new transactions)")
            elif not EMAIL_ENABLED:
                logger.info("No email sent (email disabled)")
        
        # Update last check time
        update_last_check_time()
        
    except Exception as e:
        error_msg = f"Error in main function: {e}"
        logger.error(error_msg)
        print(f"Error: {error_msg}")

if __name__ == "__main__":
    print("\n=== Blue Jays Opponent Transactions Checker ===")
    print("Checking for transactions from opponents in the next 5 days...")
    
    # For scheduled runs, we only want to check since the last time
    main(today_only=False)
