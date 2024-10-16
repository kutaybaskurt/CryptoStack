from flask import Flask, jsonify, make_response
import psycopg2
import requests
import time
from datetime import datetime
import threading
import flask.json

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="db",  # Using "db" in Docker, instead of "localhost" on local machine
            database="crypto_database",
            user="postgres",
            password="Kutay.21"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# Function to create the database and table
def create_database_and_table():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database, database or table not created.")
        return
    
    cursor = conn.cursor()
    
    # Query to create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS crypto_prices (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        price NUMERIC(18, 8) NOT NULL,
        timestamp TIMESTAMP NOT NULL
    );
    """
    
    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully (or already exists).")
    except psycopg2.Error as e:
        print(f"Table creation error: {e}")
    
    cursor.close()
    conn.close()


# Function to fetch data from Binance API and store it in the database
def fetch_and_store_data():
    symbols = ["BNBBTC", "BNBUSDT", "ETHBTC", "ETHUSDT", "XRPBTC", "XRPUSDT", "BCHBTC", "BCHUSDT", "LTCBTC", "LTCUSDT"]
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    for symbol in symbols:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            price = data['price']
            unix_time = time.time()
            try:
                cursor.execute("INSERT INTO crypto_prices (symbol, price, timestamp) VALUES (%s, %s, to_timestamp(%s))",
                               (symbol, price, unix_time))
                conn.commit()
            except psycopg2.Error as e:
                print(f"Data insertion error {symbol}: {e}")
        else:
            print(f"Data fetch error for {symbol}: {response.status_code}")

    cursor.close()
    conn.close()
    print(f"Data fetch completed: {datetime.now()}")

# Function to return JSON response
def json_response(data):
    response_json = flask.json.dumps(data, ensure_ascii=False)  # ensure_ascii=False to display unicode characters correctly
    return make_response(response_json, 200, {"Content-Type": "application/json"})

# Test route
@app.route('/api/test', methods=['GET'])
def test_route():
    response_data = {"message": "API is working!"}
    return json_response(response_data)

# Route for fetching data from the last 5 minutes
@app.route('/api/<string:symbol>/5min', methods=['GET'])
def get_5min_data(symbol):
    conn = get_db_connection()
    if conn is None:
        return json_response({"error": "Database connection error"})
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, price, timestamp
        FROM crypto_prices
        WHERE symbol = %s
        AND timestamp >= to_timestamp(EXTRACT(EPOCH FROM now()) - 900)
        ORDER BY timestamp ASC
    """, (symbol,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return json_response({"message": "No data found in the last 15 minutes."})

    result = [{"symbol": row[0], "price": row[1], "timestamp": row[2].strftime('%Y-%m-%d %H:%M:%S')} for row in rows]
    return json_response(result)

# Route for average price from the last 60 minutes
@app.route('/api/<string:symbol>/60min', methods=['GET'])
def get_average_price(symbol):
    conn = get_db_connection()
    if conn is None:
        return json_response({"error": "Database connection error"})
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price)
        FROM crypto_prices
        WHERE symbol = %s
        AND timestamp >= to_timestamp(EXTRACT(EPOCH FROM now()) - 3600)
    """, (symbol,))
    avg_price = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if avg_price is None:
        return json_response({'message': "No data found in the last 60 minutes."})

    return json_response({'average_price': avg_price})

# A function that continuously runs with threading to fetch data periodically
def run_data_fetching():
    while True:
        fetch_and_store_data()
        time.sleep(300)

if __name__ == "__main__":
    create_database_and_table()
    data_thread = threading.Thread(target=run_data_fetching)
    data_thread.start()
    app.run(host="0.0.0.0", port=5001)
