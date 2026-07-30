import pandas as pd
from typing import Union, List

class DescriptiveStats:
    """
    Computes the descriptive statistics for a given pandas Series/DataFrame.
    """

    def __init__(self, data: pd.Series):
        if not isinstance(data, pd.Series):
            raise TypeError("DescriptiveStats requires a pandas Series.")

        # Drop NaNs to ensure pure mathematical calculations
        self.data = data.dropna()

    def mean(self) -> float:
        """Returns the mean of the Series."""
        return self.data.mean()

    def median(self) -> float:
        """Returns the median of the Series."""
        return self.data.median()

    def mode(self) -> List[Union[int, float]]:
        """Returns the mode(s) of the data as a list."""
        # Pandas returns a Series for mode since there can be multiple; convert to list
        return self.data.mode().tolist()

    def variance(self) -> float | pd.Series:
        """Returns the sample variance."""
        return self.data.var()

    def standard_deviation(self) -> float:
        """Returns the sample standard deviation."""
        return self.data.std()

    def minimum(self) -> Union[int, float]:
        """Returns the minimum value."""
        return self.data.min()

    def maximum(self) -> Union[int, float]:
        """Returns the maximum value."""
        return self.data.max()

    def range(self) -> Union[int, float]:
        """Returns the range (max - min)."""
        return self.maximum() - self.minimum()

    def quartiles(self) -> dict:
        """Returns the first (25%), second (50%), and third (75%) quartiles."""
        return {
            "Q1 (25%)": self.data.quantile(0.25),
            "Q2 (50%)": self.data.quantile(0.50),
            "Q3 (75%)": self.data.quantile(0.75)
        }

    def iqr(self) -> float:
        """Returns the Interquartile Range (Q3 - Q1)."""
        q1 = self.data.quantile(0.25)
        q3 = self.data.quantile(0.75)
        return q3 - q1

    def summary(self) -> dict:
        """Returns a dictionary of all descriptive statistics."""
        return {
            "mean": self.mean(),
            "median": self.median(),
            "mode": self.mode(),
            "variance": self.variance(),
            "std_dev": self.standard_deviation(),
            "min": self.minimum(),
            "max": self.maximum(),
            "range": self.range(),
            "quartiles": self.quartiles(),
            "iqr": self.iqr()
        }
