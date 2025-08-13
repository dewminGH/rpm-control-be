from django.db import connections
from django.db.utils import OperationalError

def is_database_connected(alias="default"):
    """
    Returns True if DB connection works, False otherwise.
    """
    try:
        conn = connections[alias]
        conn.cursor()
    except OperationalError:
        return False
    return True
