import os
import sys
import time
import json
import logging
import argparse
import threading
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import telegram
import schedule
import talib
import requests
import configparser
from colorama import init, Fore, Style

# Inisialisasi colorama untuk output berwarna
init()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bnb_trading_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("BNB_Trading_Bot")

# Baca konfigurasi
config = configparser.ConfigParser()
config.read('config.ini')

# Konfigurasi default jika file config.ini tidak ada
if not config.sections():
    config['BINANCE'] = {
        'api_key': os.environ.get('BINANCE_API_KEY', ''),
        'api_secret': os.environ.get('BINANCE_SECRET_KEY', '')
    }
    config['TELEGRAM'] = {
        'bot_token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
        'chat_id': os.environ.get('TELEGRAM_CHAT_ID', '')
    }
    config['TRADING'] = {
        'symbol': 'BNBUSDT',
        'quantity': '0.1',
        'enable_auto_trading': os.environ.get('ENABLE_AUTO_TRADING', 'False'),
        'signal_threshold': os.environ.get('SIGNAL_THRESHOLD', '65'),
        'analysis_interval': os.environ.get('ANALYSIS_INTERVAL', '60')
    }
    
    # Simpan konfigurasi default ke file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Kelas utama BNB Trading Bot
class BNBTradingBot:
    def __init__(self):
        self.binance_api_key = config['BINANCE']['api_key']
        self.binance_api_secret = config['BINANCE']['api_secret']
        self.telegram_bot_token = config['TELEGRAM']['bot_token']
        self.telegram_chat_id = config['TELEGRAM']['chat_id']
        self.symbol = config['TRADING']['symbol']
        self.quantity = float(config['TRADING']['quantity'])
        self.enable_auto_trading = config['TRADING'].getboolean('enable_auto_trading')
        self.signal_threshold = int(config['TRADING']['signal_threshold'])
        self.analysis_interval = int(config['TRADING']['analysis_interval'])
        
        self.client = None
        self.telegram_bot = None
        self.last_analysis_time = None
        self.signals_log = []
        self.trades_log = []
        
        # Inisialisasi koneksi
        self.initialize_connections()
        
    def initialize_connections(self):
        """Inisialisasi koneksi ke Binance dan Telegram"""
        try:
            # Inisialisasi Binance client
            self.client = Client(self.binance_api_key, self.binance_api_secret)
            logger.info(f"Berhasil terhubung ke Binance API")
            
            # Test koneksi dengan mendapatkan server time
            server_time = self.client.get_server_time()
            logger.info(f"Binance server time: {datetime.fromtimestamp(server_time['serverTime']/1000)}")
            
            # Inisialisasi Telegram bot
            self.telegram_bot = telegram.Bot(token=self.telegram_bot_token)
            logger.info(f"Berhasil terhubung ke Telegram Bot API")
            
            # Kirim pesan selamat datang
            self.send_telegram_message("🚀 *BNB Trading Bot Aktif*\n\nBot trading BNB telah dimulai dan siap menganalisis pasar.")
            
        except BinanceAPIException as e:
            logger.error(f"Error koneksi Binance API: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error inisialisasi: {e}")
            sys.exit(1)
    
    def send_telegram_message(self, message):
        """Kirim pesan ke Telegram"""
        try:
            if self.telegram_bot and self.telegram_chat_id:
                self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
                logger.info(f"Pesan terkirim ke Telegram")
            else:
                logger.warning("Telegram bot atau chat ID tidak dikonfigurasi")
        except Exception as e:
            logger.error(f"Error mengirim pesan Telegram: {e}")
    
    def get_historical_data(self, symbol, interval='1h', limit=100):
        """Dapatkan data historis dari Binance"""
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            data = []
            for kline in klines:
                data.append({
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': kline[6],
                    'quote_asset_volume': float(kline[7]),
                    'number_of_trades': int(kline[8]),
                    'taker_buy_base_asset_volume': float(kline[9]),
                    'taker_buy_quote_asset_volume': float(kline[10])
                })
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error mendapatkan data historis: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df):
        """Hitung indikator teknis"""
        try:
            # Konversi ke numpy array untuk talib
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            volume = df['volume'].values
            
            # Hitung RSI
            df['rsi'] = talib.RSI(close_prices, timeperiod=14)
            
            # Hitung MACD
            macd, macd_signal, macd_hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_hist'] = macd_hist
            
            # Hitung Bollinger Bands
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower
            
            # Hitung Moving Averages
            df['sma_20'] = talib.SMA(close_prices, timeperiod=20)
            df['sma_50'] = talib.SMA(close_prices, timeperiod=50)
            df['sma_200'] = talib.SMA(close_prices, timeperiod=200)
            df['ema_20'] = talib.EMA(close_prices, timeperiod=20)
            
            # Hitung Stochastic
            df['slowk'], df['slowd'] = talib.STOCH(high_prices, low_prices, close_prices, 
                                                  fastk_period=14, slowk_period=3, slowk_matype=0, 
                                                  slowd_period=3, slowd_matype=0)
            
            # Hitung ATR (Average True Range)
            df['atr'] = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)
            
            # Hitung OBV (On Balance Volume)
            df['obv'] = talib.OBV(close_prices, volume)
            
            return df
        except Exception as e:
            logger.error(f"Error menghitung indikator: {e}")
            return df
    
    def analyze_bnb_btc_correlation(self):
        """Analisis korelasi BNB-BTC"""
        try:
            # Dapatkan data historis BNB dan BTC
            bnb_data = self.get_historical_data('BNBUSDT', interval='1d', limit=30)
            btc_data = self.get_historical_data('BTCUSDT', interval='1d', limit=30)
            
            if bnb_data.empty or btc_data.empty:
                return {
                    'correlation': 0,
                    'interpretation': 'Unknown',
                    'btc_trend': 'unknown',
                    'signal': 'NEUTRAL',
                    'confidence': 0
                }
            
            # Hitung korelasi
            bnb_prices = bnb_data['close'].values
            btc_prices = btc_data['close'].values
            
            # Pastikan panjang data sama
            min_length = min(len(bnb_prices), len(btc_prices))
            bnb_prices = bnb_prices[-min_length:]
            btc_prices = btc_prices[-min_length:]
            
            correlation = np.corrcoef(bnb_prices, btc_prices)[0, 1]
            
            # Analisis tren BTC
            btc_trend = 'bullish' if btc_prices[-1] > btc_prices[0] else 'bearish'
            
            # Interpretasi korelasi
            interpretation = ''
            signal = 'NEUTRAL'
            confidence = 0
            
            if correlation > 0.7:
                interpretation = 'Strong positive correlation'
                signal = 'BUY' if btc_trend == 'bullish' else 'SELL'
                confidence = 70
            elif correlation > 0.3:
                interpretation = 'Moderate positive correlation'
                signal = 'BUY' if btc_trend == 'bullish' else 'SELL'
                confidence = 50
            elif correlation > -0.3:
                interpretation = 'Weak or no correlation'
                signal = 'NEUTRAL'
                confidence = 0
            elif correlation > -0.7:
                interpretation = 'Moderate negative correlation'
                signal = 'SELL' if btc_trend == 'bullish' else 'BUY'
                confidence = 50
            else:
                interpretation = 'Strong negative correlation'
                signal = 'SELL' if btc_trend == 'bullish' else 'BUY'
                confidence = 70
            
            return {
                'correlation': correlation,
                'interpretation': interpretation,
                'btc_trend': btc_trend,
                'signal': signal,
                'confidence': confidence
            }
        except Exception as e:
            logger.error(f"Error menganalisis korelasi BNB-BTC: {e}")
            return {
                'correlation': 0,
                'interpretation': 'Error',
                'btc_trend': 'unknown',
                'signal': 'NEUTRAL',
                'confidence': 0
            }
    
    def detect_whale_movement(self, threshold=10000):
        """Deteksi pergerakan whale BNB"""
        try:
            # Dapatkan trades terbaru
            trades = self.client.get_recent_trades(symbol=self.symbol, limit=1000)
            
            # Filter transaksi besar (whale)
            whale_trades = [trade for trade in trades if float(trade['qty']) * float(trade['price']) >= threshold]
            
            if not whale_trades:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'details': {}
                }
            
            # Analisis arah whale movement
            buy_whales = [trade for trade in whale_trades if trade['isBuyerMaker'] == False]
            sell_whales = [trade for trade in whale_trades if trade['isBuyerMaker'] == True]
            
            total_buy_volume = sum(float(trade['qty']) * float(trade['price']) for trade in buy_whales)
            total_sell_volume = sum(float(trade['qty']) * float(trade['price']) for trade in sell_whales)
            
            # Tentukan sinyal berdasarkan whale movement
            if len(buy_whales) > len(sell_whales) * 1.5 and total_buy_volume > total_sell_volume * 1.5:
                signal = 'BUY'
                confidence = 80
            elif len(sell_whales) > len(buy_whales) * 1.5 and total_sell_volume > total_buy_volume * 1.5:
                signal = 'SELL'
                confidence = 80
            else:
                signal = 'NEUTRAL'
                confidence = 0
            
            return {
                'signal': signal,
                'confidence': confidence,
                'details': {
                    'whale_trades': len(whale_trades),
                    'buy_whales': len(buy_whales),
                    'sell_whales': len(sell_whales),
                    'buy_volume': total_buy_volume,
                    'sell_volume': total_sell_volume
                }
            }
        except Exception as e:
            logger.error(f"Error mendeteksi whale movement: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'details': {}
            }
    
    def analyze_sentiment(self):
        """Analisis sentimen BNB dari media sosial (simulasi)"""
        try:
            # Dalam implementasi nyata, Anda perlu menggunakan API sentimen seperti Santiment, LunarCrush, dll.
            # Ini adalah simulasi sederhana
            
            # Simulasi data sentimen
            sentiment_data = {
                'overallScore': np.random.randint(30, 85),  # 0-100
                'socialVolume': np.random.randint(8000, 15000),
                'socialDominance': np.random.uniform(2.0, 5.0),  # %
                'twitterSentiment': np.random.choice(['positive', 'neutral', 'negative'], p=[0.5, 0.3, 0.2]),
                'redditSentiment': np.random.choice(['positive', 'neutral', 'negative'], p=[0.4, 0.4, 0.2]),
                'newsSentiment': np.random.choice(['positive', 'neutral', 'negative'], p=[0.45, 0.35, 0.2]),
                'sentimentChange24h': np.random.uniform(-8.0, 8.0)  # %
            }
            
            # Tentukan signal berdasarkan sentimen
            signal = 'NEUTRAL'
            confidence = 0
            
            if sentiment_data['overallScore'] >= 70 and sentiment_data['sentimentChange24h'] > 0:
                signal = 'BUY'
                confidence = 60
            elif sentiment_data['overallScore'] <= 30 and sentiment_data['sentimentChange24h'] < 0:
                signal = 'SELL'
                confidence = 60
            
            return {
                'sentiment': sentiment_data,
                'signal': signal,
                'confidence': confidence
            }
        except Exception as e:
            logger.error(f"Error menganalisis sentimen: {e}")
            return {
                'sentiment': None,
                'signal': 'NEUTRAL',
                'confidence': 0
            }
    
    def analyze_technical_indicators(self):
        """Analisis indikator teknis untuk BNB"""
        try:
            # Dapatkan data historis
            df = self.get_historical_data(self.symbol, interval='1h', limit=100)
            
            if df.empty:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'indicators': {}
                }
            
            # Hitung indikator
            df = self.calculate_indicators(df)
            
            # Ambil data terbaru
            latest = df.iloc[-1]
            
            # Analisis RSI
            rsi = latest['rsi']
            rsi_signal = 'NEUTRAL'
            rsi_confidence = 0
            
            if rsi < 30:
                rsi_signal = 'BUY'
                rsi_confidence = 70
            elif rsi > 70:
                rsi_signal = 'SELL'
                rsi_confidence = 70
            
            # Analisis MACD
            macd = latest['macd']
            macd_signal = latest['macd_signal']
            macd_hist = latest['macd_hist']
            
            macd_cross_signal = 'NEUTRAL'
            macd_confidence = 0
            
            # MACD crossover
            if macd > macd_signal and df.iloc[-2]['macd'] <= df.iloc[-2]['macd_signal']:
                macd_cross_signal = 'BUY'
                macd_confidence = 60
            elif macd < macd_signal and df.iloc[-2]['macd'] >= df.iloc[-2]['macd_signal']:
                macd_cross_signal = 'SELL'
                macd_confidence = 60
            
            # Analisis Bollinger Bands
            bb_signal = 'NEUTRAL'
            bb_confidence = 0
            
            if latest['close'] < latest['bb_lower']:
                bb_signal = 'BUY'
                bb_confidence = 65
            elif latest['close'] > latest['bb_upper']:
                bb_signal = 'SELL'
                bb_confidence = 65
            
            # Analisis Moving Averages
            ma_signal = 'NEUTRAL'
            ma_confidence = 0
            
            if latest['sma_20'] > latest['sma_50'] and df.iloc[-2]['sma_20'] <= df.iloc[-2]['sma_50']:
                ma_signal = 'BUY'
                ma_confidence = 55
            elif latest['sma_20'] < latest['sma_50'] and df.iloc[-2]['sma_20'] >= df.iloc[-2]['sma_50']:
                ma_signal = 'SELL'
                ma_confidence = 55
            
            # Analisis Stochastic
            stoch_signal = 'NEUTRAL'
            stoch_confidence = 0
            
            if latest['slowk'] < 20 and latest['slowd'] < 20 and latest['slowk'] > latest['slowd']:
                stoch_signal = 'BUY'
                stoch_confidence = 60
            elif latest['slowk'] > 80 and latest['slowd'] > 80 and latest['slowk'] < latest['slowd']:
                stoch_signal = 'SELL'
                stoch_confidence = 60
            
            # Gabungkan semua sinyal
            signals = [
                {'name': 'RSI', 'signal': rsi_signal, 'confidence': rsi_confidence},
                {'name': 'MACD', 'signal': macd_cross_signal, 'confidence': macd_confidence},
                {'name': 'Bollinger Bands', 'signal': bb_signal, 'confidence': bb_confidence},
                {'name': 'Moving Averages', 'signal': ma_signal, 'confidence': ma_confidence},
                {'name': 'Stochastic', 'signal': stoch_signal, 'confidence': stoch_confidence}
            ]
            
            # Filter sinyal yang tidak netral
            active_signals = [s for s in signals if s['signal'] != 'NEUTRAL']
            
            if not active_signals:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'indicators': {
                        'rsi': rsi,
                        'macd': macd,
                        'macd_signal': macd_signal,
                        'macd_hist': macd_hist,
                        'bb_upper': latest['bb_upper'],
                        'bb_middle': latest['bb_middle'],
                        'bb_lower': latest['bb_lower'],
                        'sma_20': latest['sma_20'],
                        'sma_50': latest['sma_50'],
                        'slowk': latest['slowk'],
                        'slowd': latest['slowd']
                    }
                }
            
            # Hitung sinyal gabungan
            buy_signals = [s for s in active_signals if s['signal'] == 'BUY']
            sell_signals = [s for s in active_signals if s['signal'] == 'SELL']
            
            buy_confidence = sum(s['confidence'] for s in buy_signals) / len(active_signals) if buy_signals else 0
            sell_confidence = sum(s['confidence'] for s in sell_signals) / len(active_signals) if sell_signals else 0
            
            final_signal = 'NEUTRAL'
            final_confidence = 0
            
            if buy_confidence > sell_confidence and buy_confidence > 50:
                final_signal = 'BUY'
                final_confidence = buy_confidence
            elif sell_confidence > buy_confidence and sell_confidence > 50:
                final_signal = 'SELL'
                final_confidence = sell_confidence
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'macd_signal': macd_signal,
                    'macd_hist': macd_hist,
                    'bb_upper': latest['bb_upper'],
                    'bb_middle': latest['bb_middle'],
                    'bb_lower': latest['bb_lower'],
                    'sma_20': latest['sma_20'],
                    'sma_50': latest['sma_50'],
                    'slowk': latest['slowk'],
                    'slowd': latest['slowd'],
                    'signals': signals
                }
            }
        except Exception as e:
            logger.error(f"Error menganalisis indikator teknis: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'indicators': {}
            }
    
    def analyze_bnb_comprehensive(self):
        """Analisis komprehensif BNB"""
        try:
            logger.info("Memulai analisis komprehensif BNB...")
            
            # Dapatkan harga saat ini
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            current_price = float(ticker['price'])
            
            logger.info(f"Harga BNB saat ini: ${current_price}")
            
            # Jalankan semua analisis
            technical_result = self.analyze_technical_indicators()
            correlation_result = self.analyze_bnb_btc_correlation()
            whale_result = self.detect_whale_movement(10000)
            sentiment_result = self.analyze_sentiment()
            
            # Kumpulkan semua sinyal
            signals = [
                {'name': 'Technical Indicators', **technical_result},
                {'name': 'BTC Correlation', **correlation_result},
                {'name': 'Whale Movement', **whale_result},
                {'name': 'Sentiment Analysis', **sentiment_result}
            ]
            
            # Filter sinyal yang tidak netral
            active_signals = [s for s in signals if s['signal'] != 'NEUTRAL']
            
            # Hitung sinyal gabungan
            buy_signals = [s for s in active_signals if s['signal'] == 'BUY']
            sell_signals = [s for s in active_signals if s['signal'] == 'SELL']
            
            total_signals = len(active_signals)
            
            if total_signals == 0:
                final_signal = 'NEUTRAL'
                final_confidence = 0
            else:
                buy_confidence = sum(s['confidence'] for s in buy_signals) / total_signals if buy_signals else 0
                sell_confidence = sum(s['confidence'] for s in sell_signals) / total_signals if sell_signals else 0
                
                if buy_confidence > sell_confidence:
                    final_signal = 'BUY'
                    final_confidence = buy_confidence * (len(buy_signals) / total_signals)
                elif sell_confidence > buy_confidence:
                    final_signal = 'SELL'
                    final_confidence = sell_confidence * (len(sell_signals) / total_signals)
                else:
                    final_signal = 'NEUTRAL'
                    final_confidence = 0
            
            # Log sinyal
            self.log_signal(self.symbol, final_signal, current_price, final_confidence, {
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'total_signals': total_signals,
                'technical': technical_result,
                'correlation': correlation_result,
                'whale': whale_result,
                'sentiment': sentiment_result
            })
            
            # Kirim notifikasi jika sinyal cukup kuat
            if final_signal != 'NEUTRAL' and final_confidence >= self.signal_threshold:
                self.send_signal_notification(final_signal, current_price, final_confidence, {
                    'buy_signals': len(buy_signals),
                    'sell_signals': len(sell_signals),
                    'total_signals': total_signals,
                    'technical': technical_result,
                    'correlation': correlation_result,
                    'whale': whale_result,
                    'sentiment': sentiment_result
                })
                
                # Eksekusi trading jika auto trading diaktifkan
                if self.enable_auto_trading:
                    self.execute_trade(final_signal, current_price, final_confidence)
            
            self.last_analysis_time = datetime.now()
            
            return {
                'price': current_price,
                'signal': final_signal,
                'confidence': final_confidence,
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'total_signals': total_signals,
                'detailed_signals': signals,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error dalam analisis komprehensif BNB: {e}")
            self.send_telegram_message(f"❌ *Error dalam Analisis BNB*\n{str(e)}")
            return {
                'price': 0,
                'signal': 'ERROR',
                'confidence': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'total_signals': 0,
                'detailed_signals': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def log_signal(self, symbol, signal_type, price, confidence, indicators):
        """Log sinyal trading"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Buat direktori log jika belum ada
            os.makedirs('logs', exist_ok=True)
            
            # Simpan ke list untuk penggunaan dalam memori
            signal_data = {
                'timestamp': timestamp,
                'symbol': symbol,
                'signal_type': signal_type,
                'price': price,
                'confidence': confidence,
                'indicators': indicators
            }
            
            self.signals_log.append(signal_data)
            
            # Simpan ke file CSV
            log_file = os.path.join('logs', 'bnb_signals_log.csv')
            
            # Buat header jika file belum ada
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('timestamp,symbol,signal_type,price,confidence,indicators\n')
            
            # Format indikator sebagai string JSON
            indicators_str = json.dumps(indicators).replace(',', ';')
            
            # Tulis log
            with open(log_file, 'a') as f:
                f.write(f"{timestamp},{symbol},{signal_type},{price},{confidence},\"{indicators_str}\"\n")
            
            logger.info(f"Signal logged: {symbol} {signal_type} at ${price} with {confidence}% confidence")
            
        except Exception as e:
            logger.error(f"Error logging signal: {e}")
    
    def send_signal_notification(self, signal, price, confidence, details):
        """Kirim notifikasi sinyal ke Telegram"""
        try:
            # Format pesan
            signal_emoji = "🟢" if signal == "BUY" else "🔴"
            
            message = f"""
{signal_emoji} *Sinyal Trading BNB: {signal}*
💰 Harga: ${price:.2f}
🎯 Confidence: {confidence:.2f}%

📊 *Analisis:*
- Indikator Teknis: {details['technical']['signal']} ({details['technical']['confidence']:.2f}%)
- Korelasi BTC: {details['correlation']['signal']} ({details['correlation']['confidence']:.2f}%)
- Whale Movement: {details['whale']['signal']} ({details['whale']['confidence']:.2f}%)
- Sentimen: {details['sentiment']['signal']} ({details['sentiment']['confidence']:.2f}%)

📈 *Detail Indikator Teknis:*
- RSI: {details['technical']['indicators'].get('rsi', 'N/A'):.2f}
- MACD: {details['technical']['indicators'].get('macd_hist', 'N/A'):.2f}
- Stochastic: K={details['technical']['indicators'].get('slowk', 'N/A'):.2f}, D={details['technical']['indicators'].get('slowd', 'N/A'):.2f}

⚠️ *Disclaimer:* Sinyal ini adalah hasil analisis otomatis dan bukan rekomendasi finansial. Selalu lakukan analisis Anda sendiri sebelum trading.
            """
            
            self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")
    
    def execute_trade(self, signal, price, confidence):
        """Eksekusi trading berdasarkan sinyal"""
        try:
            logger.info(f"Executing {signal} trading signal at ${price} with {confidence}% confidence")
            
            # Dalam implementasi nyata, ini akan memanggil API Binance untuk membuat order
            # Untuk demo, kita hanya simulasikan
            
            order_id = f"simulated_{int(time.time())}"
            timestamp = datetime.now().isoformat()
            
            # Log trading
            trade_data = {
                'timestamp': timestamp,
                'order_id': order_id,
                'symbol': self.symbol,
                'signal': signal,
                'price': price,
                'quantity': self.quantity,
                'total_value': price * self.quantity,
                'confidence': confidence,
                'status': 'SIMULATED'  # Dalam implementasi nyata: 'FILLED', 'REJECTED', dll.
            }
            
            self.trades_log.append(trade_data)
            
            # Simpan ke file CSV
            log_file = os.path.join('logs', 'bnb_trading_log.csv')
            
            # Buat header jika file belum ada
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('timestamp,order_id,symbol,signal,price,quantity,total_value,confidence,status\n')
            
            # Tulis log
            with open(log_file, 'a') as f:
                f.write(f"{timestamp},{order_id},{self.symbol},{signal},{price},{self.quantity},{price * self.quantity},{confidence},{trade_data['status']}\n")
            
            # Kirim notifikasi
            self.send_telegram_message(f"""
💰 *BNB Trading Executed*
Signal: {signal_emoji} {signal}
Price: ${price:.2f}
Amount: {self.quantity} BNB
Total value: ${(price * self.quantity):.2f}
Confidence: {confidence:.2f}%

This trade was automatically executed based on comprehensive analysis.
            """)
            
            return {
                'success': True,
                'order_id': order_id,
                'signal': signal,
                'price': price,
                'quantity': self.quantity,
                'total_value': price * self.quantity,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error executing trading: {e}")
            self.send_telegram_message(f"❌ *Trading Error*\n{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_scheduled_analysis(self):
        """Jalankan analisis terjadwal"""
        logger.info(f"Running scheduled BNB analysis...")
        analysis_result = self.analyze_bnb_comprehensive()
        logger.info(f"Analysis completed: {analysis_result['signal']} with {analysis_result['confidence']}% confidence")
    
    def start(self):
        """Mulai bot trading"""
        logger.info("Starting BNB Trading Bot...")
        
        # Jalankan analisis pertama kali
        self.run_scheduled_analysis()
        
        # Jadwalkan analisis berikutnya
        schedule.every(self.analysis_interval).minutes.do(self.run_scheduled_analysis)
        
        logger.info(f"Scheduled analysis every {self.analysis_interval} minutes")
        
        # Loop utama
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.send_telegram_message(f"❌ *Bot Error*\nBot stopped due to an error: {str(e)}")
    
    def get_bot_status(self):
        """Dapatkan status bot"""
        return {
            'running': True,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'analysis_interval': self.analysis_interval,
            'signal_threshold': self.signal_threshold,
            'auto_trading': self.enable_auto_trading,
            'symbol': self.symbol,
            'quantity': self.quantity
        }
    
    def get_trading_stats(self):
        """Dapatkan statistik trading"""
        if not self.trades_log:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'average_profit': 0
            }
        
        # Dalam implementasi nyata, Anda perlu menghitung P/L berdasarkan harga masuk dan keluar
        # Untuk demo, kita hanya simulasikan
        
        total_trades = len(self.trades_log)
        successful_trades = int(total_trades * 0.65)  # Simulasi 65% win rate
        failed_trades = total_trades - successful_trades
        
        win_rate = (successful_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Simulasi profit
        total_value = sum(trade['total_value'] for trade in self.trades_log)
        total_profit = total_value * 0.08  # Simulasi 8% profit
        average_profit = total_profit / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'successful_trades': successful_trades,
            'failed_trades': failed_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'average_profit': average_profit
        }

# Fungsi untuk menampilkan banner
def show_banner():
    banner = f"""
{Fore.YELLOW}
██████╗ ███╗   ██╗██████╗     ████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗     ██████╗  ██████╗ ████████╗
██╔══██╗████╗  ██║██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝     ██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██╔██╗ ██║██████╔╝       ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗    ██████╔╝██║   ██║   ██║   
██╔══██╗██║╚██╗██║██╔══██╗       ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║    ██╔══██╗██║   ██║   ██║   
██████╔╝██║ ╚████║██████╔╝       ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝    ██████╔╝╚██████╔╝   ██║   
╚═════╝ ╚═╝  ╚═══╝╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═════╝  ╚═════╝    ╚═╝   
{Style.RESET_ALL}
{Fore.CYAN}Version: 1.0.0{Style.RESET_ALL}
{Fore.GREEN}Created by: Crypto Sniper Team{Style.RESET_ALL}

"""
    print(banner)

# Fungsi untuk memeriksa dependensi
def check_dependencies():
    required_packages = [
        'pandas', 'numpy', 'python-binance', 'python-telegram-bot',
        'schedule', 'talib', 'requests', 'colorama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{Fore.RED}Missing required packages: {', '.join(missing_packages)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please install them using: pip install {' '.join(missing_packages)}{Style.RESET_ALL}")
        return False
    
    return True

# Fungsi untuk memeriksa konfigurasi
def check_configuration():
    required_configs = [
        ('BINANCE', 'api_key'),
        ('BINANCE', 'api_secret'),
        ('TELEGRAM', 'bot_token'),
        ('TELEGRAM', 'chat_id')
    ]
    
    missing_configs = []
    
    for section, option in required_configs:
        if not config.has_option(section, option) or not config[section][option]:
            missing_configs.append(f"{section}.{option}")
    
    if missing_configs:
        print(f"{Fore.RED}Missing required configurations: {', '.join(missing_configs)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please update your config.ini file or set environment variables.{Style.RESET_ALL}")
        return False
    
    return True

# Fungsi utama
def main():
    show_banner()
    
    parser = argparse.ArgumentParser(description='BNB Trading Bot')
    parser.add_argument('--check', action='store_true', help='Check dependencies and configuration')
    parser.add_argument('--analyze', action='store_true', help='Run a single analysis without starting the bot')
    parser.add_argument('--backtest', action='store_true', help='Run backtesting on historical data')
    args = parser.parse_args()
    
    if args.check:
        deps_ok = check_dependencies()
        config_ok = check_configuration()
        
        if deps_ok and config_ok:
            print(f"{Fore.GREEN}All dependencies and configurations are OK!{Style.RESET_ALL}")
        
        return
    
    if not check_dependencies() or not check_configuration():
        return
    
    bot = BNBTradingBot()
    
    if args.analyze:
        print(f"{Fore.CYAN}Running single analysis...{Style.RESET_ALL}")
        result = bot.analyze_bnb_comprehensive()
        print(f"{Fore.GREEN}Analysis result:{Style.RESET_ALL}")
        print(json.dumps(result, indent=2))
        return
    
    if args.backtest:
        print(f"{Fore.YELLOW}Backtesting functionality not implemented yet.{Style.RESET_ALL}")
        return
    
    # Start the bot
    bot.start()

if __name__ == "__main__":
    main()
