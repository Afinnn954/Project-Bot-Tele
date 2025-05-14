import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Mengirim pesan ke Telegram"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"Message sent to Telegram: {message}")
                return True
            else:
                logger.error(f"Failed to send message to Telegram: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False
    
    def send_signal(self, signal):
        """Mengirim sinyal trading ke Telegram"""
        try:
            # Format pesan
            emoji = "🟢" if signal["type"] == "BUY" else "🔴" if signal["type"] == "SELL" else "⚪"
            
            message = f"{emoji} <b>Signal: {signal['type']}</b>\n\n"
            message += f"<b>Symbol:</b> {signal.get('symbol', 'BNBUSDT')}\n"
            message += f"<b>Price:</b> ${signal['price']}\n"
            message += f"<b>Confidence:</b> {signal['confidence']:.2f}%\n\n"
            
            message += "<b>Indicators:</b>\n"
            for key, value in signal['indicators'].items():
                message += f"- {key}: {value}\n"
            
            message += f"\n<b>Target:</b> ${signal['nextPriceTarget']}\n"
            message += f"<b>Stop Loss:</b> ${signal['stopLoss']}\n"
            message += f"\n<i>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
            
            return self.send_message(message)
        
        except Exception as e:
            logger.error(f"Error sending signal to Telegram: {e}")
            return False
