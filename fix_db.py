with open('app/services/database_service.py', 'r') as f:
    code = f.read()

code = code.replace('''        except Exception as e:
            print(f"Warning: Could not create transaction: {e}")
            # Return a transaction object with generated ID for consistency''', '''        except Exception as e:
            print(f"Warning: Could not create transaction: {e}")
            raise e''')

with open('app/services/database_service.py', 'w') as f:
    f.write(code)
