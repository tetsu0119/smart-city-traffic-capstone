# Smart City Traffic Intelligence – Part 2

## Python Programming, Data Pipeline and Traffic Analytics

This folder contains Part 2 of the Smart City Traffic Intelligence Capstone Project for the NUS School of Computing AI, Machine Learning and Data Science programme.

Part 2 develops a reproducible Python workflow for cleaning, transforming, analysing and visualising traffic data. It also includes an interactive command-line application that allows users to query historical traffic patterns and obtain data-driven travel guidance.

---

## Project Workflow

The Part 2 workflow consists of four main stages:

```text
Raw Traffic Dataset
        |
        v
    pipeline.py
        |
        v
cleaned_traffic_data.csv
        |
        v
feature_engineering.py
        |
        v
engineered_traffic_data.csv
        |
        +----------------------+
        |                      |
        v                      v
visualizations.py       analytics_app.py
        |                      |
        v                      v
    figures/          Interactive CLI Application
```

---

## Main Files

- `pipeline.py` – loads, validates and cleans the raw traffic dataset
- `feature_engineering.py` – creates engineered features for traffic analysis
- `visualizations.py` – generates and saves traffic visualisations
- `analytics_app.py` – provides the interactive traffic analytics application
- `pipeline.log` – sample levelled pipeline log
- `figures/` – generated traffic visualisations

Development notebooks are also included for implementation, testing and documentation.

---

## 1. Data Pipeline

`pipeline.py` performs the main data loading, validation and cleaning workflow.

The pipeline includes:

- Raw CSV loading
- Schema validation
- Categorical data validation
- Date/time validation
- Duplicate detection and removal
- Imputation of invalid zero-Kelvin temperature records
- Treatment of extreme rainfall values
- Final data validation
- Saving of the cleaned dataset
- Levelled logging of pipeline events

The raw dataset contains:

```text
48,204 rows
9 columns
```

After cleaning and validation, the resulting dataset contains:

```text
48,187 rows
9 columns
```

The cleaned dataset is saved as:

```text
cleaned_traffic_data.csv
```

---

## 2. Feature Engineering

`feature_engineering.py` loads the cleaned traffic dataset and creates additional features for traffic analysis.

The engineered features include:

- Hour of day
- Day of week
- Weekend indicator
- Cyclical hour features (`hour_sin` and `hour_cos`)
- Rain indicator
- Snow indicator
- One-hot encoded weather categories
- Min-Max scaled weather variables
- Congestion category derived from traffic-volume quartiles

The congestion category is derived from the traffic-volume distribution rather than arbitrary fixed thresholds.

The final engineered dataset contains:

```text
48,187 rows
30 columns
```

The engineered dataset is saved as:

```text
engineered_traffic_data.csv
```

---

## 3. Traffic Visualisations

`visualizations.py` loads the engineered traffic dataset and generates four analytical figures.

The generated figures are:

1. `traffic_by_hour.png`
2. `weekday_vs_weekend.png`
3. `traffic_by_weather.png`
4. `temperature_vs_traffic.png`

All figures are saved automatically in:

```text
figures/
```

The visualisations examine:

- Average traffic volume by hour
- Differences between weekday and weekend traffic patterns
- Traffic volume under different weather conditions
- The relationship between temperature and traffic volume

The visualisation workflow also validates that all four expected figures have been successfully saved to disk.

---

## 4. Mini Traffic Analytics Application

`analytics_app.py` provides an interactive command-line application for querying the processed traffic dataset.

The application provides three different analytics commands.

### Command 1 – Historical Traffic Lookup

The user enters a historical date and hour.

The application retrieves:

- Traffic volume
- Congestion category
- Weather condition
- Weather description
- Temperature

Invalid dates and hours are handled with clear messages.

If no traffic data is available for the selected date, the application asks the user to choose another date. If the date exists but the selected hour is unavailable, the user is asked to choose another hour.

### Command 2 – Travel Time Optimizer

The user selects:

- Weekday or weekend travel
- Earliest acceptable travel hour
- Latest acceptable travel hour

The application analyses historical traffic records within the selected travel window and identifies:

- A historically lower-traffic travel hour
- The busiest hour within the selected window
- Average traffic volume at both times
- Historical traffic-volume difference
- Potential percentage reduction

The recommendation is based on historical traffic patterns and is not a real-time traffic forecast.

### Command 3 – Holiday Driving Planner

The user selects a holiday available in the historical dataset.

The application analyses complete historical dates associated with the selected holiday and evaluates traffic between 06:00 and 22:00.

The application identifies:

- Recommended historical travel period
- Historically busiest travel period
- Lower-traffic historical hour
- Historically busiest hour
- Number of historical holiday dates analysed

The result provides historical planning guidance rather than a future traffic forecast.

---

## Logging and Error Handling

Python's `logging` module is used for internal status, progress, warnings and errors.

The main data-cleaning pipeline generates:

```text
pipeline.log
```

The log provides a clear, levelled trail of pipeline events using `DEBUG`, `INFO`, `WARNING` and `ERROR` levels where appropriate.

Logged events include:

- Pipeline start and completion
- Raw dataset loading
- Schema validation
- Date/time validation
- Duplicate detection and removal
- Temperature imputation
- Rainfall correction
- Final validation
- Output file creation

The mini analytics application logs command invocations and their arguments at INFO level and records invalid user input at ERROR level.

`print()` is used in the mini application only for output intended directly for the command-line user, rather than for internal status or progress reporting.

Invalid dates, hours, menu selections, holiday selections and unavailable traffic records are handled with clear messages rather than raw Python tracebacks during normal application use.

---

## How to Run Part 2

Run the scripts from the `part2_python` directory.

### Step 1 – Run the Data-Cleaning Pipeline

```bash
python pipeline.py
```

This generates or updates:

```text
cleaned_traffic_data.csv
pipeline.log
```

### Step 2 – Run Feature Engineering

```bash
python feature_engineering.py
```

This generates:

```text
engineered_traffic_data.csv
```

### Step 3 – Generate the Visualisations

```bash
python visualizations.py
```

The generated PNG files are saved in:

```text
figures/
```

### Step 4 – Run the Mini Analytics Application

```bash
python analytics_app.py
```

The application displays the following interactive menu:

```text
============================================================
             SMART CITY TRAFFIC ANALYTICS
============================================================

1. Historical Traffic Lookup
2. Travel Time Optimizer
3. Holiday Driving Planner
4. Exit
```

The user can continue selecting commands until Exit is selected.

---

## Recommended Execution Order

For complete reproducibility, execute the scripts in the following order:

```text
1. python pipeline.py
2. python feature_engineering.py
3. python visualizations.py
4. python analytics_app.py
```

The workflow is:

```text
Raw Traffic Dataset
        |
        v
    pipeline.py
        |
        v
cleaned_traffic_data.csv
        |
        v
feature_engineering.py
        |
        v
engineered_traffic_data.csv
        |
        +----------------------+
        |                      |
        v                      v
visualizations.py       analytics_app.py
        |                      |
        v                      v
    figures/          Interactive CLI Application
```

---

## Error Handling and Validation

The Part 2 workflow includes validation and exception handling for common problems such as:

- Missing input files
- Missing required columns
- Invalid date/time values
- Duplicate records
- Invalid temperature values
- Extreme rainfall values
- Invalid user-entered dates
- Invalid user-entered hours
- Invalid menu selections
- Invalid holiday selections
- Missing historical traffic records

The scripts use logging and controlled error handling so that expected problems are reported clearly rather than producing raw Python tracebacks during normal use.

---

## Part 2 Validation

The Part 2 workflow has been tested from the command line.

The following components executed successfully:

```text
pipeline.py              PASS
feature_engineering.py   PASS
visualizations.py        PASS
analytics_app.py         PASS
```

The data-cleaning pipeline successfully processed the raw dataset from 48,204 rows to a validated cleaned dataset containing 48,187 rows.

Feature engineering successfully produced an engineered dataset containing 48,187 rows and 30 columns.

The visualisation workflow successfully generated and validated four figures.

The command-line application was tested with all three analytics commands and the Exit function.

---

## Part 2 Deliverables

The Part 2 submission includes:

- `pipeline.py`
- `feature_engineering.py`
- `visualizations.py`
- `analytics_app.py`
- Generated figures in `figures/`
- `pipeline.log`
- Part 2 `README.md`
- Short methodology and findings report

---

## Reproducibility

The project is designed so that the Part 2 workflow can be reproduced from the raw traffic dataset.

Each processing stage validates its required inputs and generates the files required by the next stage.

Python logging provides a traceable record of important processing events, warnings and errors.

Git and GitHub are used to maintain incremental development history and version control for the project.

---

## Author

Tetsuya

