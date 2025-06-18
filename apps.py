import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

# Function to filter data based on ClaimStatus
def filter_data(df):
    st.write("Filtering data where 'Status Claim' is 'R'...")
    if 'Status Claim' not in df.columns:
        st.error("The column 'ClaimStatus' is missing from the uploaded file.")
        return pd.DataFrame()

    st.write(df['Status Claim'].value_counts())
    df = df[df['Status Claim'] == 'R']
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
        "Client Name", "Policy No", "Claim No", "Member No", "Membership", "Patient Name",
        "Emp ID", "Emp Name", "Claim Type", "Product Type", "Room Option",
        "Treatment Room Class", "Treatment Place", "Treatment Start", "Treatment Finish",
        "Diagnosis", "Payment Date", "Billed", "Accepted",
        "Excess Coy", "Excess Emp", "Excess Total", "Unpaid"
    ]

    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in new_df.columns]
    if missing_columns:
        st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
        return pd.DataFrame()

    # Create transformed DataFrame
    df_transformed = pd.DataFrame({
        "No": range(1, len(new_df) + 1),
        "Client Name": new_df["Client Name"],
        "Policy No": new_df["Policy No"],
        "Claim No": new_df["Claim No"],
        "Member No": new_df["Member No"],
        "Membership": new_df["Membership"],
        "Patient Name": new_df["Patient Name"],
        "Emp ID": new_df["Emp ID"],
        "Emp Name": new_df["Emp Name"],
        "Claim Type": new_df["Claim Type"],
        "Product Type": new_df["Product Type"],
        "Room Option": new_df["Room Option"],
        "Treatment Room Class": new_df["Treatment Room Class"],
        "Treatment Place": new_df["Treatment Place"],
        "Treatment Start": new_df["Treatment Start"],
        "Treatment Finish": new_df["Treatment Finish"],
        "Diagnosis": new_df["Diagnosis"],
        "Payment Date": new_df["Payment Date"],
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
