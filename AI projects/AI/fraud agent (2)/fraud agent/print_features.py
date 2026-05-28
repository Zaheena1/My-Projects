import joblib

bundle = joblib.load("model_bundle (5).pkl")
print(bundle["feature_order"])
