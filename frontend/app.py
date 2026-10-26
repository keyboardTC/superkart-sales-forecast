
import os

import pandas as pd
import requests
import streamlit as st

# Base URL of the Flask backend (the backend container's name on the Docker network)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

# Features expected by the backend for batch prediction
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]

# Page configuration and title
st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

single_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ---------------- Single prediction ----------------
with single_tab:
    with st.form("single_prediction"):
        st.subheader("Product details")
        col1, col2 = st.columns(2)
        product_weight = col1.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
        product_mrp = col2.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=1.0)
        product_allocated_area = col1.number_input(
            "Allocated display area (ratio)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
        )
        product_sugar_content = col2.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = col1.selectbox(
            "Product code prefix", ["FD", "DR", "NC"], help="FD = food, DR = drinks, NC = non-consumables"
        )
        product_type_category = col2.selectbox("Product type category", ["Non Perishables", "Perishables"])

        st.subheader("Store details")
        col3, col4 = st.columns(2)
        store_type = col3.selectbox(
            "Store type", ["Supermarket Type2", "Supermarket Type1", "Departmental Store", "Food Mart"]
        )
        store_size = col4.selectbox("Store size", ["Medium", "High", "Small"])
        store_location_city_type = col3.selectbox("City tier", ["Tier 2", "Tier 1", "Tier 3"])
        store_age_years = col4.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

        submitted = st.form_submit_button("Predict sales", type="primary")

    if submitted:
        # Create the JSON payload expected by the backend
        product_data = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
            response.raise_for_status()
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted product-store sales total: {predicted_sales:,.2f}")
        except requests.RequestException as error:
            st.error(f"Unable to get a prediction from the API: {error}")

# ---------------- Batch prediction ----------------
with batch_tab:
    st.write("Upload a CSV file with one row per product and these columns:")
    st.code(", ".join(FEATURES))
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write(f"{len(batch_df)} rows loaded")
        st.dataframe(batch_df.head(), use_container_width=True)

        if st.button("Predict for batch", type="primary"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")},
                    timeout=60,
                )
                response.raise_for_status()
                predictions = response.json()

                # Attach the predictions to the uploaded rows (keys are the row positions)
                results_df = batch_df.copy()
                results_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(results_df))]

                st.success("Predictions completed successfully!")
                st.dataframe(results_df, use_container_width=True)
                st.download_button(
                    "Download predictions as CSV",
                    results_df.to_csv(index=False),
                    file_name="superkart_predictions.csv",
                    mime="text/csv",
                )
            except requests.RequestException as error:
                st.error(f"Unable to get predictions from the API: {error}")
