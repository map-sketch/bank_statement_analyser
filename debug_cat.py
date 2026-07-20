import pandas as pd
from core.services.categorization import engine

try:
    df = pd.read_csv('combined_training_data.csv')
    print('Training data categories:')
    print(df['category'].value_counts())
except Exception as e:
    print('Error reading training data:', e)

test_cases = [
    ('UPI/Uber/TXN1234', 'DEBIT'),
    ('Electricity Bill', 'DEBIT'),
    ('Amazon Shopping', 'DEBIT'),
    ('Random unseen txn', 'DEBIT')
]

print('\nCategorization tests:')
for desc, ttype in test_cases:
    cat, conf, method = engine.categorize(desc, ttype)
    print(f'{desc!r} -> {cat} ({conf}, {method})')
