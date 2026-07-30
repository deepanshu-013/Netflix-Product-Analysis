import pandas as pd

class DistributionStats:
    """
    Computes distribution stats for a given pandas Series.
    Architecture: Receives data from the Analytics layer.
    """

    def __init__(self, data: pd.Series):
        if not isinstance(data, pd.Series):
            raise TypeError("DistributionStats requires a pandas Series.")
        self.data = data

    def frequency_table(self) -> pd.DataFrame:
        """
        Returns a frequency table for categorical/discrete data.
        Columns: value, frequency, percentage
        """
        counts = self.data.value_counts().reset_index()
        counts.columns = ['value', 'frequency']
        counts['percentage'] = (counts['frequency'] / counts['frequency'].sum()) * 100
        counts['percentage'] = counts['percentage'].round(2)
        return counts

    def histogram(self, bins: int = 10) -> pd.DataFrame:
        """
        Bins numeric data into intervals and returns frequencies per bin.
        Returns a DataFrame with bin ranges and counts.
        """
        if not pd.api.types.is_numeric_dtype(self.data):
            raise TypeError("Histogram requires a numeric data.")

        # pd.cut segments the data into discrete bins
        binned = pd.cut(self.data, bins=bins)

        # Count values in each bin and sort by the bin interval
        counts = binned.value_counts().sort_index().reset_index()
        counts.columns = ['bin_range', 'frequency']

        # Calculate percentage density within each bin
        counts['percentage'] = (counts['frequency'] / counts['frequency'].sum()) * 100
        counts['percentage'] = counts['percentage'].round(2)

        return counts

    def skewness(self) -> float:
        """
        Returns the skewness of the distribution.
        Positive = right-skewed, Negative = left-skewed, 0 = symmetric.
        """
        if not pd.api.types.is_numeric_dtype(self.data):
            raise ValueError("Skewness requires numeric data.")
        return self.data.skew()

    def kurtosis(self) -> float:
        """
        Returns the kurtosis of the distribution (Fisher's definition).
        Positive = heavier tails than normal, Negative = lighter tails.
        """
        if not pd.api.types.is_numeric_dtype(self.data):
            raise ValueError("Kurtosis requires numeric data.")
        return self.data.kurt()