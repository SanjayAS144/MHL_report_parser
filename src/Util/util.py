
import re

def cleanstr(str_val):
    cleaned_col = re.sub(r'(\\\\n|\\n|\n|\r|\t)', ' ', str(str_val))
    cleaned_col = ' '.join(cleaned_col.split())
    return cleaned_col


def clean_df_rows(df, cols):
    """
    Remove special characters like line breaks from DataFrame column names.

    Parameters:
    df: pandas DataFrame

    Returns:
    pandas DataFrame with cleaned column names
    """

    for col in cols:
        df[col] = df[col].apply(cleanstr)
    return df


def clean_dataframe_columns(df):
    """
    Remove special characters like line breaks from DataFrame column names.

    Parameters:
    df: pandas DataFrame

    Returns:
    pandas DataFrame with cleaned column names
    """
    df_cleaned = df.copy()

    # Clean column names by removing line breaks, carriage returns, tabs
    # and normalizing spaces
    cleaned_columns = []
    for col in df_cleaned.columns:
        # Remove line breaks, carriage returns, tabs
        cleaned_col = re.sub(r'(\\\\n|\\n|\n|\r|\t)', ' ', str(col))
        # Remove multiple spaces and trim
        cleaned_col = ' '.join(cleaned_col.split())
        cleaned_columns.append(cleaned_col)

    df_cleaned.columns = cleaned_columns
    return df_cleaned