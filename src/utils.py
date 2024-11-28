import numpy as np
import pandas as pd
import json
def remove_invalid_values(col):
    """
    Replaces invalid values in a column with NaN.
    Handles specific outlier codes (88, 99, 999, 9999) and negative values for organ-related columns.
    """
    col = col.replace([88, 99, 999, 9999], np.nan)
    return col

def remove_from_dataframe(df):
    """
    Removes invalid values from a dataframe.
    Specific outlier codes and negative values for organ-related metrics are handled.
    """
    for col in df.columns:
        df[col] = remove_invalid_values(df[col])

        # Set negative values to NaN for columns related to volume, diameter, or surface
        if any(keyword in col for keyword in ["Volume", "Diameter", "Surface"]):
            df[col] = df[col].apply(lambda x: np.nan if x < 0 else x)

    return df

def load_data():
    """
    Load the main dataset with cleaned data.
    """
    return pd.read_csv("data/nako_cleaned.csv")

def load_organ_dict():
    """
    Load organ dictionary mapping organ names to IDs.
    """
    df = pd.read_csv("data/organ_dict.csv")
    return dict(zip(df["name"], df["id"]))

def load_nako_field_dict():
    """
    Load the NAKO field dictionary from a JSON file.
    """
    with open("data/NAKO_field_dict.json", "r") as file:
        nako_field_dict = json.load(file)
    return nako_field_dict
    
def get_field_id_by_english_name(field_dict, field_name_eng):
    """
    Get the field ID corresponding to the given English field name.

    Args:
        field_dict (dict): The NAKO field dictionary.
        field_name_eng (str): The English name of the field.

    Returns:
        str: The corresponding field ID, or None if not found.
    """
    for field_id, metadata in field_dict.items():
        if metadata.get("field_name_eng") == field_name_eng:
            return field_id
    return None
