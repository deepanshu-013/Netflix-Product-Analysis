import pandas as pd
import numpy as np
from typing import Tuple
from scipy import stats
from statistics.descriptive import DescriptiveStats


class InferenceStats:
    """
    Performs hypothesis testing and calculates confidence intervals.
    Architecture: Receives data from the Analytics layer. Uses scipy.stats for math.
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("InferenceStats requires a pandas DataFrame.")
        self.df = df

    def confidence_interval(self, column: str, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculates the confidence interval for the mean of a numeric column.
        Uses DescriptiveStats for mean and standard deviation.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found.")

        series = self.df[column].dropna()
        if series.empty:
            return (np.nan, np.nan)

        desc = DescriptiveStats(series)
        mean = desc.mean()
        std = desc.standard_deviation()
        n = len(series)

        # Degrees of freedom
        df_degrees = n - 1

        # t-critical value for the given confidence level
        alpha = 1 - confidence
        t_crit = stats.t.ppf(1 - alpha / 2, df_degrees)

        # Standard error
        std_err = std / np.sqrt(n)

        margin_of_error = t_crit * std_err

        lower_bound = mean - margin_of_error
        upper_bound = mean + margin_of_error

        return lower_bound, upper_bound

    def t_test(self, col1: str, col2: str = None, popmean: float = None) -> dict:
        """
        Performs an Independent Two-Sample t-test (if col2 is provided)
        or a One-Sample t-test against a known population mean (if popmean is provided).
        """
        if col1 not in self.df.columns:
            raise ValueError(f"Column '{col1}' not found.")

        data1 = self.df[col1].dropna()

        # One-sample t-test
        if popmean is not None:
            t_stat, p_val = stats.ttest_1samp(data1, popmean)
            return {
                "test_type": "One-Sample t-test",
                "t_statistic": t_stat,
                "p_value": p_val
            }

        # Two-sample t-test
        if col2 is None:
            raise ValueError("Must provide either 'col2' for two-sample test or 'popmean' for one-sample test.")

        if col2 not in self.df.columns:
            raise ValueError(f"Column '{col2}' not found.")

        data2 = self.df[col2].dropna()

        # We use Welch's t-test (equal_var=False) as it is more robust
        # when the two samples have unequal variances or sample sizes.
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False, nan_policy='omit')

        return {
            "test_type": "Welch's Independent Two-Sample t-test",
            "t_statistic": t_stat,
            "p_value": p_val
        }

    def chi_square(self, col1: str, col2: str) -> dict:
        """
        Performs a Chi-Square Test of Independence between two categorical columns.
        """
        if col1 not in self.df.columns or col2 not in self.df.columns:
            raise ValueError("One or both columns not found.")

        # Create a contingency table (crosstab) of the two categorical variables
        contingency_table = pd.crosstab(self.df[col1], self.df[col2])

        # Scipy's chi2_contingency returns: chi2, p, dof, expected frequencies
        chi2_stat, p_val, dof, expected = stats.chi2_contingency(contingency_table)

        return {
            "chi2_statistic": chi2_stat,
            "p_value": p_val,
            "degrees_of_freedom": dof
        }

    def anova(self, group_col: str, value_col: str) -> dict:
        """
        Performs a One-Way ANOVA to compare the means of a numeric variable (value_col)
        across multiple groups (group_col).
        """
        if group_col not in self.df.columns or value_col not in self.df.columns:
            raise ValueError("One or both columns not found.")

        # Drop rows where either the group or the value is missing
        valid_data = self.df[[group_col, value_col]].dropna()

        # Group the numeric data by the categorical groups
        groups = [group[value_col].values for name, group in valid_data.groupby(group_col)]

        # Perform ANOVA
        f_stat, p_val = stats.f_oneway(*groups)

        return {
            "f_statistic": f_stat,
            "p_value": p_val
        }