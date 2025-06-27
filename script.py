from features.signings import scrape_signings
from features.trades import scrape_trades
import pickle
import os
from telegram_notify import send_signing_notification, send_trade_notification

# Initialize/load pickle database
def load_db():
    if os.path.exists('transactions.pkl'):
        with open('transactions.pkl', 'rb') as f:
            return pickle.load(f)
    return {'signings': [], 'trades': []}

def save_db(db):
    with open('transactions.pkl', 'wb') as f:
        pickle.dump(db, f)

# Load existing transactions
db = load_db()

# Get new transactions
signings = scrape_signings()
trades = scrape_trades()
# Check for new signings
if signings:
    for signing in signings:
        if signing not in db['signings']:
            send_signing_notification(signing)
    
# Check for new trades
if trades:
    for trade in trades:
        if trade not in db['trades']:
            send_trade_notification(trade)

# Keep only most recent 20 trades and signings
db["signings"] = signings
db["trades"] = trades

# print(db['signings'])
# print(db['trades'])

# Save updated database
save_db(db)
