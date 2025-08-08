from django.http import HttpResponse
import pandas as pd
import numpy as np
import joblib
import os

def home(request):
    print(os.getcwd())
    model_path_cat_booster = os.path.join(os.path.dirname(__file__), 'logistic_catboost_model_V4.pkl')
    cat_booster = joblib.load(model_path_cat_booster)
    print(cat_booster)
    predictions = cat_booster.predict([[34.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    print("np",np.__version__,"pd",pd.__version__,"pred",predictions)
    cat_booster.predict([[32.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds1 = cat_booster.predict([[29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds2 = cat_booster.predict([[30.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds3 = cat_booster.predict([[32.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    preds4 = cat_booster.predict([[34.29, 88.00, 3014.35, 386.86, 1, 0, 0, 0, 0]])
    # Print predictions and CatBoost version
    print(preds1,preds2,preds3,preds4)
    return HttpResponse("Hello, world!",preds1 )
