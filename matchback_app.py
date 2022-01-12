import streamlit as st
import pandas as pd


@st.cache
def convert_df(df):
    return df.to_csv().encode("utf-8")


def create_matches():
    if prospect_file is None or customer_file is None:
        st.error("Please select prospect and/or customer file")
    # elif save_path == "" or file_name == "":
    #    st.error("Please enter save path and/or file name")
    elif "person_hash" in [
        prosp_addr,
        prosp_ln,
        prosp_zip,
        cust_addr,
        cust_ln,
        cust_zip,
    ]:
        st.error("Please select prospect and customer columns")
    else:
        prospects["jr_string"] = prospects.apply(
            lambda row: str(row[prosp_addr]).lower().strip()[:10]
            + str(row[prosp_ln]).lower().strip()[:2]
            + str(int(float(row[prosp_zip]))),
            axis=1,
        )
        customers["jr_string"] = customers.apply(
            lambda row: str(row[cust_addr]).lower().strip()[:10]
            + str(row[cust_ln]).lower().strip()[:2]
            + str(int(float(row[cust_zip]))),
            axis=1,
        )
        jr_matches = prospects.merge(
            customers, how="inner", on="jr_string", suffixes=["_Prospect", "_Customer"]
        )
        abil_matches = prospects.merge(
            customers,
            how="inner",
            on="household.abilitec.householdLink",
            suffixes=["_Prospect", "_Customer"],
        )
        total_matches = pd.concat([jr_matches, abil_matches])
        total_matches.drop_duplicates(
            subset=["person_hash_Customer"], inplace=True, keep="first"
        )
        # total_matches.to_csv(r"{}\{}.csv".format(save_path, file_name), index=False)
        st.success(r"Matches Created! Stats below")
        st.balloons()
        return total_matches


st.title("USAData Matchback")

# Set empty array for column list for loading purposes
prospect_columns = []
customer_columns = []


# file selection for prospect file with formatting for column selection
prospect_file = st.file_uploader("Select Prospect File")
col1, col2, col3 = st.columns(3)
st.text(
    "-----------------------------------------------------------------------------------"
)

# file selection for customer file with formatting for column selection
customer_file = st.file_uploader("Select Customer File")
col4, col5, col6 = st.columns(3)
st.text(
    "-----------------------------------------------------------------------------------"
)

# When a file is selected, load into dataframe and allow column selection
if prospect_file is not None:
    prospects = pd.read_csv(prospect_file)
    prospect_columns = prospects.columns
    with col1:
        prosp_addr = st.selectbox("Select Prospect Address Column", prospect_columns)
    with col2:
        prosp_ln = st.selectbox("Select Prospect Lastname Column", prospect_columns)
    with col3:
        prosp_zip = st.selectbox("Select Prospect Zip Column", prospect_columns)


if customer_file is not None:
    customers = pd.read_csv(customer_file)
    customer_columns = customers.columns
    with col4:
        cust_addr = st.selectbox("Select Customer Address Column", customer_columns)
    with col5:
        cust_ln = st.selectbox("Select Customer Lastname Column", customer_columns)
    with col6:
        cust_zip = st.selectbox("Select Customer Zip Column", customer_columns)

col7, col8, col9 = st.columns(3)
with col7:
    match_button = st.button("Create Matches")
if match_button:
    matches = create_matches()
    st.session_state["df"] = matches

if "df" in st.session_state:
    # Path and file name for resulting match file
    csv = convert_df(st.session_state.df)
    st.text(f"Total Matches: {len(st.session_state.df)}")
    file_name = st.text_input("File Name (Without Extension)")
    with col9:
        st.download_button(
            "Download Match File",
            data=csv,
            file_name=file_name,
            mime="text/csv",
        )
    cols = st.session_state.df.columns
    grp_col = st.selectbox("Select grouping column", cols)
    st.dataframe(
        st.session_state.df.groupby(grp_col, dropna=False)
        .count()
        .rename(columns={cols[0]: "Count"})
        .iloc[:, 0]
    )
