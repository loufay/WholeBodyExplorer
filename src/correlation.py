from scipy.stats import pearsonr, spearmanr
import numpy as np

def compute_pearson(df, x, y):
    """
    Computes the Pearson correlation coefficient and p-value.
    Returns results rounded to 2 decimal places.
    """
    try:
        corr, p_value = pearsonr(df[x], df[y])
        return round(corr, 2), round(p_value, 2)
    except Exception as e:
        return None, None

def compute_spearman(df, x, y):
    """
    Computes the Spearman rank correlation coefficient and p-value.
    Returns results rounded to 2 decimal places.
    """
    try:
        corr, p_value = spearmanr(df[x], df[y])
        return round(corr, 2), round(p_value, 2)
    except Exception as e:
        return None, None
