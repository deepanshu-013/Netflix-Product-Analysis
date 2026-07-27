from config import *
import pandas as pd
from datetime import datetime
import numpy as np

class Preprocessor:
    """Preprocessing engine that returns a DataFrame."""
    def __init__(self, data_path: str = DATA_PATH, date_format: str = DATE_FORMAT, random_seed: int = RANDOM_SEED, required_columns: list = REQUIRED_COLUMNS, valid_ratings: set = VALID_RATINGS):
        self.data_path = data_path
        self.date_format = date_format
        self.required_columns = required_columns
        self.valid_ratings = valid_ratings
        self.random_seed = random_seed
        self.validation_report: dict = {}

    def __load_data(self):
        """Load the CSV into DataFrame."""
        df = pd.read_csv(self.data_path)
        return df

    def __validate(self, df):
        """Validate the DataFrame and return Validation report in dictionary format."""
        report = {
            "row_count": df.shape[0],
            "column_count": df.shape[1],
            "missing_required_columns": [],
            "missing_values": {},
            "duplicate_show_ids": 0,
            "duplicate_titles": 0,
            "invalid_dates": 0,
            "invalid_durations": 0,
            "invalid_ratings": [],
            "is_valid": True
        }

        # Check if any required columns are missing
        report["missing_required_columns"] = set(self.required_columns) - set(df.columns)

        # If any required columns are missing, set is_valid -> False
        if report["missing_required_columns"]:
            report["is_valid"] = False


        if not report["missing_required_columns"]:
            # Check every column for total amount of missing values
            report["missing_values"] = {
                col : int(df[col].isnull().sum())
                for col in df.columns
                if df[col].isnull().sum() > 0
            }

            # Duplicate title or ids
            if "show_id" in df.columns:
                report["duplicate_show_ids"] = int(df["show_id"].duplicated().sum())
            if "title" in df.columns:
                report["duplicate_titles"] = int(df["title"].duplicated().sum())

            # Invalid dates
            if "date_added" in df.columns:
                parsed = pd.to_datetime(df["date_added"], format=self.date_format, errors='coerce')

                # Instead of invalid dates, NaN is set at there respective place.
                original_notnull_dates = df["date_added"].notna()
                invalid_dates = original_notnull_dates & parsed.isna()
                report["invalid_dates"] = int(invalid_dates.sum())

            # Invalid duration
            if "duration" in df.columns:
                def _is_valid_duration(val):
                    if pd.isna(val):
                        return True # Nulls are tracked separately
                    s = str(val).strip().lower()
                    if s.endswith("min"):
                        num = s.replace("min", "").strip()
                        return num.isdigit() and int(num) > 0
                    if s.endswith("seasons") or s.endswith("season"):
                        num = s.replace("seasons", "").replace("season", "").strip()
                        return num.isdigit() and int(num) > 0
                    return False

                invalid_durations = df["duration"].apply(lambda x: not _is_valid_duration(x))
                report["invalid_durations"] = int(invalid_durations.sum())

            # Invalid rating
            if "rating" in df.columns:
                non_null_ratings = df["rating"].dropna().astype(str).str.strip()
                invalid_ratings = non_null_ratings[
                    ~ non_null_ratings.isin(self.valid_ratings)
                ]
                report["invalid_ratings"] = sorted(invalid_ratings.unique().tolist())

        # Validation flag
        fatal_errors = (
                len(report["missing_required_columns"]) > 0
        )

        if fatal_errors:
            raise ValueError(
                f"Missing required columns: {report['missing_required_columns']}"
            )
        return report

    def __clean(self, df):
        """Fix duplicates, nulls, whitespaces, and types in-place."""

        # Strip whitespace from all string columns
        str_cols = df.select_dtypes(include=['object']).columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
            # Normalize "nan" string back to real NaN
            df.loc[df[col].str.lower() == "nan", col] = np.nan

        # Remove duplicates (keeping the first appearance)
        if "show_id" in df.columns:
            df.drop_duplicates(subset= ["show_id"], keep= "first", inplace= True)
        df.drop_duplicates(inplace= True)

        # Handling null values
        critical_cols = [c for c in ["title", "type"] if c in df.columns]
        df.dropna(subset= critical_cols, inplace= True)

        # Fill descriptive text with something sensible
        text_fill_map = {
            "director": "Unknown",
            "cast": "Unknown",
            "country": "Unknown",
            "rating": "UR", # Unrated
            "date_added": pd.NaT
        }
        for col, fill_value in text_fill_map.items():
            if col in df.columns:
                df[col] = df[col].fillna(value=fill_value)

        # Handling description
        if "description" in df.columns:
            df["description"] = df["description"].fillna(value="")

        # Type conversion
        if "release_year" in df.columns:
            df["release_year"] = pd.to_numeric(df["release_year"], errors='coerce')
            df["release_year"] = df["release_year"].fillna(value=0).astype(int)

        if "date_added" in df.columns:
            df["date_added"] = pd.to_datetime(df["date_added"], format=self.date_format, errors='coerce')


        # Resetting the index after all the changes
        df.reset_index(drop= True, inplace= True)

    def __engineer_features(self, df):
        """Create derived columns in-place for analytic purpose."""
        current_year = datetime.now().year

        # duration_ minutes column: minutes for movies, NaN for shows
        if "duration" in df.columns:
            def _extract_minutes(val):
                if pd.isna(val):
                    return np.nan
                s = str(val).strip().lower()
                if s.endswith("min"):
                    num = s.replace("min", "").strip()
                    return float(num) if num.replace(".", "", 1).isdigit() else np.nan
                return np.nan

            df["duration_minutes"] = df["duration"].apply(_extract_minutes)

        # release_decade
        if "release_year" in df.columns:
            df["release_decade"] =(df["release_year"] // 10) * 10

        # content_age
        if "release_year" in df.columns:
            df["content_age"] = current_year - df["release_year"]
            df.loc[df["content_age"] < 0, "content_age"] = np.nan

        # month_added
        if "date_added" in df.columns:
            df["month_added"] = df["date_added"].dt.month

        # country_count
        if "country" in df.columns:
            df["country_count"] = df["country"].apply(
                lambda v: 0 if pd.isna(v) or v == "Unknown"
                else len([c for c in str(v).split(",") if c.strip()])
            )

        # genre_count (from listed_in)
        if "listed_in" in df.columns:
            df["genre_count"] = df["listed_in"].apply(
                lambda v: 0 if pd.isna(v)
                else len([g for g in str(v).split(",") if g.strip()])
            )

        # director_count
        if "director" in df.columns:
            df["director_count"] = df["director"].apply(
                lambda v: 0 if pd.isna(v) or v == "Unknown"
                else len([d for d in str(v).split(",") if d.strip()])
            )


    def preprocess(self):
        """Integrates the full pipeline:
            load_data() -> validate() -> clean() -> engineer_features()
        Return pandas.dataframe, validation report
        """
        df= self.__load_data()
        report = self.__validate(df)
        self.__clean(df)
        self.__engineer_features(df)
        return df, report
