import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("dataset/fake_job_postings.csv")

print("=" * 50)
print("DATASET INFORMATION")
print("=" * 50)

print("\nShape of Dataset:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nData Types:")
print(df.dtypes)

print("\nFraudulent Job Distribution:")
print(df["fraudulent"].value_counts())

print("\nPercentage Distribution:")
print(df["fraudulent"].value_counts(normalize=True) * 100)
# -----------------------------
# Bar Chart
# -----------------------------
counts = df["fraudulent"].value_counts()

plt.figure(figsize=(6,4))
plt.bar(["Real Jobs", "Fake Jobs"], counts.values)

plt.title("Real vs Fake Job Postings")
plt.xlabel("Job Type")
plt.ylabel("Number of Jobs")

plt.show()
# -----------------------------
# Pie Chart
# -----------------------------
plt.figure(figsize=(6,6))

plt.pie(
    counts.values,
    labels=["Real Jobs", "Fake Jobs"],
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Distribution of Real and Fake Jobs")

plt.show()
# -----------------------------
# Missing Values Graph
# -----------------------------

missing = df.isnull().sum()
missing = missing[missing > 0]

plt.figure(figsize=(10,5))
missing.sort_values(ascending=False).plot(kind='bar')

plt.title("Missing Values in Dataset")
plt.xlabel("Columns")
plt.ylabel("Number of Missing Values")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
# -----------------------------
# Correlation Heatmap
# -----------------------------

plt.figure(figsize=(8,6))

sns.heatmap(
    df.corr(numeric_only=True),
    annot=True,
    cmap="coolwarm"
)

plt.title("Correlation Heatmap")

plt.show()