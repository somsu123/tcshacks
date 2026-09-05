import re

with open('app/services/anomaly_detector.py', 'r') as f:
    code = f.read()

# Replace parsing logic to make sure we always have offset-aware
new_ts_logic = '''
            if isinstance(tx_time, str):
                tx_time = datetime.fromisoformat(tx_time.replace("Z", "+00:00"))
            elif tx_time.tzinfo is None:
                tx_time = tx_time.replace(tzinfo=timezone.utc)
'''
code = re.sub(r'if isinstance\(tx_time, str\):\s*tx_time = datetime.fromisoformat\(tx_time\.replace\("Z", "\+00:00"\)\)', new_ts_logic.strip(), code)

new_hist_logic = '''
                if isinstance(hist_time, str):
                    hist_time = datetime.fromisoformat(hist_time.replace("Z", "+00:00"))
                elif hist_time.tzinfo is None:
                    hist_time = hist_time.replace(tzinfo=timezone.utc)
'''
code = re.sub(r'if isinstance\(hist_time, str\):\s*hist_time = datetime.fromisoformat\(hist_time\.replace\("Z", "\+00:00"\)\)', new_hist_logic.strip(), code)

# Let's fix for parsed_timestamp as well
new_parsed_logic = '''
        parsed_timestamp = None
        if timestamp:
            if isinstance(timestamp, str):
                parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                parsed_timestamp = timestamp
                if parsed_timestamp.tzinfo is None:
                    parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
'''
code = re.sub(r'parsed_timestamp = None\s*if timestamp:\s*if isinstance\(timestamp, str\):\s*parsed_timestamp = datetime.fromisoformat\(timestamp\.replace\("Z", "\+00:00"\)\)\s*else:\s*parsed_timestamp = timestamp', new_parsed_logic.strip(), code)

with open('app/services/anomaly_detector.py', 'w') as f:
    f.write(code)
