import re

def contains_illegal(str):
    if re.search(r'[,\\,\\.\\/\\;]', str):
        return True
    else:
        return False