import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_telegram_notification(message, parse_mode='HTML'):
    """
    Send a notification to Telegram
    
    Args:
        message (str): The message to send
        parse_mode (str): 'HTML' or 'Markdown' for formatting
    """
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        print("Telegram bot not configured. Update telegram_config.py with your bot token and chat ID.")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error sending Telegram notification: {e}")
        return False

def send_signing_notification(signing_data):
    """
    Send a formatted signing notification to Telegram
    
    Args:
        signing_data (dict): The signing data from scrape_signings()
    """
    player = signing_data['player']
    team = signing_data['team']
    contract = signing_data['contract']
    
    message = f"""
🏒 <b>NEW SIGNING: {signing_data['date']}</b>

👤 <b>{player['name']}</b> to <b>{team['name']}</b>
• Position: {player['position']}
• Age: {player['age']} years old

💰 <b>Contract Details:</b>
• Cap Hit: {contract['capHit']} x {contract['length']}
• Total: {contract['total']}
• Type: {contract['type']}

🔗 <a href="{signing_data['details']}">View Details</a>
"""
    
    return send_telegram_notification(message)

def send_trade_notification(trade_data):
    """
    Send a formatted trade notification to Telegram
    
    Args:
        trade_data (dict): The trade data matching the Discord embed format
    """
    message = f"""
🔄 <b>TRADE: {trade_data.get('date', 'Today')}</b>

"""
    
    # Add each team's acquisitions
    for team in trade_data.get('teams', []):
        name = team.get('name', 'Unknown Team')
        acq = team.get('acq', [])
        
        message += f"🏆 <b>{name} Acquire:</b>\n"
        
        if acq:
            for player in acq:
                desc = player.get('desc', 'Unknown Player')
                link = player.get('link', '')
                
                if link:
                    message += f"• <a href=\"{link}\">{desc}</a>\n"
                else:
                    message += f"• {desc}\n"
        else:
            message += "• No players acquired\n"
        
        message += "\n"
    
    # Add details link if available
    details = trade_data.get('details', '')
    if details:
        message += f"🔗 <a href=\"{details}\">View Details</a>"
    
    return send_telegram_notification(message)

