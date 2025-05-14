from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import json
import os
import logging
from datetime import datetime
import configparser
from binance_bot import BinanceBot
from telegram_notifier import TelegramNotifier

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Baca konfigurasi
config = configparser.ConfigParser()
config.read('config.ini')

# Inisialisasi Flask app
app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk semua routes

# Inisialisasi bot dan notifier
try:
    bot = BinanceBot(
        api_key=config['BINANCE']['api_key'],
        api_secret=config['BINANCE']['api_secret'],
        symbol=config['TRADING']['symbol'],
        quantity=float(config['TRADING']['quantity'])
    )
    
    notifier = TelegramNotifier(
        bot_token=config['TELEGRAM']['bot_token'],
        chat_id=config['TELEGRAM']['chat_id']
    )
    
    # Kirim notifikasi bahwa bot telah dimulai
    notifier.send_message("🚀 BNB Trading Bot server telah dimulai!")
    
except Exception as e:
    logger.error(f"Error initializing bot: {e}")
    bot = None
    notifier = None

# Status bot
bot_status = {
    "running": False,
    "last_analysis": None,
    "analysis_interval": int(config['TRADING']['analysis_interval']),
    "signal_threshold": int(config['TRADING']['signal_threshold']),
    "auto_trading": config['TRADING'].getboolean('enable_auto_trading'),
    "version": "1.0.0",
    "uptime": 0,
    "start_time": datetime.now().isoformat()
}

# Data trading
trading_stats = {
    "total_trades": 0,
    "successful_trades": 0,
    "failed_trades": 0,
    "win_rate": 0,
    "total_profit": 0,
    "average_profit": 0
}

# Menyimpan sinyal trading
trading_signals = []

# Thread untuk analisis otomatis
def analysis_thread():
    global bot_status, trading_signals
    
    while bot_status["running"]:
        try:
            logger.info("Running analysis...")
            
            # Dapatkan data historis
            historical_data = bot.get_historical_data()
            
            # Analisis data dan dapatkan sinyal
            signal = bot.analyze_data(historical_data)
            
            # Simpan sinyal
            if signal:
                trading_signals.append({
                    "id": f"signal-{len(trading_signals) + 1}",
                    "timestamp": datetime.now().isoformat(),
                    "symbol": bot.symbol,
                    "type": signal["type"],
                    "price": signal["price"],
                    "confidence": signal["confidence"],
                    "indicators": signal["indicators"]
                })
                
                # Batasi jumlah sinyal yang disimpan
                if len(trading_signals) > 100:
                    trading_signals = trading_signals[-100:]
                
                # Kirim notifikasi
                notifier.send_signal(signal)
                
                # Eksekusi trading otomatis jika diaktifkan
                if bot_status["auto_trading"] and signal["confidence"] >= bot_status["signal_threshold"]:
                    if signal["type"] == "BUY":
                        result = bot.place_buy_order()
                        notifier.send_message(f"🟢 Auto BUY order executed: {result}")
                    elif signal["type"] == "SELL":
                        result = bot.place_sell_order()
                        notifier.send_message(f"🔴 Auto SELL order executed: {result}")
            
            # Update status bot
            bot_status["last_analysis"] = datetime.now().isoformat()
            
            # Simpan data ke file
            save_data_to_file()
            
        except Exception as e:
            logger.error(f"Error in analysis thread: {e}")
            notifier.send_message(f"⚠️ Error in analysis thread: {e}")
        
        # Tunggu interval analisis berikutnya
        time.sleep(bot_status["analysis_interval"] * 60)

# Thread utama
analysis_thread_instance = None

def start_bot():
    global bot_status, analysis_thread_instance
    
    if not bot_status["running"]:
        bot_status["running"] = True
        bot_status["start_time"] = datetime.now().isoformat()
        
        # Mulai thread analisis
        analysis_thread_instance = threading.Thread(target=analysis_thread)
        analysis_thread_instance.daemon = True
        analysis_thread_instance.start()
        
        logger.info("Bot started")
        return True
    
    return False

def stop_bot():
    global bot_status, analysis_thread_instance
    
    if bot_status["running"]:
        bot_status["running"] = False
        
        # Tunggu thread analisis berhenti
        if analysis_thread_instance:
            analysis_thread_instance.join(timeout=5)
        
        logger.info("Bot stopped")
        return True
    
    return False

# Fungsi untuk menyimpan data ke file
def save_data_to_file():
    try:
        # Simpan sinyal trading
        with open('data/signals.json', 'w') as f:
            json.dump(trading_signals, f)
        
        # Simpan statistik trading
        with open('data/stats.json', 'w') as f:
            json.dump(trading_stats, f)
        
        # Simpan status bot
        with open('data/status.json', 'w') as f:
            json.dump(bot_status, f)
    
    except Exception as e:
        logger.error(f"Error saving data to file: {e}")

# Fungsi untuk memuat data dari file
def load_data_from_file():
    global trading_signals, trading_stats, bot_status
    
    try:
        # Buat direktori data jika belum ada
        os.makedirs('data', exist_ok=True)
        
        # Muat sinyal trading
        if os.path.exists('data/signals.json'):
            with open('data/signals.json', 'r') as f:
                trading_signals = json.load(f)
        
        # Muat statistik trading
        if os.path.exists('data/stats.json'):
            with open('data/stats.json', 'r') as f:
                trading_stats = json.load(f)
        
        # Muat status bot
        if os.path.exists('data/status.json'):
            with open('data/status.json', 'r') as f:
                saved_status = json.load(f)
                # Update hanya beberapa field
                for key in ['analysis_interval', 'signal_threshold', 'auto_trading']:
                    if key in saved_status:
                        bot_status[key] = saved_status[key]
    
    except Exception as e:
        logger.error(f"Error loading data from file: {e}")

# API Routes

@app.route('/api/price', methods=['GET'])
def get_price():
    symbol = request.args.get('symbol', 'BNBUSDT')
    
    try:
        price = bot.get_current_price(symbol)
        return jsonify({
            "symbol": symbol,
            "price": str(price),
            "lastUpdate": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting price: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/historical', methods=['GET'])
def get_historical():
    symbol = request.args.get('symbol', 'BNBUSDT')
    interval = request.args.get('interval', '1d')
    limit = int(request.args.get('limit', 30))
    
    try:
        data = bot.get_historical_data(symbol, interval, limit)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot-status', methods=['GET'])
def get_bot_status():
    # Hitung uptime
    if bot_status["running"]:
        start_time = datetime.fromisoformat(bot_status["start_time"])
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        bot_status["uptime"] = f"{int(uptime_seconds // 3600)} hours, {int((uptime_seconds % 3600) // 60)} minutes"
    
    return jsonify(bot_status)

@app.route('/api/trading-stats', methods=['GET'])
def get_trading_stats():
    return jsonify(trading_stats)

@app.route('/api/signals', methods=['GET'])
def get_signals():
    limit = int(request.args.get('limit', 10))
    signal_type = request.args.get('type')
    
    filtered_signals = trading_signals
    
    # Filter berdasarkan tipe jika ditentukan
    if signal_type:
        filtered_signals = [s for s in filtered_signals if s["type"].upper() == signal_type.upper()]
    
    # Urutkan berdasarkan timestamp (terbaru dulu)
    sorted_signals = sorted(filtered_signals, key=lambda x: x["timestamp"], reverse=True)
    
    # Batasi jumlah hasil
    limited_signals = sorted_signals[:limit]
    
    return jsonify(limited_signals)

@app.route('/api/bnb-trading', methods=['GET'])
def get_prediction():
    try:
        # Dapatkan data historis
        historical_data = bot.get_historical_data()
        
        # Analisis data dan dapatkan sinyal
        signal = bot.analyze_data(historical_data)
        
        if not signal:
            # Jika tidak ada sinyal, buat prediksi default
            current_price = bot.get_current_price()
            signal = {
                "type": "NEUTRAL",
                "price": current_price,
                "confidence": 0.5,
                "indicators": {
                    "rsi": 50,
                    "macd": "neutral",
                    "movingAverages": "sideways",
                    "volume": "stable"
                },
                "nextPriceTarget": current_price * 1.01,
                "stopLoss": current_price * 0.99
            }
        
        return jsonify({
            "status": "success",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "currentPrice": signal["price"],
                "prediction": signal["type"],
                "confidence": signal["confidence"],
                "indicators": signal["indicators"],
                "nextPriceTarget": signal.get("nextPriceTarget", signal["price"] * 1.02),
                "stopLoss": signal.get("stopLoss", signal["price"] * 0.98)
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting prediction: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bnb-trading', methods=['POST'])
def execute_trade():
    try:
        data = request.json
        order_type = data.get('orderType', 'BUY')
        amount = data.get('amount', 0.1)
        
        result = None
        
        if order_type.upper() == 'BUY':
            result = bot.place_buy_order(amount)
            # Update statistik trading
            trading_stats["total_trades"] += 1
            if result.get("status") == "success":
                trading_stats["successful_trades"] += 1
            else:
                trading_stats["failed_trades"] += 1
        
        elif order_type.upper() == 'SELL':
            result = bot.place_sell_order(amount)
            # Update statistik trading
            trading_stats["total_trades"] += 1
            if result.get("status") == "success":
                trading_stats["successful_trades"] += 1
            else:
                trading_stats["failed_trades"] += 1
        
        # Hitung win rate
        if trading_stats["total_trades"] > 0:
            trading_stats["win_rate"] = (trading_stats["successful_trades"] / trading_stats["total_trades"]) * 100
        
        # Simpan data ke file
        save_data_to_file()
        
        # Kirim notifikasi
        notifier.send_message(f"🔄 Manual {order_type} order executed: {result}")
        
        return jsonify({
            "status": "success",
            "message": f"{order_type} order executed successfully",
            "orderDetails": {
                "type": order_type,
                "amount": amount,
                "price": bot.get_current_price(),
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
        })
    
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/telegram-notify', methods=['POST'])
def send_telegram():
    try:
        data = request.json
        message = data.get('message', '')
        
        if message:
            notifier.send_message(message)
            return jsonify({
                "status": "success",
                "message": "Notification sent to Telegram"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No message provided"
            }), 400
    
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/toggle-auto-trading', methods=['POST'])
def toggle_auto_trading():
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        bot_status["auto_trading"] = enabled
        
        # Update konfigurasi
        config['TRADING']['enable_auto_trading'] = str(enabled)
        with open('config.ini', 'w') as f:
            config.write(f)
        
        # Simpan data ke file
        save_data_to_file()
        
        # Kirim notifikasi
        notifier.send_message(f"🔄 Auto trading {'enabled' if enabled else 'disabled'}")
        
        return jsonify({
            "success": True,
            "autoTrading": enabled
        })
    
    except Exception as e:
        logger.error(f"Error toggling auto trading: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start_bot():
    if start_bot():
        notifier.send_message("🟢 Bot started")
        return jsonify({"status": "success", "message": "Bot started"})
    else:
        return jsonify({"status": "error", "message": "Bot already running"}), 400

@app.route('/api/stop', methods=['POST'])
def api_stop_bot():
    if stop_bot():
        notifier.send_message("🔴 Bot stopped")
        return jsonify({"status": "success", "message": "Bot stopped"})
    else:
        return jsonify({"status": "error", "message": "Bot not running"}), 400

# Rute untuk health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "bot_running": bot_status["running"]
    })

if __name__ == '__main__':
    # Muat data dari file
    load_data_from_file()
    
    # Mulai bot jika auto_trading diaktifkan
    if bot_status["auto_trading"]:
        start_bot()
    
    # Jalankan server Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
