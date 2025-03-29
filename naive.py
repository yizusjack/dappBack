import joblib
import pandas as pd

model, encoders, feature_names = joblib.load("naive_bayes_model.pkl")

def getResult(sample_input):
    input_df = pd.DataFrame([sample_input], columns=feature_names)

    for col in input_df.columns:
        le = encoders[col]
        input_df[col] = le.transform(input_df[col])

    prediction = model.predict(input_df)

    return prediction[0]
