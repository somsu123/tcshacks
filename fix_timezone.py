import re
with open('app/services/anomaly_detector.py', 'r') as f:
    code = f.read()

if 'from datetime import timezone' not in code:
    code = code.replace('from datetime import datetime', 'from datetime import datetime, timezone')

with open('app/services/anomaly_detector.py', 'w') as f:
    f.write(code)
