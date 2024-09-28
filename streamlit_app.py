import streamlit as st
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
import os

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# Initialize PandasAI with OpenAI
llm = OpenAI()
pandas_ai = PandasAI(llm)

def main():
    st.set_page_config(page_title="CSV Data Cleaning with PandasAI", layout="wide")

    st.title("CSV Data Cleaning with PandasAI")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Display original dataframe
        st.subheader("Original Data")
        st.dataframe(df.head())

        # Display dataframe info
        st.subheader("Data Info")
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

        # PandasAI cleaning options
        st.subheader("Data Cleaning Options")

        cleaning_option = st.selectbox(
            "Choose a cleaning operation",
            [
                "Remove duplicates",
                "Handle missing values",
                "Convert data types",
                "Remove outliers",
                "Custom cleaning prompt"
            ]
        )

        if cleaning_option == "Remove duplicates":
            prompt = "Remove duplicate rows from the dataframe"
        elif cleaning_option == "Handle missing values":
            method = st.selectbox("Choose method", ["Drop", "Fill with mean", "Fill with median", "Fill with mode"])
            prompt = f"Handle missing values in the dataframe by {method.lower()}"
        elif cleaning_option == "Convert data types":
            column = st.selectbox("Choose column", df.columns)
            new_type = st.selectbox("Choose new data type", ["int", "float", "string", "datetime"])
            prompt = f"Convert the '{column}' column to {new_type} data type"
        elif cleaning_option == "Remove outliers":
            column = st.selectbox("Choose column", df.columns)
            prompt = f"Remove outliers from the '{column}' column using the IQR method"
        else:
            prompt = st.text_input("Enter your custom cleaning prompt")

        if st.button("Clean Data"):
            with st.spinner("Cleaning data..."):
                try:
                    cleaned_df = pandas_ai.run(df, prompt)
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_df.head())

                    # Compare original and cleaned dataframes
                    st.subheader("Data Comparison")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Original Data Shape:", df.shape)
                    with col2:
                        st.write("Cleaned Data Shape:", cleaned_df.shape)

                    # Option to download cleaned data
                    csv = cleaned_df.to_csv(index=False)
                    st.download_button(
                        label="Download cleaned data as CSV",
                        data=csv,
                        file_name="cleaned_data.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
