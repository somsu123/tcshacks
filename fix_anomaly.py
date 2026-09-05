import re

with open('app/services/anomaly_detector.py', 'r') as f:
    code = f.read()

# Just remove the second duplicate block
code = re.sub(r'# Factor 5: GEO_VELOCITY.*?(?=# Factor 6: VELOCITY)', '', code, flags=re.DOTALL)
code = re.sub(r'# Factor 6: VELOCITY.*?return min\(score, 1\.0\), factors', 'return min(score, 1.0), factors', code, flags=re.DOTALL)

with open('app/services/anomaly_detector.py', 'w') as f:
    f.write(code)
