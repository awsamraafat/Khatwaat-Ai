import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "raw", "QuestionBank.csv")
df = pd.read_csv(csv_path)

print("Total Rows:", len(df))
print("Columns:", df.columns.tolist())
print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicates (all columns):", df.duplicated().sum())
print("Duplicates (QuestionText):", df.duplicated(subset=['QuestionText']).sum())

print("\nValue Counts for Subject:")
print(df['Subject'].value_counts())

print("\nValue Counts for CorrectAnswer:")
print(df['CorrectAnswer'].value_counts())
