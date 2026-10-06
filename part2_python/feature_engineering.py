"""Feature engineering pipeline for the cleaned Metro Interstate Traffic dataset."""

# ============================================================
# Task 2 – Feature Engineering (NumPy and Pandas)
# ============================================================

# 1. Imports
import logging
from pathlib import Path

import numpy as np
import pandas as pd


# 2. Logger
logger = logging.getLogger(__name__)


# 3. Configuration
CLEANED_DATA_PATH = Path("cleaned_traffic_data.csv")
ENGINEERED_DATA_PATH = Path("engineered_traffic_data.csv")
LOG_PATH = Path("feature_engineering.log")

REQUIRED_FEATURES = [
    "hour",
    "day_of_week",
    "is_weekend",
    "hour_sin",
    "hour_cos",
    "has_rain",
    "has_snow",
    "temp_scaled",
    "clouds_all_scaled",
    "congestion_category",
]

# ============================================================
# 4. Logging Configuration
# ============================================================

def configure_logging():
    """Configure console and file logging for feature engineering."""

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
# 5. Load Cleaned Data
# ============================================================

def load_cleaned_data(file_path):
    """Load the cleaned traffic dataset for feature engineering."""
    try:
        df = pd.read_csv(
            file_path,
            parse_dates=["date_time"]
        )

        logger.info(
            "Cleaned dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Cleaned dataset was not found: %s",
            file_path,
            exc_info=True
        )
        return None

    except (pd.errors.ParserError, ValueError):
        logger.error(
            "Failed to parse the cleaned dataset: %s",
            file_path,
            exc_info=True
        )
        return None

    except OSError:
        logger.error(
            "File I/O error while reading cleaned dataset: %s",
            file_path,
            exc_info=True
        )
        return None

# ============================================================
# 6. Create Time Features
# ============================================================

def create_time_features(df):
    """Create time-based and cyclical features from date_time."""
    df = df.copy()

    df["hour"] = df["date_time"].dt.hour
    df["day_of_week"] = df["date_time"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    logger.info(
        "Created time features: hour, day_of_week, is_weekend, "
        "hour_sin, and hour_cos."
    )

    return df  

# ============================================================
# 7. Create Weather Features
# ============================================================

def create_weather_features(df):
    """Create encoded and derived weather features."""
    df = df.copy()

    # Derived binary weather indicators
    df["has_rain"] = (df["rain_1h"] > 0).astype(int)
    df["has_snow"] = (df["snow_1h"] > 0).astype(int)

    # One-hot encode the main weather category
    weather_dummies = pd.get_dummies(
        df["weather_main"],
        prefix="weather",
        dtype=int
    )

    df = pd.concat(
        [df, weather_dummies],
        axis=1
    )

    logger.info(
        "Created weather features: has_rain, has_snow, and %d "
        "one-hot encoded weather_main columns.",
        weather_dummies.shape[1]
    )

    return df

# ============================================================
# 8. Scale Numerical Features
# ============================================================

def create_scaled_features(df):
    """Create Min-Max scaled versions of selected continuous variables."""
    df = df.copy()

    columns_to_scale = ["temp", "clouds_all"]

    for column in columns_to_scale:
        column_min = df[column].min()
        column_max = df[column].max()

        logger.debug(
            "%s scaling range: min=%.2f, max=%.2f.",
            column,
            column_min,
            column_max
        )

        if column_max == column_min:
            df[f"{column}_scaled"] = 0.0

            logger.warning(
                "Column '%s' has no variation; scaled values set to 0.",
                column
            )
        else:
            df[f"{column}_scaled"] = (
                (df[column] - column_min)
                / (column_max - column_min)
            )

    logger.info(
        "Created Min-Max scaled features for: %s.",
        ", ".join(columns_to_scale)
    )

    return df

# ============================================================
# 9. Create Congestion Category
# ============================================================

def create_congestion_category(df):
    """Create a data-driven congestion category using traffic-volume quartiles."""
    df = df.copy()

    q1 = df["traffic_volume"].quantile(0.25)
    q3 = df["traffic_volume"].quantile(0.75)

    logger.debug(
        "Congestion thresholds calculated: Q1=%.2f, Q3=%.2f.",
        q1,
        q3
    )

    conditions = [
        df["traffic_volume"] <= q1,
        df["traffic_volume"] > q3
    ]

    choices = [
        "Low",
        "High"
    ]

    df["congestion_category"] = np.select(
        conditions,
        choices,
        default="Medium"
    )

    logger.info(
        "Created congestion_category using traffic-volume quartiles."
    )

    return df

# ============================================================
# 10. Validate Engineered Features
# ============================================================

def validate_engineered_features(df):
    """Validate that required engineered features exist and contain no missing values."""

    missing_features = [
        feature for feature in REQUIRED_FEATURES
        if feature not in df.columns
    ]

    if missing_features:
        logger.error(
            "Feature validation failed. Missing features: %s",
            missing_features
        )
        return False

    missing_values = df[REQUIRED_FEATURES].isna().sum()
    features_with_missing = missing_values[
        missing_values > 0
    ]

    if not features_with_missing.empty:
        logger.error(
            "Feature validation failed. Missing values detected: %s",
            features_with_missing.to_dict()
        )
        return False

    logger.info(
        "Feature validation successful. All %d required features are present "
        "with no missing values.",
        len(REQUIRED_FEATURES)
    )

    return True

# ============================================================
# 11. Save Engineered Data
# ============================================================

def save_engineered_data(df, output_path):
    """Save the engineered dataset to a CSV file."""
    try:
        df.to_csv(
            output_path,
            index=False
        )

        logger.info(
            "Engineered dataset saved successfully to '%s': %d rows, %d columns.",
            output_path,
            df.shape[0],
            df.shape[1]
        )

        return True

    except OSError:
        logger.error(
            "Failed to save engineered dataset to '%s'.",
            output_path,
            exc_info=True
        )
        return False

# ============================================================
# 12. Main Feature Engineering Pipeline
# ============================================================

def main():
    """Run the complete feature-engineering pipeline."""
    configure_logging()

    logger.info("Feature engineering pipeline started.")

    try:
        # Step 1: Load cleaned data
        traffic_df = load_cleaned_data(CLEANED_DATA_PATH)

        if traffic_df is None:
            logger.error(
                "Feature engineering stopped because the cleaned dataset "
                "could not be loaded."
            )
            return False

        # Log shape before feature engineering
        logger.info(
            "Dataset shape before feature engineering: %d rows, %d columns.",
            traffic_df.shape[0],
            traffic_df.shape[1]
        )

        # Step 2: Create time features
        traffic_df = create_time_features(traffic_df)

        # Step 3: Create weather features
        traffic_df = create_weather_features(traffic_df)

        # Step 4: Scale numerical features
        traffic_df = create_scaled_features(traffic_df)

        # Step 5: Create congestion target
        traffic_df = create_congestion_category(traffic_df)

        # Step 6: Validate engineered features
        if not validate_engineered_features(traffic_df):
            logger.error(
                "Feature engineering stopped because final validation failed."
            )
            return False

        # Log shape after feature engineering
        logger.info(
            "Dataset shape after feature engineering: %d rows, %d columns.",
            traffic_df.shape[0],
            traffic_df.shape[1]
        )

        # Step 7: Save engineered dataset
        if not save_engineered_data(
            traffic_df,
            ENGINEERED_DATA_PATH
        ):
            logger.error(
                "Feature engineering stopped because the engineered dataset "
                "could not be saved."
            )
            return False

        logger.info(
            "Feature engineering pipeline completed successfully."
        )
        return True

    except Exception:
        logger.error(
            "Unexpected error prevented feature engineering from completing.",
            exc_info=True
        )
        return False

# ============================================================
# 13. Entry Point
# ============================================================

if __name__ == "__main__":
    main()