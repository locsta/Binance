import websocket, json, pprint, talib
import numpy as np
from binance.client import Client
from binance.enums import *
import config

# https://pypi.org/project/websocket-client/
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 2
RSI_OVERBOUGHT = 40
RSI_OVERSOLD = 37
TRADE_SYMBOL = "ETHUSD"
TRADE_QUANTITY = 0.05

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_test_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        return True
    except Exception as e:
        return False


return_value = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
print(f"Return value {return_value}")
# info = client.get_account()
# pprint.pprint(info)

status = client.get_account_api_trading_status()
pprint.pprint(status)
quit()


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    # close = json_message['k']['x']
    # print(f"close: {close}")
    # exit()

    if is_candle_closed:
        print(f"candle closed at {close}")
        closes.append(float(close))
        # print("closes")
        # print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsi calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print(f"the current rsi is {last_rsi}")

            if last_rsi > RSI_OVERBOUGHT:
                print("OVERBOUGHT")
                if in_position:
                    print("Sell! Sell!, Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                        ws.keep_running = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                print("OVERSOLD")
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Buy! Buy! Buy!")
                    # put binance order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
                        ws.keep_running = False
        # quit()

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()