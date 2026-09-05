import re

with open('tests/test_api/test_validation.py', 'r') as f:
    code = f.read()

# Add account_id to all data payloads where it's missing
code = re.sub(r'data = \{(.*?)\}', r'data = {"account_id": "TEST-123", \1}', code)

with open('tests/test_api/test_validation.py', 'w') as f:
    f.write(code)

with open('tests/test_api/test_transactions.py', 'r') as f:
    code = f.read()

# I also need to fix test_get_transaction_detail_includes_explanation
# The risk_factors is detailed, wait, why did it fail?
# KeyError: 'risk_factors'
# Let's check app/main.py around line 363 for explanation_data["risk_factors"]
# The dictionary from explanation_data has "risk_factors", wait. Let's see.
