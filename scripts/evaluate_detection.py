import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def evaluate():
    from app.services.anomaly_detector import get_anomaly_detector
    
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'data', 'synthetic_transactions.json')
    if not os.path.exists(json_path):
        print("Dataset not found. Please run generate_synthetic_transactions.py first.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        transactions = json.load(f)
        
    detector = get_anomaly_detector()
    
    # Build history
    account_histories = {}
    
    total_injected = 0
    injected_detected = 0
    total_clean = 0
    clean_flagged = 0
    
    scenario_stats = {}
    
    for txn in transactions:
        acc = txn['account_id']
        hist = account_histories.get(acc, [])
        
        try:
            score, factors = detector.calculate_risk_score(txn, hist)
        except Exception:
            score = 0.0
            
        label = txn.get('injected_label')
        is_fraud = label is not None
        is_flagged = score >= 0.4  # Assuming >=0.4 is medium/high risk
        
        if is_fraud:
            total_injected += 1
            if label not in scenario_stats:
                scenario_stats[label] = {'total': 0, 'detected': 0}
            scenario_stats[label]['total'] += 1
            
            if is_flagged:
                injected_detected += 1
                scenario_stats[label]['detected'] += 1
        else:
            total_clean += 1
            if is_flagged:
                clean_flagged += 1
                
        # Add to history for subsequent transactions
        hist.append({
            'amount': txn['amount'],
            'timestamp': txn['timestamp'],
            'location_lat': txn['location_lat'],
            'location_lon': txn['location_lon'],
            'location_country': txn['location_country']
        })
        account_histories[acc] = hist
        
    print(f"Total Transactions Evaluated: {len(transactions)}")
    print(f"Total Injected Fraud: {total_injected}")
    print(f"Total Clean: {total_clean}")
    print("-" * 40)
    
    if total_injected > 0:
        det_rate = (injected_detected / total_injected) * 100
        print(f"Overall Detection Rate: {det_rate:.2f}% ({injected_detected}/{total_injected})")
    
    if total_clean > 0:
        fp_rate = (clean_flagged / total_clean) * 100
        print(f"False Positive Rate: {fp_rate:.2f}% ({clean_flagged}/{total_clean})")
        
    print("-" * 40)
    print("Scenario Breakdown:")
    for sc, stats in scenario_stats.items():
        rate = (stats['detected'] / stats['total']) * 100
        print(f"  {sc}: {rate:.2f}% ({stats['detected']}/{stats['total']})")

if __name__ == '__main__':
    evaluate()
