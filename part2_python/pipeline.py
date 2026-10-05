"""End-to-end data cleaning pipeline for the Metro Interstate Traffic dataset."""

# ============================================================
# Task 1 – Data Pipeline Construction
# ============================================================

# 1. Imports
import logging
from pathlib import Path

import pandas as pd


# 2. Logger
logger = logging.getLogger(__name__)


# 3. Configuration
EXPECTED_COLUMNS = [
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "weather_main",
    "weather_description",
    "date_time",
    "traffic_volume",
]

CATEGORICAL_COLUMNS = [
    "holiday",
    "weather_main",
    "weather_description",
]

RAW_DATA_PATH = Path("../part1_data_analytics/Metro_Interstate_Traffic_Volume.csv")
CLEANED_DATA_PATH = Path("cleaned_traffic_data.csv")
LOG_PATH = Path("pipeline.log")
# ============================================================
# 4. Logging Configuration
# ============================================================

def configure_logging():
    """Configure console and file logging for the pipeline."""

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Console handler: INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler: DEBUG and above
    file_handler = logging.FileHandler(LOG_PATH, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# ============================================================
# 5. Load Raw Data
# ============================================================

def load_raw_data(file_path):
    """Load the raw traffic CSV file safely."""
    try:
        df = pd.read_csv(file_path)

        logger.info(
            "Raw CSV loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Raw CSV file was not found: %s",
            file_path,
            exc_info=True
        )
        return None

    except pd.errors.ParserError:
        logger.error(
            "Failed to parse the raw CSV file: %s",
            file_path,
            exc_info=True
        )
        return None

    except OSError:
        logger.error(
            "File I/O error while reading: %s",
            file_path,
            exc_info=True
        )
        return None  

# ============================================================
# 6. Validate Schema
# ============================================================

def validate_schema(df, expected_columns):
    """Validate that all required columns exist in the dataset."""
    missing_columns = [
        column for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        logger.error(
            "Schema validation failed. Missing columns: %s",
            missing_columns
        )
        return False

    logger.info(
        "Schema validation successful. All %d expected columns are present.",
        len(expected_columns)
    )

    return True  

# ============================================================
# 7. Standardise Categorical Values
# ============================================================

def standardise_categorical_values(df, columns):
    """Standardise categorical text fields without changing valid category names."""
    df = df.copy()

    for column in columns:
        before = df[column].copy()

        df[column] = df[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )

        # Treat NaN before and after as unchanged
        changed_mask = ~(
            before.eq(df[column]) |
            (before.isna() & df[column].isna())
        )
        changed_rows = changed_mask.sum()

        if changed_rows > 0:
            logger.warning(
                "%d rows modified while standardising categorical column '%s'.",
                changed_rows,
                column
            )
        else:
            logger.info(
                "Categorical column '%s' required no standardisation changes.",
                column
            )

    return df

# ============================================================
# 8. Parse and Validate Date/Time
# ============================================================

def parse_datetime_column(df, column="date_time"):
    """Parse and validate the date/time column."""
    df = df.copy()

    parsed_dates = pd.to_datetime(
        df[column],
        errors="coerce"
    )

    invalid_mask = parsed_dates.isna() & df[column].notna()
    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        logger.warning(
            "%d invalid date/time values detected in '%s'.",
            invalid_count,
            column
        )
    else:
        logger.info(
            "Date/time validation successful for '%s'; "
            "no invalid values detected.",
            column
        )

    df[column] = parsed_dates

    return df

# ============================================================
# 9. Identify and Remove Duplicate Rows
# ============================================================

def remove_duplicates(df):
    """Identify and remove fully duplicated rows."""
    df = df.copy()

    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)

        logger.warning(
            "%d duplicate rows detected and removed.",
            duplicate_count
        )
    else:
        logger.info(
            "Duplicate check completed; no duplicate rows detected."
        )

    return df

# ============================================================
# 10. Impute Zero-Kelvin Temperatures
# ============================================================

def impute_zero_kelvin_by_month(df):
    """Replace 0 K temperatures with the median valid temperature for each month."""
    df = df.copy()

    zero_mask = df["temp"] == 0
    affected_rows = zero_mask.sum()

    if affected_rows == 0:
        logger.info(
            "No zero-Kelvin temperature values required imputation."
        )
        return df

    for month in sorted(df.loc[zero_mask, "date_time"].dt.month.unique()):
        month_zero_mask = (
            zero_mask & (df["date_time"].dt.month == month)
        )

        valid_month_values = df.loc[
            (df["date_time"].dt.month == month)
            & (df["temp"] > 0),
            "temp"
        ]

        monthly_median = valid_month_values.median()

        # Fallback if a month contains no valid temperature readings
        if pd.isna(monthly_median):
            monthly_median = df.loc[
                df["temp"] > 0,
                "temp"
            ].median()

            logger.warning(
                "No valid monthly temperature values found for month %d; "
                "global valid temperature median used instead.",
                month
            )

        logger.debug(
            "Month %d valid temperature median used for imputation: %.2f K.",
            month,
            monthly_median
        )

        df.loc[month_zero_mask, "temp"] = monthly_median

    logger.warning(
        "%d zero-Kelvin temperature records imputed using "
        "monthly median temperatures.",
        affected_rows
    )

    return df

# ============================================================
# 11. Impute Extreme Rainfall
# ============================================================

def impute_extreme_rainfall(df, threshold=9000):
    """Replace implausible rainfall values with the median valid rainfall."""
    df = df.copy()

    extreme_mask = df["rain_1h"] > threshold
    affected_rows = extreme_mask.sum()

    if affected_rows == 0:
        logger.info(
            "No rainfall values above %.0f mm required imputation.",
            threshold
        )
        return df

    valid_rainfall = df.loc[
        df["rain_1h"] <= threshold,
        "rain_1h"
    ]

    rainfall_median = valid_rainfall.median()

    logger.debug(
        "Valid rainfall median used for imputation: %.2f mm.",
        rainfall_median
    )

    df.loc[extreme_mask, "rain_1h"] = rainfall_median

    logger.warning(
        "%d rainfall record(s) above %.0f mm imputed using "
        "the valid rainfall median.",
        affected_rows,
        threshold
    )

    return df

# ============================================================
# 12. Final Validation
# ============================================================

def final_validation(df):
    """Perform final validation checks on the cleaned dataset."""

    duplicate_count = df.duplicated().sum()
    zero_kelvin_count = (df["temp"] == 0).sum()
    extreme_rain_count = (df["rain_1h"] > 9000).sum()
    invalid_datetime_count = df["date_time"].isna().sum()

    if (
        duplicate_count == 0
        and zero_kelvin_count == 0
        and extreme_rain_count == 0
        and invalid_datetime_count == 0
    ):
        logger.info(
            "Final validation successful: %d rows, %d columns; "
            "no duplicates, zero-Kelvin temperatures, extreme rainfall values, "
            "or invalid date/time values remain.",
            df.shape[0],
            df.shape[1]
        )
        return True

    logger.error(
        "Final validation failed: duplicates=%d, zero_kelvin=%d, "
        "extreme_rainfall=%d, invalid_datetime=%d.",
        duplicate_count,
        zero_kelvin_count,
        extreme_rain_count,
        invalid_datetime_count
    )

    return False

# ============================================================
# 13. Save Cleaned Data
# ============================================================

def save_cleaned_data(df, output_path):
    """Save the cleaned dataset to a CSV file."""
    try:
        df.to_csv(output_path, index=False)

        logger.info(
            "Cleaned dataset saved successfully to '%s': %d rows, %d columns.",
            output_path,
            df.shape[0],
            df.shape[1]
        )

        return True

    except OSError:
        logger.error(
            "Failed to save cleaned dataset to '%s'.",
            output_path,
            exc_info=True
        )
        return False

# ============================================================
# 14. Main Pipeline
# ============================================================

def main():
    """Run the complete traffic data-cleaning pipeline."""
    configure_logging()

    logger.info("Traffic data pipeline started.")

    try:
        # Step 1: Load raw data
        traffic_df = load_raw_data(RAW_DATA_PATH)

        if traffic_df is None:
            logger.error(
                "Pipeline stopped because the raw dataset could not be loaded."
            )
            return False

        # Step 2: Validate schema before any cleaning
        if not validate_schema(traffic_df, EXPECTED_COLUMNS):
            logger.error(
                "Pipeline stopped because schema validation failed."
            )
            return False

        # Step 3: Standardise categorical values
        traffic_df = standardise_categorical_values(
            traffic_df,
            CATEGORICAL_COLUMNS
        )

        # Step 4: Parse and validate date/time
        traffic_df = parse_datetime_column(traffic_df)

        # Step 5: Remove duplicate rows
        traffic_df = remove_duplicates(traffic_df)

        # Step 6: Impute impossible temperature values
        traffic_df = impute_zero_kelvin_by_month(traffic_df)

        # Step 7: Impute extreme rainfall values
        traffic_df = impute_extreme_rainfall(traffic_df)

        # Step 8: Final validation
        if not final_validation(traffic_df):
            logger.error(
                "Pipeline stopped because final validation failed."
            )
            return False

        # Step 9: Save cleaned dataset
        if not save_cleaned_data(traffic_df, CLEANED_DATA_PATH):
            logger.error(
                "Pipeline stopped because the cleaned dataset could not be saved."
            )
            return False

        logger.info("Traffic data pipeline completed successfully.")
        return True

    except Exception:
        logger.error(
            "Unexpected error prevented the pipeline from completing.",
            exc_info=True
        )
        return False

# ============================================================
# 15. Entry Point
# ============================================================

if __name__ == "__main__":
    main()