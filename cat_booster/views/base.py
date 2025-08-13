from django.http import HttpResponse
import pandas as pd
import numpy as np
from utils.db_connection_doc import is_database_connected
from ..services.boot_model import get_model

def home(request):
    """
    Test route AI
    """
    cat_booster =get_model()
    print(cat_booster)
    predictions = cat_booster.predict([[34.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    print("np",np.__version__,"pd",pd.__version__,"pred",predictions)
    cat_booster.predict([[32.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds1 = cat_booster.predict([[29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds2 = cat_booster.predict([[30.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds3 = cat_booster.predict([[32.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds4 = cat_booster.predict([[34.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    db_connection_status= is_database_connected()
    return HttpResponse(f"[DEBUG] DB_CONNECTION {db_connection_status} [DEBUG] TEST samples {preds1} {preds2} {preds3} {preds4}" )
