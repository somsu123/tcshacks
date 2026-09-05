import re

with open('app/db_models.py', 'r') as f:
    code = f.read()

code = code.replace('payee = Column(String(255), nullable=False, index=True)', 'payee = Column(String(255), nullable=False, index=True)\n    payee_is_new = Column(Boolean, default=False)')

with open('app/db_models.py', 'w') as f:
    f.write(code)
