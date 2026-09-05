import re

with open('app/services/anomaly_detector.py', 'r') as f:
    code = f.read()
if 'timezone' not in code:
    code = code.replace('from datetime import datetime', 'from datetime import datetime, timezone')

with open('app/services/anomaly_detector.py', 'w') as f:
    f.write(code)

with open('app/main.py', 'r') as f:
    main_code = f.read()

# Fix the risk_factors cache logic in main.py
# "risk_factors_detailed": explanation_data.get("risk_factors"),
main_code = main_code.replace('"risk_factors_detailed": explanation_data.get("risk_factors"),', '"risk_factors_detailed": explanation_data.get("risk_factors", []),')

# transaction.risk_factors_detailed or []
main_code = main_code.replace('"risk_factors": transaction.risk_factors_detailed or [],', '"risk_factors": transaction.risk_factors_detailed or [],')

with open('app/main.py', 'w') as f:
    f.write(main_code)
