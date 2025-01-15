from models import User
import hashlib
from dotenv import load_dotenv
import os
load_dotenv()

m = hashlib.sha256()
m.update(os.getenv('USER_PASSWORD').encode('utf8'))

def userSeed():
    User.create(
        username = "daltonicapp",
        password = m.hexdigest()
    )