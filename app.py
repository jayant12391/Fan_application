from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)


# More configuration and routes...
# Database connection
conn = psycopg2.connect("dbname=Newdb user=jayant password=123456 host=Newdb")
cur = conn.cursor()

@app.route('/fan', methods=['POST'])
def update_fan_status():
    data = request.json
    status = data['status']
    speed_level = data['speed_level']
    
    # Insert fan status log into the database
    cur.execute("INSERT INTO fan_status_logs (status, speed_level) VALUES (%s, %s)", (status, speed_level))
    conn.commit()
    
    return jsonify({"message": "Fan status updated"}), 200

@app.route('/power-consumption', methods=['GET'])
def get_power_consumption():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    # Fetch logs between the requested times
    cur.execute("SELECT * FROM fan_status_logs WHERE timestamp BETWEEN %s AND %s", (start_time, end_time))
    logs = cur.fetchall()
    
    total_energy = 0
    
    for log in logs:
        timestamp, status, speed_level = log[1], log[2], log[3]
        
        if status:
            cur.execute("SELECT current FROM fan_specifications WHERE speed_level = %s", (speed_level,))
            current = cur.fetchone()[0]
            voltage = 220
            power_factor = 0.8
            power = current * voltage * power_factor
            duration = (datetime.now() - timestamp).total_seconds() / 3600  # in hours
            energy = power * duration
            total_energy += energy
    
    return jsonify({
        "power_consumption": power,
        "energy_consumption": total_energy
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
