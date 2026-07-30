import pandas as pd

class CorrelationStats:
    """
    Computes correlation and covariance metrics.
    """

    def __init__(self, x: pd.Series = None, y: pd.Series = None, df: pd.DataFrame = None):
        self.x = x.dropna() if x is not None else None
        self.y = y.dropna() if y is not None else None
        self.df = df.dropna() if df is not None else None

    def pearson(self) -> float:
        """Computes Pearson correlation coefficient (-1 to 1). Linear relationship."""
        if self.x is None or self.y is None:
            raise ValueError("Pearson requires two Series (x and y).")
        return self.x.corr(self.y, method="pearson")

    def spearman(self) -> float:
        """Computes Spearman rank correlation (-1 to 1). Monotonic relationship."""
        if self.x is None or self.y is None:
            raise ValueError("Spearman requires two Series (x and y).")
        return self.x.corr(self.y, method='spearman')

    def covariance(self) -> float:
        """Computes sample covariance between two Series."""
        if self.x is None or self.y is None:
            raise ValueError("Covariance requires two Series (x and y).")
        return self.x.cov(self.y)

    def correlation_matrix(self, method: str = 'pearson') -> pd.DataFrame:
        """Returns a correlation matrix for all numeric columns in a DataFrame."""
        if self.df is None:
            raise ValueError("Correlation matrix requires a DataFrame.")
        return self.df.corr(method=method)