import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils import load_data, load_organ_dict, remove_from_dataframe, load_nako_field_dict, get_field_id_by_english_name 
from correlation import compute_pearson, compute_spearman

def main():
    st.set_page_config(page_title="Whole-Body Organ Explorer", page_icon=":computer:", layout="wide")
    st.markdown("<h1 style='text-align: center; color: black;'>Whole-Body Organ Explorer</h1>", unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(["Home", "Data Distribution Explorer", "Data Correlation Explorer"])
    tab1, tab2, tab3 = tabs

    # Load data and dictionaries
    organ_dict = load_organ_dict()
    df = load_data()

    # df rename ID to SubjectID
    df.rename(columns={"ID": "SubjectID"}, inplace=True)

    # Ensure organ data is correctly processed
    df_organ_volume = pd.read_csv("data/volume_not_completed_cleaned.csv")
    df_organ_diameter = pd.read_csv("data/diameter_not_completed_cleaned.csv")
    df_organ_surface = pd.read_csv("data/surface_not_completed_cleaned.csv")

    # Swap key-value pairs in the organ dictionary
    organ_dict_swap = {v: k for k, v in organ_dict.items()}

    # Rename organ-specific columns
    df_organ_volume.columns = ["SubjectID"] + [f"Volume: {organ_dict_swap[int(col[6:])]}" for col in df_organ_volume.columns[1:]]
    df_organ_diameter.columns = ["SubjectID"] + [f"Diameter: {organ_dict_swap[int(col[8:])]}" for col in df_organ_diameter.columns[1:]]
    df_organ_surface.columns = ["SubjectID"] + [f"Surface: {organ_dict_swap[int(col[7:])]}" for col in df_organ_surface.columns[1:]]

    # Convert units for better interpretability
    df_organ_volume.iloc[:, 1:] = df_organ_volume.iloc[:, 1:] / 1000  # cm³
    df_organ_diameter.iloc[:, 1:] = df_organ_diameter.iloc[:, 1:] / 10  # cm
    df_organ_surface.iloc[:, 1:] = df_organ_surface.iloc[:, 1:] / 100  # cm²



    # Merge organ-specific data into the main DataFrame
    df = pd.merge(df, df_organ_volume, on="SubjectID", how="left")
    df = pd.merge(df, df_organ_diameter, on="SubjectID", how="left")
    df = pd.merge(df, df_organ_surface, on="SubjectID", how="left")

    # Remove the 'SubjectID' column as it's no longer needed
    df.drop(columns=["SubjectID"], inplace=True)

    with tab1:
        st.markdown("<h1 style='text-align: left; color: black;'>Home</h1>", unsafe_allow_html=True)

        st.markdown(
            """
            <h2 style="text-align: left;">
                Welcome to the Whole-Body Explorer of almost 30,000 subjects of the German National Cohort (NAKO)!
            </h2>
            """,
            unsafe_allow_html=True
    )

        col1, col2 = st.columns([1, 1])

        with col1:
            # Center the text using HTML and CSS
            st.markdown(
            """
            <div style="text-align: left;">
                <p>This tool provides an overview of the volume, surface, and maximal diameter of 55 different volumes 
                from the skeleton, muscles, cardiovascular system, and gastrointestinal tract of the human body.</p>
            </div>
            """,
            unsafe_allow_html=True)

            st.markdown("<h2 style='text-align: left; color: black;'>Data Information</h2>", unsafe_allow_html=True)
            # Embed link to NAKO study on word "NAKO"
            st.markdown(" The data of this study was aquired by the [NAKO study](https://www.nako.de) (German National Cohort). The applied data consists of 30,000 full-body MRI data (see Figure on the right)."+
                        " Information of 55 volumes was automatically extracted from the MRI data using the DL-based software [TotalSegmentator](https://github.com/wasserth/TotalSegmentator/tree/master). " +
                        "Based on the extracted segmentation masks, the volume, surface, and maximal diameter of each segmentation class was calculated using [PyRadiomics](https://www.radiomics.io/pyradiomics.html).")

    
        with col2:
            st.image("data/img_seg.png", use_column_width=False)
            st.write("TODO: ATTENTION - Image not in correct shape!")
        logo_nako = "data/nako_logo.png"
        st.image(logo_nako, use_column_width=False)
    with tab2:
        st.header("Data Distribution Explorer")

        # Ensure 'basis_age' is of type int
        df["basis_age"] = df["basis_age"].astype(int)

        # User controls
        factor_choice = st.selectbox("Select Factor", df.columns)
        sex_choice = st.radio("Select Gender", ["All", "Female/Male"])
        age_range = st.slider(
            "Select Age Range", 
            min_value=int(df["basis_age"].min()), 
            max_value=int(df["basis_age"].max()), 
            value=(int(df["basis_age"].min()), int(df["basis_age"].max()))
        )

        # Data filtering
        df_filtered = df[(df["basis_age"] >= age_range[0]) & (df["basis_age"] <= age_range[1])]

        # Replace sex values with meaningful labels
        df_filtered["basis_sex"] = df_filtered["basis_sex"].replace({1: "Male", 2: "Female"})

        if sex_choice == "Female/Male":
            # Plot for Female/Male
            fig = px.histogram(
                df_filtered, 
                x=factor_choice, 
                color="basis_sex",
                nbins=100, 
                title=f"Distribution of {factor_choice} by Gender",
                color_discrete_map={"Male": "#1f77b4", "Female": "#ff7f0e"}
            )
            fig.update_layout(barmode="overlay")  # Overlap histograms for comparison
        else:
            # Plot for all
            fig = px.histogram(
                df_filtered, 
                x=factor_choice, 
                nbins=100, 
                title=f"Distribution of {factor_choice} (All)"
            )

        st.plotly_chart(fig)

    # Tab 3: Data Correlation Explorer
    with tab3:
        # Load NAKO field dictionary
        nako_field_dict = load_nako_field_dict()

        st.header("Data Correlation Explorer")
        st.write("Organ shape measure compared to age.")

        # Organ Selection
        organs = list(organ_dict.keys())

        # Create two columns for inputs and results
        col1, col2 = st.columns([1, 2])

        with col1:
            # Select organ
            organ = st.selectbox("Organ", organs)
            field_id_columns = df.columns

            # Create list of field names using NAKO dictionary
            field_names = []
            for field_id in field_id_columns:
                try:
                    field_names.append(nako_field_dict[field_id]["field_name_eng"])
                except KeyError:
                    field_names.append(field_id)

            field_names.sort()
            x_column_name = st.selectbox("X Axis", field_names)
            st.markdown(
                f"<p style='font-size:12px; color:lightgrey;'>NAKO field value: {x_column_name}</p>",
                unsafe_allow_html=True,
            )

            # Select shape value
            y_column_shape = st.radio("Shape Measure", ["Volume", "Diameter", "Surface"])
            y_column = f"{y_column_shape}: {organ}"

            # Map selected organ key to value
            organ_id = organ_dict[organ]

            # Gender separation
            separate_by_sex = st.radio("Separate by Sex", ["All", "Male/Female"])

            # Informational message
            st.markdown(
                """
                <div style="text-align: left; font-size: 20px;">
                    ⚠️ Manual data quality assessment of the automatically extracted volume, surface, 
                    and diameter values not yet uploaded.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            # Create title for plot
            st.markdown(
                f"<h3 style='text-align: left; color: black;'>{organ.capitalize()}: {y_column_shape} vs {x_column_name}</h3>",
                unsafe_allow_html=True,
            )

            # Match x_column with its ID in the dictionary
            x_column = get_field_id_by_english_name(nako_field_dict, x_column_name)

            if x_column not in df.columns or y_column not in df.columns:
                st.error(f"Column {x_column} or {y_column} not found in the data.")
                st.stop()

            # Ensure numeric data
            df[x_column] = pd.to_numeric(df[x_column], errors="coerce")
            df[y_column] = pd.to_numeric(df[y_column], errors="coerce")

            # Filter and clean data
            data = remove_from_dataframe(df).dropna(subset=[x_column, y_column])

            # Visualization: Separate by Gender
            if separate_by_sex == "Male/Female":
                data["basis_sex"] = data["basis_sex"].replace({1: "Male", 2: "Female"})
                custom_colors = {"Male": "#1f77b4", "Female": "#ff7f0e"}

                fig = px.scatter(
                    data,
                    x=x_column,
                    y=y_column,
                    color="basis_sex",
                    color_discrete_map=custom_colors,
                    trendline="lowess",
                    title=f"{y_column} vs {x_column} by Gender",
                )
                fig.update_traces(marker=dict(size=4))
            else:
                fig = px.scatter(
                    data,
                    x=x_column,
                    y=y_column,
                    title=f"{y_column} vs {x_column}",
                )

            st.plotly_chart(fig)

            # Statistical summary table
            st.subheader("Statistical Summary")
            df_grouped = data.groupby("basis_sex" if separate_by_sex == "Male/Female" else ["basis_sex"]).agg(
                {
                    x_column: ["min", "max", "mean", "std"],
                    y_column: ["min", "max", "mean", "std"],
                }
            )
            df_grouped = df_grouped.round(2)
            st.table(df_grouped)

            # Correlation analysis
            st.subheader("Correlation Analysis")
            corr_pearson, p_value_pearson = compute_pearson(data, x_column, y_column)
            corr_spearman, p_value_spearman = compute_spearman(data, x_column, y_column)

            corr_table = pd.DataFrame(
                {
                    "Statistic": ["Pearson r", "Spearman r", "p-value (Pearson)", "p-value (Spearman)"],
                    "Value": [corr_pearson, corr_spearman, p_value_pearson, p_value_spearman],
                }
            )
            st.table(corr_table)




if __name__ == "__main__":
    main()
