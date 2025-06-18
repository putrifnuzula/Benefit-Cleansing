import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

# Function to filter data based on ClaimStatus
def filter_data(df):
    st.write("Filtering data where 'ClaimStatus' is 'R'...")
    if 'Status_Claim' not in df.columns:
        st.error("The column 'ClaimStatus' is missing from the uploaded file.")
        return pd.DataFrame()

    st.write(df['Status_Claim'].value_counts())
    df = df[df['Status_Claim'] == 'R']
    return df

# Main processing function
def move_to_template(df):
    # Step 1: Filter the data
    new_df = filter_data(df)
    if new_df.empty:
        st.error("No data left after filtering. Please check the input file.")
        return pd.DataFrame()

    # Step 2: Convert date columns to datetime
    date_columns = ["TreatmentStart", "TreatmentFinish", "PaymentDate"]
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
        "Diagnosis", "PaymentDate", "Billed", "Accepted",
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
        "Diagnosis": new_df["Diagnosis"],
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


# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    raw_data = pd.read_csv(uploaded_file)
    
    # Process data
    st.write("Processing data...")
    transformed_data = move_to_template(raw_data)
    
    # Show a preview of the transformed data
    st.write("Transformed Data Preview:")
    st.dataframe(transformed_data.head())

    # Compute summary statistics
    total_claims = len(transformed_data)
    total_billed = int(transformed_data["Sum of Billed"].sum())
    total_accepted = int(transformed_data["Sum of Accepted"].sum())
    total_excess = int(transformed_data["Sum of Excess Total"].sum())
    total_unpaid = int(transformed_data["Sum of Unpaid"].sum())

    st.write("Claim Summary:")
    st.write(f"- Total Claims: {total_claims:,}")
    st.write(f"- Total Billed: {total_billed:,.2f}")
    st.write(f"- Total Accepted: {total_accepted:,.2f}")
    st.write(f"- Total Excess: {total_excess:,.2f}")
    st.write(f"- Total Unpaid: {total_unpaid:,.2f}")

    # User input for filename
    filename = st.text_input("Enter the Excel file name (without extension):", "Transformed_Claim_Data")

    # Download link for the Excel file
    if filename:
        excel_file, final_filename = save_to_excel(transformed_data, filename=filename + ".xlsx")
        st.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name=final_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
