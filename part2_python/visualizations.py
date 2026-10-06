"""Matplotlib visualisation workflow for the engineered traffic dataset."""

# ============================================================
# Task 3 – Visualise Traffic Patterns
# ============================================================

# 1. Imports
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# 2. Logger
logger = logging.getLogger(__name__)


# 3. Configuration
ENGINEERED_DATA_PATH = Path("engineered_traffic_data.csv")
FIGURES_DIR = Path("figures")
LOG_PATH = Path("visualisation.log")

EXPECTED_FIGURES = [
    FIGURES_DIR / "traffic_by_hour.png",
    FIGURES_DIR / "weekday_vs_weekend.png",
    FIGURES_DIR / "traffic_by_weather.png",
    FIGURES_DIR / "temperature_vs_traffic.png",
]

# ============================================================
# 4. Logging Configuration
# ============================================================

def configure_logging():
    """Configure console and file logging for visualisation."""

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Console handler: INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler: DEBUG and above
    file_handler = logging.FileHandler(
        LOG_PATH,
        mode="w"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# ============================================================
# 5. Load Engineered Data
# ============================================================

def load_engineered_data(file_path):
    """Load the engineered traffic dataset for visualisation."""
    try:
        df = pd.read_csv(
            file_path,
            parse_dates=["date_time"]
        )

        logger.info(
            "Engineered dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Engineered dataset was not found: %s",
            file_path,
            exc_info=True
        )
        return None

    except (pd.errors.ParserError, ValueError):
        logger.error(
            "Failed to parse the engineered dataset: %s",
            file_path,
            exc_info=True
        )
        return None

    except OSError:
        logger.error(
            "File I/O error while reading engineered dataset: %s",
            file_path,
            exc_info=True
        )
        return None

# ============================================================
# 6. Traffic Demand by Hour
# ============================================================

def plot_traffic_by_hour(df):
    """Create and save average traffic volume by hour of day."""

    hourly_traffic = (
        df
        .groupby("hour")["traffic_volume"]
        .mean()
        .sort_index()
    )

    figure_path = FIGURES_DIR / "traffic_by_hour.png"

    plt.figure(figsize=(10, 6))

    plt.plot(
        hourly_traffic.index,
        hourly_traffic.values,
        marker="o"
    )

    plt.title("Average Traffic Volume by Hour of Day")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Traffic Volume")
    plt.xticks(range(0, 24))
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    logger.info(
        "Figure saved successfully to '%s'.",
        figure_path
    )

    plt.close()

# ============================================================
# 7. Weekday vs Weekend Traffic
# ============================================================

def plot_weekday_vs_weekend(df):
    """Create and save weekday versus weekend traffic patterns."""

    weekday_weekend_traffic = (
        df
        .groupby(["hour", "is_weekend"])["traffic_volume"]
        .mean()
        .unstack()
    )

    weekday_weekend_traffic.columns = [
        "Weekday",
        "Weekend"
    ]

    figure_path = FIGURES_DIR / "weekday_vs_weekend.png"

    plt.figure(figsize=(10, 6))

    plt.plot(
        weekday_weekend_traffic.index,
        weekday_weekend_traffic["Weekday"],
        marker="o",
        label="Weekday"
    )

    plt.plot(
        weekday_weekend_traffic.index,
        weekday_weekend_traffic["Weekend"],
        marker="o",
        label="Weekend"
    )

    plt.title("Average Traffic Volume: Weekday vs Weekend")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Traffic Volume")
    plt.xticks(range(0, 24))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    logger.info(
        "Figure saved successfully to '%s'.",
        figure_path
    )

    plt.close()

# ============================================================
# 8. Traffic by Weather Condition
# ============================================================

def plot_traffic_by_weather(df):
    """Create and save average traffic volume by weather condition."""

    weather_summary = (
        df
        .groupby("weather_main")["traffic_volume"]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
    )

    logger.debug(
        "Weather condition summary: %s",
        weather_summary.to_dict("index")
    )

    weather_plot_data = weather_summary.sort_values(
        "mean",
        ascending=True
    )

    figure_path = FIGURES_DIR / "traffic_by_weather.png"

    plt.figure(figsize=(10, 7))

    plt.barh(
        weather_plot_data.index,
        weather_plot_data["mean"]
    )

    plt.title("Average Traffic Volume by Weather Condition")
    plt.xlabel("Average Traffic Volume")
    plt.ylabel("Weather Condition")
    plt.grid(
        axis="x",
        alpha=0.3
    )
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    logger.info(
        "Figure saved successfully to '%s'.",
        figure_path
    )

    plt.close()

# ============================================================
# 9. Temperature vs Traffic Volume
# ============================================================

def plot_temperature_vs_traffic(df):
    """Create and save a scatter plot of temperature versus traffic volume."""

    figure_path = FIGURES_DIR / "temperature_vs_traffic.png"

    plt.figure(figsize=(10, 6))

    plt.scatter(
        df["temp"],
        df["traffic_volume"],
        alpha=0.2,
        s=15
    )

    plt.title("Temperature vs Traffic Volume")
    plt.xlabel("Temperature (Kelvin)")
    plt.ylabel("Traffic Volume")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    logger.info(
        "Figure saved successfully to '%s'.",
        figure_path
    )

    plt.close()
    
# ============================================================
# 10. Validate Saved Figures
# ============================================================

def validate_saved_figures():
    """Validate that all expected visualisation files were saved."""

    missing_figures = []

    for figure_path in EXPECTED_FIGURES:
        if figure_path.exists():
            logger.info(
                "Validated saved figure: '%s'.",
                figure_path
            )
        else:
            logger.error(
                "Expected figure was not found: '%s'.",
                figure_path
            )
            missing_figures.append(figure_path)

    if missing_figures:
        return False

    logger.info(
        "Figure validation successful. All %d expected figures were saved.",
        len(EXPECTED_FIGURES)
    )

    return True

# ============================================================
# 11. Main Visualisation Workflow
# ============================================================

def main():
    """Run the complete traffic visualisation workflow."""
    configure_logging()

    logger.info("Visualisation workflow started.")

    try:
        # Step 1: Load engineered data
        traffic_df = load_engineered_data(ENGINEERED_DATA_PATH)

        if traffic_df is None:
            logger.error(
                "Visualisation workflow stopped because the engineered "
                "dataset could not be loaded."
            )
            return False

        # Step 2: Create output directory
        FIGURES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Figures will be saved to '%s'.",
            FIGURES_DIR
        )

        # Step 3: Generate visualisations
        plot_traffic_by_hour(traffic_df)
        plot_weekday_vs_weekend(traffic_df)
        plot_traffic_by_weather(traffic_df)
        plot_temperature_vs_traffic(traffic_df)

        # Step 4: Validate saved figures
        if not validate_saved_figures():
            logger.error(
                "Visualisation workflow stopped because figure "
                "validation failed."
            )
            return False

        logger.info(
            "Visualisation workflow completed successfully."
        )
        return True

    except Exception:
        logger.error(
            "Unexpected error prevented the visualisation workflow "
            "from completing.",
            exc_info=True
        )
        return False

# ============================================================
# 12. Entry Point
# ============================================================

if __name__ == "__main__":
    main()