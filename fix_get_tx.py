import re

with open('app/services/database_service.py', 'r') as f:
    code = f.read()

code = code.replace('filter(Transaction.id == uuid_obj)', 'filter(Transaction.id == str(uuid_obj))')
# also audit trail
code = code.replace('filter(AuditLog.transaction_id == uuid_obj)', 'filter(AuditLog.transaction_id == str(uuid_obj))')

with open('app/services/database_service.py', 'w') as f:
    f.write(code)
