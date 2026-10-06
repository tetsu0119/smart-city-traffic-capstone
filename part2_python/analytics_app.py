

"""Interactive mini traffic analytics application."""

import logging
from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

PROCESSED_DATA_PATH = Path("engineered_traffic_data.csv")
LOG_PATH = Path("analytics_app.log")

logger = logging.getLogger(__name__)


# ============================================================
# Logging Configuration
# ============================================================

def configure_logging():
    """Configure console and file logging."""

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Prevent duplicate handlers if the code is re-run.
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Console: INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File: DEBUG and above
    file_handler = logging.FileHandler(
        LOG_PATH,
        mode="w"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# ============================================================
# Load Processed Dataset
# ============================================================

def load_processed_data(file_path):
    """Load and validate the processed traffic dataset."""

    required_columns = {
        "date_time",
        "traffic_volume",
        "weather_main",
        "weather_description",
        "temp",
        "congestion_category",
        "hour",
        "is_weekend",
        "holiday"
    }

    try:
        df = pd.read_csv(
            file_path,
            parse_dates=["date_time"]
        )

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            logger.error(
                "Processed dataset is missing required columns: %s",
                sorted(missing_columns)
            )
            return None

        logger.info(
            "Processed dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Processed dataset was not found: %s",
            file_path
        )
        return None

    except (pd.errors.ParserError, ValueError) as error:
        logger.error(
            "Unable to parse processed dataset: %s",
            error
        )
        return None

    except OSError as error:
        logger.error(
            "File I/O error while loading processed dataset: %s",
            error
        )
        return None


# ============================================================
# Helper Functions
# ============================================================

def build_unique_traffic_records(df):
    """Create one traffic observation for each unique timestamp."""

    records = (
        df
        .groupby("date_time", as_index=False)
        .agg(
            traffic_volume=("traffic_volume", "mean"),
            hour=("hour", "first"),
            is_weekend=("is_weekend", "first")
        )
    )

    records["date"] = records["date_time"].dt.date
    records["year"] = records["date_time"].dt.year

    return records


def parse_hour_input(value):
    """Validate and convert a user-entered hour."""

    text = str(value).strip()

    if ":" in text:
        parsed_time = pd.to_datetime(
            text,
            format="%H:%M",
            errors="raise"
        )

        if parsed_time.minute != 0:
            raise ValueError(
                "Only whole-hour values are supported."
            )

        hour = parsed_time.hour

    else:
        hour = int(text)

    if hour < 0 or hour > 23:
        raise ValueError(
            "Hour must be between 0 and 23."
        )

    return hour


def format_hour(hour):
    """Format an integer hour as HH:00."""

    return f"{int(hour):02d}:00"


# ============================================================
# Command 1 – Historical Traffic Lookup
# ============================================================

def query_historical_traffic(df, date_text, hour_text):
    """Retrieve traffic and weather for a selected date and hour."""

    logger.info(
        (
            "Command invoked: historical-lookup, "
            "arguments: date=%s, hour=%s"
        ),
        date_text,
        hour_text
    )

    # --------------------------------------------------------
    # Validate date
    # --------------------------------------------------------

    try:
        date_text = str(date_text).strip()

        if (
            len(date_text) != 10
            or date_text[4] != "-"
            or date_text[7] != "-"
        ):
            raise ValueError

        target_date = pd.to_datetime(
            date_text,
            format="%Y-%m-%d",
            errors="raise"
        )

        if target_date.strftime("%Y-%m-%d") != date_text:
            raise ValueError

    except (ValueError, TypeError):
        logger.error(
            "Invalid date input: %s",
            date_text
        )

        return {
            "success": False,
            "message": (
                "Invalid date. "
                "Please use YYYY-MM-DD format."
            )
        }

    # --------------------------------------------------------
    # Validate hour
    # --------------------------------------------------------

    try:
        hour_text = str(hour_text).strip()

        if not hour_text.isdigit():
            raise ValueError

        target_hour = int(hour_text)

        if target_hour < 0 or target_hour > 23:
            raise ValueError

    except (ValueError, TypeError):
        logger.error(
            "Invalid hour input: %s",
            hour_text
        )

        return {
            "success": False,
            "message": (
                "Invalid hour. "
                "Please enter a whole number from 0 to 23."
            )
        }

    # --------------------------------------------------------
    # Check whether selected date exists
    # --------------------------------------------------------

    selected_date_records = df.loc[
        df["date_time"].dt.date
        == target_date.date()
    ]

    if selected_date_records.empty:
        logger.warning(
            "No traffic data available for date=%s",
            date_text
        )

        return {
            "success": False,
            "message": (
                "No traffic data is available for the selected date. "
                "Please choose another date."
            )
        }

    # --------------------------------------------------------
    # Build selected hourly timestamp
    # --------------------------------------------------------

    target_datetime = (
        target_date
        + pd.Timedelta(hours=target_hour)
    )

    columns = [
        "date_time",
        "traffic_volume",
        "congestion_category",
        "weather_main",
        "weather_description",
        "temp"
    ]

    result = (
        df.loc[
            df["date_time"] == target_datetime,
            columns
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if result.empty:
        logger.warning(
            (
                "No traffic data available for "
                "date=%s, hour=%d"
            ),
            date_text,
            target_hour
        )

        return {
            "success": False,
            "message": (
                "Traffic data is available for this date, "
                "but not for the selected hour. "
                "Please choose another hour."
            )
        }

    logger.info(
        "Historical lookup returned %d matching record(s).",
        len(result)
    )

    return {
        "success": True,
        "data": result
    }


# ============================================================
# Command 2 – Travel Time Optimizer
# ============================================================

def optimize_travel_time(
    df,
    day_type,
    start_hour,
    end_hour
):
    """Find a lower-traffic hour within a user-defined travel window."""

    logger.info(
        (
            "Command invoked: travel-time-optimizer, "
            "arguments: day_type=%s, start_hour=%s, end_hour=%s"
        ),
        day_type,
        start_hour,
        end_hour
    )

    day_type_clean = str(day_type).strip().lower()

    if day_type_clean not in {"weekday", "weekend"}:
        logger.error(
            "Invalid day type: %s",
            day_type
        )

        return {
            "success": False,
            "message": (
                "Invalid day type. "
                "Please select Weekday or Weekend."
            )
        }

    try:
        start = parse_hour_input(start_hour)
        end = parse_hour_input(end_hour)

    except (ValueError, TypeError) as error:
        logger.error(
            "Invalid travel-time input: %s",
            error
        )

        return {
            "success": False,
            "message": (
                "Invalid travel time. "
                "Please enter a whole hour between 0 and 23."
            )
        }

    if start > end:
        logger.error(
            "Invalid travel window: start=%s, end=%s",
            start_hour,
            end_hour
        )

        return {
            "success": False,
            "message": (
                "The earliest travel hour must be before "
                "or equal to the latest travel hour."
            )
        }

    records = build_unique_traffic_records(df)

    weekend_flag = (
        1 if day_type_clean == "weekend" else 0
    )

    selected_records = records.loc[
        (records["is_weekend"] == weekend_flag)
        & (records["hour"] >= start)
        & (records["hour"] <= end)
    ].copy()

    if selected_records.empty:
        logger.warning(
            (
                "No historical records found for "
                "day_type=%s, start=%d, end=%d"
            ),
            day_type_clean,
            start,
            end
        )

        return {
            "success": False,
            "message": (
                "No historical traffic records were found "
                "for that travel window."
            )
        }

    hourly_summary = (
        selected_records
        .groupby("hour")["traffic_volume"]
        .agg(
            average_traffic="mean",
            median_traffic="median",
            observations="count"
        )
        .sort_index()
    )

    logger.debug(
        "Travel optimizer hourly summary: %s",
        hourly_summary.to_dict("index")
    )

    best_hour = int(
        hourly_summary["average_traffic"].idxmin()
    )

    busiest_hour = int(
        hourly_summary["average_traffic"].idxmax()
    )

    best_average = float(
        hourly_summary.loc[
            best_hour,
            "average_traffic"
        ]
    )

    busiest_average = float(
        hourly_summary.loc[
            busiest_hour,
            "average_traffic"
        ]
    )

    traffic_difference = (
        busiest_average - best_average
    )

    if busiest_average > 0:
        reduction_percentage = (
            traffic_difference
            / busiest_average
            * 100
        )
    else:
        reduction_percentage = 0.0

    logger.info(
        (
            "Travel optimizer completed: "
            "recommended_hour=%s, busiest_hour=%s"
        ),
        format_hour(best_hour),
        format_hour(busiest_hour)
    )

    return {
        "success": True,
        "day_type": day_type_clean.title(),
        "start_hour": start,
        "end_hour": end,
        "best_hour": best_hour,
        "best_average": best_average,
        "busiest_hour": busiest_hour,
        "busiest_average": busiest_average,
        "traffic_difference": traffic_difference,
        "reduction_percentage": reduction_percentage,
        "observations": len(selected_records)
    }


# ============================================================
# Command 3 – Holiday Driving Planner
# ============================================================

def get_available_holidays(df):
    """Return holiday names available in the dataset."""

    holiday_values = (
        df["holiday"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    holiday_values = holiday_values.loc[
        (holiday_values != "")
        & (holiday_values.str.lower() != "none")
    ]

    return sorted(
        holiday_values.unique().tolist()
    )


def holiday_driving_plan(df, holiday_name):
    """Analyse historical traffic for a selected holiday."""

    logger.info(
        (
            "Command invoked: holiday-driving-planner, "
            "arguments: holiday=%s"
        ),
        holiday_name
    )

    available_holidays = get_available_holidays(df)

    holiday_lookup = {
        holiday.lower(): holiday
        for holiday in available_holidays
    }

    requested_holiday = str(
        holiday_name
    ).strip().lower()

    if requested_holiday not in holiday_lookup:
        logger.error(
            "Invalid holiday selection: %s",
            holiday_name
        )

        return {
            "success": False,
            "message": (
                "Invalid holiday. "
                "Please select one of the available holidays."
            )
        }

    official_holiday_name = holiday_lookup[
        requested_holiday
    ]

    holiday_label_rows = df.loc[
        df["holiday"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        == official_holiday_name.lower()
    ].copy()

    holiday_dates = sorted(
        holiday_label_rows["date_time"]
        .dt.date
        .unique()
        .tolist()
    )

    if not holiday_dates:
        logger.error(
            "No historical dates found for holiday=%s",
            official_holiday_name
        )

        return {
            "success": False,
            "message": (
                "No historical dates were found "
                "for the selected holiday."
            )
        }

    records = build_unique_traffic_records(df)

    holiday_records = records.loc[
        records["date"].isin(holiday_dates)
    ].copy()

    practical_records = holiday_records.loc[
        holiday_records["hour"].between(6, 22)
    ].copy()

    if practical_records.empty:
        logger.warning(
            "No practical-hour records found for holiday=%s",
            official_holiday_name
        )

        return {
            "success": False,
            "message": (
                "No traffic records between 06:00 and 22:00 "
                "were found for the selected holiday."
            )
        }

    hourly_summary = (
        practical_records
        .groupby("hour")["traffic_volume"]
        .agg(
            average_traffic="mean",
            observations="count"
        )
        .sort_index()
    )

    best_hour = int(
        hourly_summary["average_traffic"].idxmin()
    )

    busiest_hour = int(
        hourly_summary["average_traffic"].idxmax()
    )

    best_hour_average = float(
        hourly_summary.loc[
            best_hour,
            "average_traffic"
        ]
    )

    busiest_hour_average = float(
        hourly_summary.loc[
            busiest_hour,
            "average_traffic"
        ]
    )

    def assign_period(hour):
        if 6 <= hour <= 11:
            return "Morning (06:00-11:00)"
        elif 12 <= hour <= 17:
            return "Afternoon (12:00-17:00)"
        else:
            return "Evening (18:00-22:00)"

    practical_records["travel_period"] = (
        practical_records["hour"]
        .apply(assign_period)
    )

    period_order = [
        "Morning (06:00-11:00)",
        "Afternoon (12:00-17:00)",
        "Evening (18:00-22:00)"
    ]

    period_summary = (
        practical_records
        .groupby("travel_period")[
            "traffic_volume"
        ]
        .mean()
        .reindex(period_order)
        .dropna()
    )

    best_period = str(
        period_summary.idxmin()
    )

    busiest_period = str(
        period_summary.idxmax()
    )

    best_period_average = float(
        period_summary.loc[
            best_period
        ]
    )

    busiest_period_average = float(
        period_summary.loc[
            busiest_period
        ]
    )

    logger.debug(
        "Holiday hourly summary for %s: %s",
        official_holiday_name,
        hourly_summary.to_dict("index")
    )

    logger.debug(
        "Holiday period summary for %s: %s",
        official_holiday_name,
        period_summary.to_dict()
    )

    logger.info(
        (
            "Holiday driving analysis completed for %s "
            "using %d historical date(s)."
        ),
        official_holiday_name,
        len(holiday_dates)
    )

    return {
        "success": True,
        "holiday": official_holiday_name,
        "holiday_dates": holiday_dates,
        "historical_dates": len(holiday_dates),
        "observations": len(practical_records),
        "best_hour": best_hour,
        "best_hour_average": best_hour_average,
        "busiest_hour": busiest_hour,
        "busiest_hour_average": busiest_hour_average,
        "best_period": best_period,
        "best_period_average": best_period_average,
        "busiest_period": busiest_period,
        "busiest_period_average": busiest_period_average
    }

# ============================================================
# User-Facing Result Display
# ============================================================

def display_historical_result(result):
    """Display Historical Traffic Lookup results."""

    if not result["success"]:
        print(f"\n{result['message']}")
        return

    print("\n" + "=" * 60)
    print("HISTORICAL TRAFFIC LOOKUP")
    print("=" * 60)

    print(
        result["data"].to_string(
            index=False
        )
    )


def display_optimizer_result(result):
    """Display Travel Time Optimizer results."""

    if not result["success"]:
        print(f"\n{result['message']}")
        return

    print("\n" + "=" * 60)
    print("TRAVEL TIME OPTIMIZER")
    print("=" * 60)

    print(
        f"Day type: {result['day_type']}"
    )

    print(
        f"Travel window: "
        f"{format_hour(result['start_hour'])}"
        f"-{format_hour(result['end_hour'])}"
    )

    print(
        f"Historical observations: "
        f"{result['observations']:,}"
    )

    print("\nRecommended lower-traffic time:")

    print(
        f"  {format_hour(result['best_hour'])}"
        f" | Average traffic: "
        f"{result['best_average']:,.0f}"
    )

    print("\nBusiest time in this window:")

    print(
        f"  {format_hour(result['busiest_hour'])}"
        f" | Average traffic: "
        f"{result['busiest_average']:,.0f}"
    )

    print(
        f"\nHistorical traffic difference: "
        f"{result['traffic_difference']:,.0f} vehicles"
    )

    print(
        f"Potential reduction: "
        f"{result['reduction_percentage']:.1f}%"
    )

    print(
        "\nNote: This recommendation is based on historical "
        "traffic patterns, not a real-time forecast."
    )


def display_holiday_result(result):
    """Display Holiday Driving Planner results."""

    if not result["success"]:
        print(f"\n{result['message']}")
        return

    print("\n" + "=" * 60)
    print("HOLIDAY DRIVING PLANNER")
    print("=" * 60)

    print(
        f"Holiday: {result['holiday']}"
    )

    print(
        f"Historical dates used: "
        f"{result['historical_dates']}"
    )

    print(
        "Years analysed: "
        + ", ".join(
            str(date.year)
            for date in result["holiday_dates"]
        )
    )

    print(
        f"Traffic observations: "
        f"{result['observations']:,}"
    )

    print(
        "Driving hours analysed: 06:00-22:00"
    )

    print("\nRecommended historical travel period:")

    print(
        f"  {result['best_period']}"
        f" | Average traffic: "
        f"{result['best_period_average']:,.0f}"
    )

    print("\nHistorically busiest period:")

    print(
        f"  {result['busiest_period']}"
        f" | Average traffic: "
        f"{result['busiest_period_average']:,.0f}"
    )

    print("\nLower-traffic historical hour:")

    print(
        f"  {format_hour(result['best_hour'])}"
        f" | Average traffic: "
        f"{result['best_hour_average']:,.0f}"
    )

    print("\nHistorically busiest hour:")

    print(
        f"  {format_hour(result['busiest_hour'])}"
        f" | Average traffic: "
        f"{result['busiest_hour_average']:,.0f}"
    )

    print(
        "\nNote: This is historical planning guidance "
        "based on available records, not a forecast."
    )


# ============================================================
# Interactive Command-Line Menu
# ============================================================

def main_menu(df):
    """Run the interactive Smart City Traffic Analytics application."""

    while True:

        print("\n" + "=" * 60)
        print("             SMART CITY TRAFFIC ANALYTICS")
        print("=" * 60)

        print("\n1. Historical Traffic Lookup")
        print(
            "   Check traffic, congestion and weather "
            "for a specific historical date and hour."
        )

        print("\n2. Travel Time Optimizer")
        print(
            "   Find a lower-traffic hour within "
            "your available travel window."
        )

        print("\n3. Holiday Driving Planner")
        print(
            "   Use historical holiday traffic to "
            "identify better driving periods."
        )

        print("\n4. Exit")

        choice = input(
            "\nSelect a menu number (1-4): "
        ).strip()

        # ----------------------------------------------------
        # Command 1
        # ----------------------------------------------------

        if choice == "1":

            print("\n" + "-" * 60)
            print("You selected: Historical Traffic Lookup")
            print("-" * 60)

            date_text = input(
                "\nEnter date (YYYY-MM-DD): "
            ).strip()

            hour_text = input(
                "Enter hour (0-23): "
            ).strip()

            result = query_historical_traffic(
                df,
                date_text,
                hour_text
            )

            display_historical_result(
                result
            )

        # ----------------------------------------------------
        # Command 2
        # ----------------------------------------------------

        elif choice == "2":

            print("\n" + "-" * 60)
            print("You selected: Travel Time Optimizer")
            print("-" * 60)

            print("\nSelect day type:")
            print("1. Weekday")
            print("2. Weekend")

            day_choice = input(
                "\nSelect 1 or 2: "
            ).strip()

            if day_choice == "1":
                day_type = "weekday"

            elif day_choice == "2":
                day_type = "weekend"

            else:
                logger.info(
                    (
                        "Command invoked: travel-time-optimizer, "
                        "arguments: day_selection=%s"
                    ),
                    day_choice
                )

                logger.error(
                    "Invalid day-type selection: %s",
                    day_choice
                )

                print(
                    "\nInvalid selection. "
                    "Please select 1 or 2."
                )

                continue

            print(
                "\nEnter the time window in which "
                "you are able to travel."
            )

            start_hour = input(
                "\nEarliest travel hour (0-23): "
            ).strip()

            end_hour = input(
                "Latest travel hour (0-23): "
            ).strip()

            result = optimize_travel_time(
                df,
                day_type,
                start_hour,
                end_hour
            )

            display_optimizer_result(
                result
            )

        # ----------------------------------------------------
        # Command 3
        # ----------------------------------------------------

        elif choice == "3":

            print("\n" + "-" * 60)
            print("You selected: Holiday Driving Planner")
            print("-" * 60)

            holidays = get_available_holidays(
                df
            )

            if not holidays:
                logger.error(
                    "No holiday information is available in the dataset."
                )

                print(
                    "\nNo holiday information is available "
                    "in the dataset."
                )

                continue

            print("\nAvailable holidays:")

            for number, holiday in enumerate(
                holidays,
                start=1
            ):
                print(
                    f"{number}. {holiday}"
                )

            selection = input(
                "\nSelect a holiday number: "
            ).strip()

            try:
                holiday_number = int(
                    selection
                )

                if not 1 <= holiday_number <= len(holidays):
                    raise ValueError

            except ValueError:

                logger.info(
                    (
                        "Command invoked: holiday-driving-planner, "
                        "arguments: selection=%s"
                    ),
                    selection
                )

                logger.error(
                    "Invalid holiday selection: %s",
                    selection
                )

                print(
                    "\nInvalid holiday selection. "
                    "Please choose a number from the list."
                )

                continue

            selected_holiday = holidays[
                holiday_number - 1
            ]

            result = holiday_driving_plan(
                df,
                selected_holiday
            )

            display_holiday_result(
                result
            )

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        elif choice == "4":

            logger.info(
                "Command invoked: exit, arguments: none"
            )

            print("\n" + "-" * 60)
            print("Exiting Smart City Traffic Analytics.")
            print("-" * 60)

            break

        # ----------------------------------------------------
        # Invalid Menu Selection
        # ----------------------------------------------------

        else:

            logger.error(
                "Invalid menu selection: %s",
                choice
            )

            print(
                "\nInvalid choice. "
                "Please enter a number from 1 to 4."
            )


# ============================================================
# Application Entry Point
# ============================================================

def main():
    """Start the traffic analytics application."""

    configure_logging()

    logger.info(
        "Starting Smart City Traffic Analytics application."
    )

    traffic_df = load_processed_data(
        PROCESSED_DATA_PATH
    )

    if traffic_df is None:
        logger.error(
            "Application cannot start because the dataset could not be loaded."
        )
        return

    main_menu(
        traffic_df
    )

    logger.info(
        "Smart City Traffic Analytics application ended normally."
    )


# ============================================================
# Run Application
# ============================================================

if __name__ == "__main__":
    main()

