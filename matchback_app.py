import streamlit as st
import pandas as pd


def create_matches():
    if prospect_file is None or customer_file is None:
        st.error("Please select prospect and/or customer file")
    elif save_path == "" or file_name == "":
        st.error("Please enter save path and/or file name")
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
        total_matches.to_csv(r"{}\{}.csv".format(save_path, file_name), index=False)
        st.success(
            r"Match File created! Find at location {}\{}.csv".format(
                save_path, file_name
            )
        )
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

# Path and file name for resulting match file
save_path = st.text_input("Save Location")
file_name = st.text_input("File Name (Without Extension)")

match_button = st.button("Create Matches")
if match_button:
    matches = create_matches()
    st.session_state["df"] = matches

if "df" in st.session_state:
    cols = st.session_state.df.columns
    grp_col = st.selectbox("Select grouping column", cols)
    st.dataframe(
        st.session_state.df.groupby(grp_col, dropna=False)
        .count()
        .rename(columns={cols[0]: "Count"})
        .iloc[:, 0]
    )








import streamlit as st
import pandas as pd
import io


def convert_df(df):
    if type(df) == type([]):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df[0].to_excel(writer, sheet_name="Matches", index=False)
            df[1].to_excel(writer, sheet_name="Grouping Counts")
        return buffer
    else:
        return df.to_csv(index=False).encode("utf-8")


def create_matches(liveramp):
    print(cust_dedupe)
    if prospect_file is None or customer_file is None:
        st.error("Please select prospect and/or customer file")
        return False
    # elif save_path == "" or file_name == "":
    #    st.error("Please enter save path and/or file name")
    elif " " in [
        prosp_addr,
        prosp_ln,
        prosp_zip,
        cust_addr,
        cust_ln,
        cust_zip,
    ]:
        st.error("Please select prospect and customer columns")
        return False
    elif len(cust_dedupe) == 0:
        st.error("Please select column(s) for deduplicating")
        return False
    else:
        customers.drop_duplicates(subset=cust_dedupe, inplace=True)
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
        jr_matches["match_type"] = "JR"
        abil_matches = prospects.merge(
            customers,
            how="inner",
            on= "household_link" if liveramp else "household.abilitec.householdLink",
            suffixes=["_Prospect", "_Customer"],
        )
        abil_matches["match_type"] = "Abilitec"
        total_matches = pd.concat([jr_matches, abil_matches])
        total_matches.loc[
            total_matches.duplicated(
                subset=["person_hash_Prospect", "person_hash_Customer"], keep="last"
            ),
            "match_type",
        ] = "Both"

        total_matches.drop_duplicates(
            subset=["person_hash_Customer"], inplace=True, keep="first"
        )

        st.success(r"Matches Created! Stats below")
        st.balloons()
        return total_matches


st.title("USAData Matchback")

# Set empty array for column list for loading purposes
prospect_columns = [" "]
customer_columns = [" "]


# file selection for prospect file with formatting for column selection
prospect_file = st.file_uploader("Select Prospect File")
col1, col2, col3 = st.columns(3)
st.text(
    "-----------------------------------------------------------------------------------"
)

# file selection for customer file with formatting for column selection
customer_file = st.file_uploader("Select Customer File")
col4, col5, col6 = st.columns(3)
col_ded, col_blank = st.columns(2)
st.text(
    "-----------------------------------------------------------------------------------"
)

# When a file is selected, load into dataframe and allow column selection
if prospect_file is not None:
    prospects = pd.read_csv(prospect_file)
    prospect_columns += prospects.columns.tolist()
    with col1:
        prosp_addr = st.selectbox("Select Prospect Address Column", prospect_columns)
    with col2:
        prosp_ln = st.selectbox("Select Prospect Lastname Column", prospect_columns)
    with col3:
        prosp_zip = st.selectbox("Select Prospect Zip Column", prospect_columns)


if customer_file is not None:
    customers = pd.read_csv(customer_file)
    customer_columns += customers.columns.tolist()
    with col4:
        cust_addr = st.selectbox("Select Customer Address Column", customer_columns)
    with col5:
        cust_ln = st.selectbox("Select Customer Lastname Column", customer_columns)
    with col6:
        cust_zip = st.selectbox("Select Customer Zip Column", customer_columns)
    with col_ded:
        cust_dedupe = st.multiselect(
            "Select Column(s) to Dedupe From", customer_columns
        )

col7, col8, col9 = st.columns(3)
with col7:
    match_button = st.button("Create Matches")
with col8:
    liveramp = st.checkbox("Liveramp")

if match_button:
    matches = create_matches(liveramp)
    if type(matches) == type(pd.DataFrame()):
        st.session_state["df"] = matches

if "df" in st.session_state:
    # Path and file name for resulting match file
    st.header(f"Total Matches: {len(st.session_state.df)}")
    file_name = st.text_input("File Name (Without Extension)")

    df = pd.DataFrame()
    cols = [" "] + st.session_state.df.columns.tolist()
    col10, col11 = st.columns(2)
    with col10:
        grp_col1 = st.selectbox("Select grouping column 1", cols)
    with col11:
        grp_col2 = st.selectbox("Select grouping column 2 (optional)", options=cols)

    if " " not in [grp_col1, grp_col2]:
        df = (
            st.session_state.df.groupby([grp_col1, grp_col2], dropna=False)
            .count()
            .rename(columns={cols[1]: "Count"})
            .iloc[:, 0]
        )

    elif " " != grp_col1:
        df = (
            st.session_state.df.groupby(grp_col1, dropna=False)
            .count()
            .rename(columns={cols[1]: "Count"})
            .iloc[:, 0]
        )
    if not df.empty:
        st.dataframe(df)
    with col9:
        download_btn = st.empty()
        breakdown = st.checkbox("Include grouping?")
        if breakdown:
            csv = convert_df([st.session_state.df, df])
            with download_btn:
                st.download_button(
                    "Download Match File",
                    data=csv,
                    file_name=(
                        f"{file_name}.xlsx" if file_name != "" else "match_file.xlsx"
                    ),
                )
        else:
            csv = convert_df(st.session_state.df)
            with download_btn:
                st.download_button(
                    "Download Match File",
                    data=csv,
                    file_name=(
                        f"{file_name}.csv" if file_name != "" else "match_file.csv"
                    ),
                    mime="text/csv",
                )
