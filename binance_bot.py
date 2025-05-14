import logging
import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import talib
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class BinanceBot:
    def __init__(self, api_key, api_secret, symbol='BNBUSDT', quantity=0.1):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol
        self.quantity = quantity
        self.client = None
        
        self.connect()
    
    def connect(self):
        """Menghubungkan ke API Binance"""
        try:
            self.client = Client(self.api_key, self.api_secret)
            logger.info(f"Connected to Binance API")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Binance API: {e}")
            return False
    
    def get_current_price(self, symbol=None):
        """Mendapatkan harga terkini"""
        if symbol is None:
            symbol = self.symbol
        
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            raise e
    
    def get_historical_data(self, symbol=None, interval='1d', limit=100):
        """Mendapatkan data historis"""
        if symbol is None:
            symbol = self.symbol
        
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Konversi ke format yang lebih mudah digunakan
            data = []
            for k in klines:
                data.append({
                    'timestamp': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                })
            
            return data
        
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise e
    
    def analyze_data(self, data):
        """Menganalisis data dan menghasilkan sinyal trading"""
        if not data or len(data) < 50:
            logger.warning("Not enough data for analysis")
            return None
        
        try:
            # Konversi data ke DataFrame
            df = pd.DataFrame(data)
            
            # Hitung indikator teknis
            
            # RSI (Relative Strength Index)
            df['rsi'] = talib.RSI(np.array(df['close']), timeperiod=14)
            
            # MACD (Moving Average Convergence Divergence)
            macd, macdsignal, macdhist = talib.MACD(
                np.array(df['close']),
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            df['macd'] = macd
            df['macdsignal'] = macdsignal
            df['macdhist'] = macdhist
            
            # Bollinger Bands
            upperband, middleband, lowerband = talib.BBANDS(
                np.array(df['close']),
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            df['upperband'] = upperband
            df['middleband'] = middleband
            df['lowerband'] = lowerband
            
            # Moving Averages
            df['sma20'] = talib.SMA(np.array(df['close']), timeperiod=20)
            df['sma50'] = talib.SMA(np.array(df['close']), timeperiod=50)
            df['sma200'] = talib.SMA(np.array(df['close']), timeperiod=200)
            
            # Stochastic Oscillator
            slowk, slowd = talib.STOCH(
                np.array(df['high']),
                np.array(df['low']),
                np.array(df['close']),
                fastk_period=14,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0
            )
            df['slowk'] = slowk
            df['slowd'] = slowd
            
            # Ambil data terbaru
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Logika sinyal trading
            signal_type = "NEUTRAL"
            confidence = 0.5
            
            # Hitung skor untuk sinyal BUY
            buy_score = 0
            
            # RSI oversold (di bawah 30)
            if latest['rsi'] < 30:
                buy_score += 1
            
            # MACD crossover (MACD > Signal Line)
            if latest['macd'] > latest['macdsignal'] and prev['macd'] <= prev['macdsignal']:
                buy_score += 1
            
            # Harga di bawah lower Bollinger Band
            if latest['close'] < latest['lowerband']:
                buy_score += 1
            
            # SMA crossover (SMA20 > SMA50)
            if latest['sma20'] > latest['sma50'] and prev['sma20'] <= prev['sma50']:
                buy_score += 1
            
            # Stochastic Oscillator crossover dalam zona oversold
            if latest['slowk'] > latest['slowd'] and latest['slowk'] < 20:
                buy_score += 1
            
            # Hitung skor untuk sinyal SELL
            sell_score = 0
            
            # RSI overbought (di atas 70)
            if latest['rsi'] > 70:
                sell_score += 1
            
            # MACD crossover (MACD < Signal Line)
            if latest['macd'] < latest['macdsignal'] and prev['macd'] >= prev['macdsignal']:
                sell_score += 1
            
            # Harga di atas upper Bollinger Band
            if latest['close'] > latest['upperband']:
                sell_score += 1
            
            # SMA crossover (SMA20 < SMA50)
            if latest['sma20'] < latest['sma50'] and prev['sma20'] >= prev['sma50']:
                sell_score += 1
            
            # Stochastic Oscillator crossover dalam zona overbought
            if latest['slowk'] < latest['slowd'] and latest['slowk'] > 80:
                sell_score += 1
            
            # Tentukan sinyal berdasarkan skor
            max_score = 5  # Skor maksimum
            
            if buy_score > sell_score and buy_score >= 2:
                signal_type = "BUY"
                confidence = (buy_score / max_score) * 100
            elif sell_score > buy_score and sell_score >= 2:
                signal_type = "SELL"
                confidence = (sell_score / max_score) * 100
            
            # Tentukan status indikator
            macd_status = "bullish" if latest['macd'] > latest['macdsignal'] else "bearish"
            ma_status = "uptrend" if latest['sma20'] > latest['sma50'] else "downtrend"
            volume_status = "increasing" if latest['volume'] > df['volume'].mean() else "decreasing"
            
            # Hitung target harga dan stop loss
            atr = talib.ATR(
                np.array(df['high']),
                np.array(df['low']),
                np.array(df['close']),
                timeperiod=14
            )
            latest_atr = atr[-1]
            
            if signal_type == "BUY":
                next_price_target = latest['close'] + (2 * latest_atr)
                stop_loss = latest['close'] - latest_atr
            elif signal_type == "SELL":
                next_price_target = latest['close'] - (2 * latest_atr)
                stop_loss = latest['close'] + latest_atr
            else:
                next_price_target = latest['close'] * 1.01
                stop_loss = latest['close'] * 0.99
            
            # Buat sinyal
            signal = {
                "type": signal_type,
                "price": latest['close'],
                "confidence": confidence,
                "indicators": {
                    "rsi": round(latest['rsi'], 2),
                    "macd": macd_status,
                    "movingAverages": ma_status,
                    "volume": volume_status
                },
                "nextPriceTarget": round(next_price_target, 2),
                "stopLoss": round(stop_loss, 2)
            }
            
            return signal
        
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return None
    
    def place_buy_order(self, quantity=None):
        """Menempatkan order beli"""
        if quantity is None:
            quantity = self.quantity
        
        try:
            # Dalam implementasi nyata, ini akan memanggil API Binance untuk membuat order
            # order = self.client.create_order(
            #     symbol=self.symbol,
            #     side=Client.SIDE_BUY,
            #     type=Client.ORDER_TYPE_MARKET,
            #     quantity=quantity
            # )
            
            # Untuk demo, kita simulasikan order
            current_price = self.get_current_price()
            order = {
                "symbol": self.symbol,
                "side": "BUY",
                "type": "MARKET",
                "quantity": quantity,
                "price": current_price,
                "status": "success",
                "orderId": f"demo-{int(time.time())}",
                "transactTime": int(time.time() * 1000)
            }
            
            logger.info(f"Buy order placed: {order}")
            return order
        
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
            return {"status": "error", "message": str(e)}
    
    def place_sell_order(self, quantity=None):
        """Menempatkan order jual"""
        if quantity is None:
            quantity = self.quantity
        
        try:
            # Dalam implementasi nyata, ini akan memanggil API Binance untuk membuat order
            # order = self.client.create_order(
            #     symbol=self.symbol,
            #     side=Client.SIDE_SELL,
            #     type=Client.ORDER_TYPE_MARKET,
            #     quantity=quantity
            # )
            
            # Untuk demo, kita simulasikan order
            current_price = self.get_current_price()
            order = {
                "symbol": self.symbol,
                "side": "SELL",
                "type": "MARKET",
                "quantity": quantity,
                "price": current_price,
                "status": "success",
                "orderId": f"demo-{int(time.time())}",
                "transactTime": int(time.time() * 1000)
            }
            
            logger.info(f"Sell order placed: {order}")
            return order
        
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")
            return {"status": "error", "message": str(e)}
