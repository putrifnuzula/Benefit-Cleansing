import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

# Function to filter data based on ClaimStatus
def filter_data(df):
    st.write("Filtering data where 'ClaimStatus' is 'R'...")
    if 'ClaimStatus' not in df.columns:
        st.error("The column 'ClaimStatus' is missing from the uploaded file.")
        return pd.DataFrame()

    st.write(df['ClaimStatus'].value_counts())
    df = df[df['ClaimStatus'] == 'R']
    return df

# Main processing function
def move_to_template(df):
    # Step 1: Filter the data
    new_df = filter_data(df)
    if new_df.empty:
        st.error("No data left after filtering. Please check the input file.")
        return pd.DataFrame()

    # Step 2: Convert date columns to datetime
    date_columns = ["TreatmentStart", "TreatmentFinish", "Date", "PaymentDate"]
    for col in date_columns:
        if col in new_df.columns:
            new_df[col] = pd.to_datetime(new_df[col], errors='coerce')
            if new_df[col].isnull().any():
                st.warning(f"Invalid date values detected in column '{col}'. Coerced to NaT.")

    # Step 3: Transform to the new template
    required_columns = [
        "ClientName", "PolicyNo", "ClaimNo", "MemberNo", "Membership", "PatientName",
        "EmpID", "EmpName", "ClaimType", "ProductType", "RoomOption",
        "TreatmentRoomClass", "TreatmentPlace", "TreatmentStart", "TreatmentFinish",
        "PrimaryDiagnosis", "PaymentDate", "Billed", "Accepted",
        "ExcessCoy", "ExcessEmp", "ExcessTotal", "Unpaid"
    ]

    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in new_df.columns]
    if missing_columns:
        st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
        return pd.DataFrame()

    # Create transformed DataFrame
    df_transformed = pd.DataFrame({
        "No": range(1, len(new_df) + 1),
        "Client Name": new_df["ClientName"],
        "Policy No": new_df["PolicyNo"],
        "Claim No": new_df["ClaimNo"],
        "Member No": new_df["MemberNo"],
        "Membership": new_df["Membership"],
        "Patient Name": new_df["PatientName"],
        "Emp ID": new_df["EmpID"],
        "Emp Name": new_df["EmpName"],
        "Claim Type": new_df["ClaimType"],
        "Product Type": new_df["ProductType"],
        "Room Option": new_df["RoomOption"],
        "Treatment Room Class": new_df["TreatmentRoomClass"],
        "Treatment Place": new_df["TreatmentPlace"],
        "Treatment Start": new_df["TreatmentStart"],
        "Treatment Finish": new_df["TreatmentFinish"],
        "Diagnosis": new_df["PrimaryDiagnosis"],
        "Payment Date": new_df["PaymentDate"],
        "Billed": new_df["Billed"],
        "Accepted": new_df["Accepted"],
        "Excess Coy": new_df["ExcessCoy"],
        "Excess Emp": new_df["ExcessEmp"],
        "Excess Total": new_df["ExcessTotal"],
        "Unpaid": new_df["Unpaid"],
    })

    return df_transformed

# Save the processed data to Excel and return as BytesIO
def save_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Benefit Claim')
    output.seek(0)
    return output

# Streamlit app
st.title("Benefit Claim Data Processor")

# File uploader
uploaded_file = st.file_uploader("Upload your Benefit Claim CSV file", type=["csv"])
if uploaded_file:
    try:
        raw_data = pd.read_csv(uploaded_file)

        # Process data
        st.write("Processing data...")
        transformed_data = move_to_template(raw_data)

        if not transformed_data.empty:
            # Show a preview of the transformed data
            st.write("Transformed Data Preview:")
            st.dataframe(transformed_data.head())

            # Download link for the Excel file
            st.write("Download the transformed data as an Excel file:")
            excel_file = save_to_excel(transformed_data)
            st.download_button(
                label="Download Excel File",
                data=excel_file,
                file_name="Transformed_Benefit_Claim_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("The transformed data is empty. Please check the input file.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")