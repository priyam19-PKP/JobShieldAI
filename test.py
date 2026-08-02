import pandas as pd

# Load dataset
df = pd.read_csv("dataset/fake_job_postings.csv")

# Show first 5 rows
print("First 5 Rows:")
print(df.head())

# Dataset shape
print("\nDataset Shape:")
print(df.shape)

# Column names
print("\nColumns:")
print(df.columns)

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Target variable distribution
print("\nFraudulent Jobs:")
print(df["fraudulent"].value_counts())