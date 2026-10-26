
# Import the necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask app with a name
superkart_api = Flask("SuperKart")

# Keep the response keys in the order of the input rows (Flask sorts keys by default)
superkart_api.json.sort_keys = False

# Load the trained model pipeline (preprocessing + regressor) once at start-up
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the same form as used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (also used as a health check)
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# Define an endpoint to predict the sales of a single product in a store
@superkart_api.post("/v1/predict")
def predict_sales():
    # Get the JSON data from the request
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Make sure that every feature required by the model is present
    missing = [feature for feature in FEATURES if feature not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Convert the extracted features into a single-row DataFrame
    input_data = pd.DataFrame([{feature: data[feature] for feature in FEATURES}])

    # Make a prediction using the trained model
    prediction = float(model.predict(input_data)[0])

    # Return the prediction as a JSON response
    return jsonify({"Sales": round(prediction, 2)})


# Define an endpoint to predict the sales of a batch of products uploaded as a CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file using the 'file' field"}), 400

    # Read the file into a DataFrame
    input_data = pd.read_csv(request.files["file"])

    # Make sure that every feature required by the model is present
    missing = [feature for feature in FEATURES if feature not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Make predictions for all the rows
    predictions = model.predict(input_data[FEATURES])

    # Map each row index to its predicted sales
    output = {str(i): round(float(pred), 2) for i, pred in enumerate(predictions)}
    return jsonify(output)


# Run the Flask app locally (inside Docker the app is served by Gunicorn instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
