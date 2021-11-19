"""

# Project:
# Author: justforstar
# CreateTime: 2021/4/14 下午3:55
# Function:

"""
import hashlib
import random
import string


def genhashpassword(str, salt):
    sha256 = hashlib.sha256()
    sha256.update((str + salt).encode('utf-8'))
    res = sha256.hexdigest()
    return res


def verificationcodegenerator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
