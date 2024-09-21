import pandas as pd
import numpy as np

def generate_financial_data():
    data = {
        'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
        'Revenue': np.random.uniform(100000, 200000, 12),
        'Cost of Goods Sold': np.random.uniform(50000, 100000, 12),
        'Operating Expenses': np.random.uniform(20000, 50000, 12),
    }
    df = pd.DataFrame(data)
    df['Gross Profit'] = df['Revenue'] - df['Cost of Goods Sold']
    df['Net Income'] = df['Gross Profit'] - df['Operating Expenses']
    return df
