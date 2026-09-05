import json
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

def generate_and_load(db_session=None):
    num_normal = 285
    num_accounts = 30
    accounts = [f"SYNTH-{i:03d}" for i in range(1, num_accounts+1)]
    locations = [
        {"country": "GB", "lat": 51.5074, "lon": -0.1278, "name": "London"},
        {"country": "GB", "lat": 53.4808, "lon": -2.2426, "name": "Manchester"},
        {"country": "GB", "lat": 52.4862, "lon": -1.8904, "name": "Birmingham"},
        {"country": "FR", "lat": 48.8566, "lon": 2.3522, "name": "Paris"},
        {"country": "DE", "lat": 52.5200, "lon": 13.4050, "name": "Berlin"}
    ]
    
    payees = ["Tesco", "Sainsburys", "Amazon", "Uber", "Deliveroo", "Netflix", "Spotify", "Vodafone", "O2", "EE"]
    
    transactions = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    def random_time(start, end, business_hours=True):
        while True:
            delta = end - start
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            random_second = random.randrange(int_delta)
            dt = start + timedelta(seconds=random_second)
            if business_hours:
                if 8 <= dt.hour <= 20:
                    return dt
            else:
                return dt

    for _ in range(num_normal):
        acc = random.choice(accounts)
        loc = random.choice(locations)
        dt = random_time(base_time, datetime.utcnow())
        
        txn = {
            "id": f"syn_{uuid.uuid4().hex[:8]}",
            "account_id": acc,
            "amount": round(random.uniform(10.0, 500.0), 2),
            "payee": random.choice(payees),
            "payee_is_new": random.random() < 0.1,
            "timestamp": dt.isoformat() + "Z",
            "reference": f"REF-{random.randint(1000, 9999)}",
            "location_country": loc["country"],
            "location_lat": loc["lat"],
            "location_lon": loc["lon"],
            "injected_label": None
        }
        transactions.append(txn)
    
    # 3x Impossible travel
    for _ in range(3):
        acc = random.choice(accounts)
        dt1 = random_time(base_time, datetime.utcnow())
        dt2 = dt1 + timedelta(minutes=random.randint(5, 10))
        
        txn1 = {
            "id": f"syn_it1_{uuid.uuid4().hex[:8]}",
            "account_id": acc,
            "amount": round(random.uniform(50.0, 150.0), 2),
            "payee": random.choice(payees),
            "payee_is_new": False,
            "timestamp": dt1.isoformat() + "Z",
            "reference": f"REF-{random.randint(1000, 9999)}",
            "location_country": "JP",
            "location_lat": 35.6762,
            "location_lon": 139.6503,
            "injected_label": "impossible_travel"
        }
        txn2 = {
            "id": f"syn_it2_{uuid.uuid4().hex[:8]}",
            "account_id": acc,
            "amount": round(random.uniform(50.0, 150.0), 2),
            "payee": random.choice(payees),
            "payee_is_new": False,
            "timestamp": dt2.isoformat() + "Z",
            "reference": f"REF-{random.randint(1000, 9999)}",
            "location_country": "IN",
            "location_lat": 22.5726,
            "location_lon": 88.3639,
            "injected_label": "impossible_travel"
        }
        transactions.extend([txn1, txn2])
        
    # 4x Amount spike
    for _ in range(4):
        acc = random.choice(accounts)
        dt = random_time(base_time, datetime.utcnow())
        loc = random.choice(locations)
        txn = {
            "id": f"syn_spk_{uuid.uuid4().hex[:8]}",
            "account_id": acc,
            "amount": round(random.uniform(5000.0, 10000.0), 2),
            "payee": "Luxury Goods Inc",
            "payee_is_new": True,
            "timestamp": dt.isoformat() + "Z",
            "reference": f"REF-{random.randint(1000, 9999)}",
            "location_country": loc["country"],
            "location_lat": loc["lat"],
            "location_lon": loc["lon"],
            "injected_label": "amount_spike"
        }
        transactions.append(txn)
        
    # 2x Velocity burst
    for _ in range(2):
        acc = random.choice(accounts)
        dt = random_time(base_time, datetime.utcnow())
        loc = random.choice(locations)
        for j in range(5):
            txn = {
                "id": f"syn_vel_{uuid.uuid4().hex[:8]}",
                "account_id": acc,
                "amount": round(random.uniform(20.0, 100.0), 2),
                "payee": random.choice(payees),
                "payee_is_new": False,
                "timestamp": (dt + timedelta(minutes=j)).isoformat() + "Z",
                "reference": f"REF-{random.randint(1000, 9999)}",
                "location_country": loc["country"],
                "location_lat": loc["lat"],
                "location_lon": loc["lon"],
                "injected_label": "velocity_burst"
            }
            transactions.append(txn)
            
    # 1x Combined
    acc = random.choice(accounts)
    dt = base_time.replace(hour=3, minute=15) + timedelta(days=random.randint(1, 28))
    loc = random.choice(locations)
    txn = {
        "id": f"syn_cmb_{uuid.uuid4().hex[:8]}",
        "account_id": acc,
        "amount": round(random.uniform(8000.0, 12000.0), 2),
        "payee": "Unknown Offshore Entity",
        "payee_is_new": True,
        "timestamp": dt.isoformat() + "Z",
        "reference": f"REF-{random.randint(1000, 9999)}",
        "location_country": loc["country"],
        "location_lat": loc["lat"],
        "location_lon": loc["lon"],
        "injected_label": "combined"
    }
    transactions.append(txn)
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    
    # Write to files
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, 'app', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    json_path = os.path.join(data_dir, 'synthetic_transactions.json')
    csv_path = os.path.join(data_dir, 'synthetic_transactions.csv')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=2)
        
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)
        
    if db_session:
        from app.services.database_service import db_service
        count = 0
        for txn in transactions:
            db_service.create_transaction(
                db_session,
                account_id=txn['account_id'],
                amount=txn['amount'],
                payee=txn['payee'],
                timestamp=datetime.fromisoformat(txn['timestamp'].replace('Z', '+00:00')),
                reference=txn['reference'],
                payee_is_new=txn['payee_is_new'],
                location_country=txn['location_country'],
                location_lat=txn['location_lat'],
                location_lon=txn['location_lon'],
                risk_score=0.0,
                risk_level='low',
                factors=[]
            )
            count += 1
        return count
        
    return len(transactions)

if __name__ == '__main__':
    count = generate_and_load()
    print(f"Generated {count} synthetic transactions.")
