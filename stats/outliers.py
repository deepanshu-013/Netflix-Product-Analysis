import pandas as pd
from statistics.descriptive import DescriptiveStats

class OutlierStats:
    """
    Detects outliers in a numeric pandas Series.
    Architecture: Consumes DescriptiveStats to get mean, median, and IQR.
    """

    def __init__(self, data: pd.Series):
        if not isinstance(data, pd.Series):
            raise TypeError("OutlierStats requires a pandas Series.")
        self.data = data.dropna()

        # Dependency Injection: OutlierStats uses DescriptiveStats for its math
        self.desc_stats = DescriptiveStats(self.data)

    def z_score(self, threshold: float = 3.0) -> pd.DataFrame:
        """
        Returns outliers based on Z-scores.
        Uses DescriptiveStats for mean and standard deviation.
        """
        # Use descriptive.py methods!
        mean = self.desc_stats.mean()
        std = self.desc_stats.standard_deviation()

        if std == 0 or pd.isna(std):
            return pd.DataFrame(columns=['value', 'z_score'])

        z_scores = (self.data - mean) / std
        outliers = self.data[z_scores.abs() > threshold]

        return outliers.to_frame(name='value').assign(z_score=z_scores[outliers.index])

    def iqr_outliers(self) -> pd.DataFrame:
        """
        Returns outliers based on the Interquartile Range (1.5 * IQR rule).
        Uses DescriptiveStats for Q1, Q3, and IQR.
        """
        # Use descriptive.py methods!
        quartiles = self.desc_stats.quartiles()
        q1 = quartiles["Q1 (25%)"]
        q3 = quartiles["Q3 (75%)"]

        # We can even use the IQR method from DescriptiveStats!
        iqr = self.desc_stats.iqr()

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = self.data[(self.data < lower_bound) | (self.data > upper_bound)]
        return outliers.to_frame(name='value')

    def modified_z_score(self, threshold: float = 3.5) -> pd.DataFrame:
        """
        Returns outliers based on Modified Z-scores using Median Absolute Deviation (MAD).
        Uses DescriptiveStats for the median.
        """
        # Use descriptive.py method!
        median = self.desc_stats.median()

        abs_dev = (self.data - median).abs()
        mad = abs_dev.median()

        if mad == 0:
            return pd.DataFrame(columns=['value', 'modified_z_score'])

        mod_z_scores = 0.6745 * (self.data - median) / mad
        outliers = self.data[mod_z_scores.abs() > threshold]

        return outliers.to_frame(name='value').assign(modified_z_score=mod_z_scores[outliers.index])