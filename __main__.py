from ib_insync import *

TICK_TYPE_MAP = {
    # --- LIVE DATA ---
    0: "Bid Size",
    1: "Live Bid",
    2: "Live Ask",
    3: "Ask Size",
    4: "Live Last Trade",
    5: "Live Last Size",
    6: "Live High",
    7: "Live Low",
    8: "Live Volume",
    9: "Live Close",
    14: "Live Open",
    # --- DELAYED DATA ---
    66: "Delayed Bid",
    67: "Delayed Ask",
    68: "Delayed Last Trade",
    69: "Delayed Last Size",
    72: "Delayed High",
    73: "Delayed Low",
    74: "Delayed Volume",
    75: "Delayed Close",
    76: "Delayed Open",
    # --- OPTIONS & OTHER ---
    24: "Option Implied Vol",
    45: "Last Timestamp",
    84: "Last Exchange",
    86: "Futures Open Interest",
}

# 1. Initialize the IB connection
ib = IB()

# Connect to IB Gateway running on your local machine
# We are using port 4002 (Paper Trading) for safety.
ib.connect("127.0.0.1", 4002, clientId=1)

# 2. Define the stock you want to monitor
contract = Stock("AAPL", "SMART", "USD")

# Validate the contract with IBKR's servers to prevent errors
ib.qualifyContracts(contract)

# 3. Request real-time streaming data
# (This requires those paid live data subscriptions we discussed earlier)
ib.reqMarketDataType(3)
ticker = ib.reqMktData(contract, "", False, False)
print("Waiting for data stream to stabilize...")
ib.sleep(2)

# 4. Define your custom breakout logic
target_breakout_price = 175.50
target_volume_surge = 5000000


# 5. Create a function that triggers every time new market data arrives
def onPendingTickers(tickers):
    for t in tickers:
        if not t.ticks:
            print(f"[{t.contract.symbol}] Received empty tick data. Skipping...")
            continue
        print(f"\n--- 📡 New Data Update for {t.contract.symbol} ---")
        processed_ticks = []

        # 1. Receive and Translate
        for tick in t.ticks:
            tick_name = TICK_TYPE_MAP.get(
                tick.tickType, f"Unknown Tick ({tick.tickType})"
            )

            # Store the data as a tuple: (ID, Name, Price, Size)
            processed_ticks.append((tick.tickType, tick_name, tick.price, tick.size))

        # processed_ticks.sort(key=lambda x: x[0])

        # 3. Print them cleanly formatted
        for tick_id, name, price, size in processed_ticks:
            # We format it to align nicely in the console
            print(f"[{tick_id:02d}] {name:<18} | Price: {price:<8} | Size: {size}")
        # t.last is the live price, t.volume is the total volume for the day
        # print(f"[{t.contract.symbol}] Live Price: ${t.last} | Total Volume: {t.volume}")

        # # This is where your custom 1.5x Volume & Price strategy executes
        # if t.last and t.volume: # Ensure data isn't empty
        #     if t.last > target_breakout_price and t.volume > target_volume_surge:
        #         print("\n🚨 ALERT: Breakout and Volume threshold met! 🚨")
        #         print("Executing logic (e.g., sending an order or a text message)...\n")
        #
        #         # Disconnect or pause here to prevent firing an alert every millisecond
        #         ib.disconnect()
        #         quit()


# 6. Attach your function to the live data event listener
ib.pendingTickersEvent += onPendingTickers

# 7. Keep the script running continuously to listen to the live market tape
print("Streaming live market data... Press Ctrl+C to stop.")

try:
    ib.run()

except KeyboardInterrupt:
    # This block triggers the moment you press Ctrl+C
    print("\n🛑 Ctrl+C detected. Stopping data stream...")

finally:
    # The 'finally' block ensures this cleanup code runs NO MATTER WHAT,
    # whether you pressed Ctrl+C or if the script crashed for another reason.
    if ib.isConnected():
        ib.disconnect()
        print("🔌 Disconnected cleanly from IB Gateway. Goodbye!")
