import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_spending(df):
    if len(df) < 2:
        return "Not enough data"
    
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    
    monthly = df.groupby('month')['amount'].sum().reset_index()
    
    X = monthly[['month']]
    y = monthly['amount']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Handle next month properly
    next_month = monthly['month'].max() + 1
    if next_month > 12:
        next_month = 1

    prediction = model.predict(np.array([[next_month]]))
    
    return round(prediction[0], 2)
