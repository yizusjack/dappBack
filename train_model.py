import pandas as pd
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv("ishihara_data.csv")

X = df.drop(columns=["Tipo_Daltonismo"])
y = df["Tipo_Daltonismo"]

encoders = {}
for column in X.columns:
    le = LabelEncoder()
    X[column] = le.fit_transform(X[column])
    encoders[column] = le

model = CategoricalNB()

model.fit(X, y)

joblib.dump((model, encoders, X.columns.tolist()), "naive_bayes_model.pkl")
print("Model and encoders saved!")
