import streamlit as st
import pandas as pd

st.set_page_config(page_title = "Join Excel", page_icon = "📝")

st.title('Join Excel Files')
st.write("Please select the columns to join on from each Excel file. The first file should be the one with the students (alumnos de Studium).")

# Upload the first Excel file
uploaded_file1 = st.file_uploader("Choose the first Excel file (students)", type="xlsx")
if uploaded_file1 is not None:
    df1 = pd.read_excel(uploaded_file1)
    st.write("First Excel file (students):")
    st.write(df1)
    column1 = st.selectbox("Select the column to join on from the first Excel file", df1.columns)
    new_name1 = st.text_input("Enter new name for the join column from first file", value=column1)

# Upload the second Excel file
uploaded_file2 = st.file_uploader("Choose the second Excel file", type="xlsx")
if uploaded_file2 is not None:
    df2 = pd.read_excel(uploaded_file2)
    st.write("Second Excel file:")
    st.write(df2)
    column2 = st.selectbox("Select the column to join on from the second Excel file", df2.columns)
    new_name2 = st.text_input("Enter new name for the join column from second file", value=column2)

# Perform the join operation when the button is clicked
if uploaded_file1 is not None and uploaded_file2 is not None and column1 and column2:
    if st.button('Join Files'):
        # Rename columns before merging
        df1 = df1.rename(columns={column1: new_name1})
        df2 = df2.rename(columns={column2: new_name2})
        
        merged_df = pd.merge(df1, df2, how='left', left_on=new_name1, right_on=new_name2)
        st.write("Merged Excel file:")
        st.write(merged_df)

        # Download the merged Excel file
        merged_file = 'merged_file.xlsx'
        merged_df.to_excel(merged_file, index=False)
        with open(merged_file, 'rb') as f:
            st.download_button('Download Merged Excel File', f, file_name=merged_file)
            # Inform the user with a summary
            total_records = len(merged_df)
            joined_records = merged_df[new_name2].notna().sum()
            not_joined_records = len(df1) - joined_records

            st.write(f"Total records first document: {total_records}")
            st.write(f"Total records second document: {len(df2)}")
            st.write(f"Joined records: {joined_records}")
            st.write(f"Records in the first Excel file not joined: {not_joined_records}")