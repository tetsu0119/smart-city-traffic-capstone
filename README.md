# Smart City Traffic Intelligence

## From Data Analytics to AI-Powered Mobility

**Capstone Project**  
**NUS School of Computing – AI, Machine Learning and Data Science**  
**Author: Tetsuya Tanaka**

## 1. Project Overview

This repository contains an end-to-end Smart City Traffic Intelligence capstone project developed as part of the NUS School of Computing AI, Machine Learning and Data Science programme.

The project integrates data analytics, SQL, Python programming, machine learning, deep learning, explainable AI, recommendation systems, and MLOps to analyse historical traffic patterns and develop an AI-powered mobility decision-support prototype.

The solution is organised into three interconnected parts:

- **Part 1 – Data Analytics:** Statistical analysis, SQL, and Power BI.
- **Part 2 – Python Programming:** Data processing, feature engineering, visualisation, and application development.
- **Part 3 – Machine Learning and AI:** Predictive modelling, explainability, recommendation systems, experiment tracking, deployment simulation, and responsible AI.
The project uses historical traffic observations from the westbound I-94 corridor near Minneapolis–St. Paul, Minnesota, covering approximately 2012–2018.

## 2. Important Data Limitation

**No real accident dataset was used in this project.**

Accident risk was represented using a documented proxy based on congestion derived from traffic volume together with severe or low-visibility weather conditions.

This proxy does not represent observed accidents or verified accident probabilities.

Similarly, the recommendation system identifies historically lower-traffic travel periods rather than safer routes or guaranteed reductions in accident risk.

The results should be interpreted as a historical traffic intelligence prototype, not a production-ready road safety or real-time navigation system.

## 3. Repository Structure

```text
smart-city-traffic-capstone/
├── README.md
├── .gitignore
├── .gitattributes
├── part1_data_analytics/
│   └── [Part 1 deliverables]
├── part2_python/
│   ├── README.md
│   ├── pipeline.py
│   ├── feature_engineering.py
│   ├── visualizations.py
│   ├── analytics_app.py
│   ├── cleaned_traffic_data.csv
│   ├── engineered_traffic_data.csv
│   ├── figures/
│   └── [Part 2 notebooks and report]
└── part3_machine_learning/
├── README.md
├── task1_supervised_ml.ipynb
├── task2_unsupervised_ml.ipynb
├── task3_deep_learning_explainability.ipynb
├── task4_mlflow_experiment_tracking.ipynb
├── task5_traffic_recommendation_system.ipynb
├── task6_mlops_deployment_simulation.ipynb
├── task7_responsible_sustainable_ai.ipynb
├── mlflow_tracking.db
├── mlruns/
├── deployment_features.txt
├── figures/
├── final_capstone_report.pdf
└── responsible_ai_report.docx
```

Each project part contains its own supporting deliverables. Part 2 and Part 3 include dedicated README files for further implementation details.

## 4. Part 1 – Data Analytics

Part 1 establishes the analytical foundation of the project through:

- SQL-based traffic data analysis.

- Descriptive statistics and correlation analysis.

- Probability and conditional probability.

- Traffic and weather data exploration.

- Power BI dashboard development.

- Interpretation of analytical findings.

The interactive Power BI dashboard is stored in:

`part1_data_analytics/traffic_intelligence_dashboard.pbix`

It can be opened using Power BI Desktop.

## 5. Part 2 – Python Programming

Part 2 implements reusable Python components for data processing and exploratory analysis.

The main components include:

- Data cleaning and validation pipelines.

- Exception handling and structured logging.

- Feature engineering using NumPy and Pandas.

- Traffic data visualisation.

- A Python analytics mini-application.

- Reusable scripts and Jupyter notebooks.

The cleaned and engineered datasets provide the analytical foundation for Part 3.

Key scripts include:

- `pipeline.py`

- `feature_engineering.py`

- `visualizations.py`

- `analytics_app.py`

Detailed instructions are available in part2_python/README.md.

## 6. Part 3 – Machine Learning and AI

Part 3 extends the project into predictive modelling and operational AI.

### Task 1 – Supervised Machine Learning

Classification and regression models were developed to analyse traffic conditions and predict hourly traffic volume.

The Random Forest Classifier achieved an accuracy of 0.9851 and an F1-score of 0.9359 on the documented proxy classification task.

The Random Forest Regressor achieved an MAE of 271.3004 and an R² of 0.9442 in the recorded MLflow regression experiment.

### Task 2 – Unsupervised Machine Learning

K-means clustering and Apriori association rule mining were used to identify historical traffic patterns.

The selected K-means solution used six clusters and achieved a silhouette score of 0.5254.

Association rule mining identified relationships between travel periods, weather conditions, and congestion levels.

### Task 3 – Deep Learning and Explainability

A feed-forward neural network was developed using TensorFlow and Keras.

The neural network achieved an MAE of 297.8235 and an R² of 0.9395.

SHAP explainability was applied to a comparable Random Forest model to identify influential temporal features.

### Task 4 – MLflow Experiment Tracking

MLflow was used to record model configurations, evaluation metrics, and experiment histories.

The experiments were stored in a local SQLite tracking database.

### Task 5 – Traffic Recommendation System

A historical traffic recommendation system was developed to identify lower-traffic travel periods based on day type, preferred travel hours, and weather conditions.

The system includes minimum observation requirements, fallback handling, input validation, and plain-language recommendations.

### Task 6 – MLOps and Deployment Simulation

The selected Random Forest regression model was reconstructed and logged as a deployment artifact.

A FastAPI /predict endpoint was tested locally.

Simulated monitoring used a baseline MAE of 271.3004 and an alert threshold of approximately 406.95, demonstrating both PASS and ALERT conditions.

### Task 7 – Responsible and Sustainable AI

The project evaluates:

- Geographic and historical data limitations.

- Proxy-label validity and fairness concerns.

- Uneven prediction errors across operating conditions.

- Human oversight and model governance.

- Monitoring, investigation, and rollback requirements.

- Computational sustainability and resource efficiency.

The detailed findings are documented in the accompanying Responsible AI report.

## 7. Technologies Used

| Category | Technologies |
|---|---|
| Programming | Python |
| Data processing | NumPy, Pandas |
| Data analysis | SQL, descriptive statistics |
| Visualisation | Matplotlib, Power BI |
| Machine learning | Scikit-learn |
| Deep learning | TensorFlow, Keras |
| Explainability | SHAP |
| Experiment tracking | MLflow, SQLite |
| Deployment simulation | FastAPI |
| Model artifacts | MLflow, Git LFS |
| Version control | Git, GitHub |
| Development environment | Jupyter Notebook |

## 8. How to Run

1. Clone the repository using git clone https://github.com/tetsu0119/smart-city-traffic-capstone.git.

2. Ensure Git LFS is installed and run git lfs pull from the repository root to retrieve large model artifacts.

3. Install Python and the dependencies required for the relevant project part. Consult the individual README files and MLflow model environment files for dependency information.

4. Open Power BI deliverables using Power BI Desktop.

5. To reproduce data preparation, run the Part 2 pipeline and feature engineering scripts as described in the Part 2 README.

6. Open and execute Part 3 Jupyter notebooks from the part3_machine_learning directory so that relative data and database paths resolve correctly.

7. Review the MLflow tracking database and model artifacts for experiment results.

8. Follow the Part 3 README for the local FastAPI deployment simulation and monitoring demonstrations.

Some notebook steps may require additional environment-specific configuration.

## 9. MLflow Portability Note

The MLflow tracking database (part3_machine_learning/mlflow_tracking.db) contains artifact URIs referencing the original local Windows development directory.

Although the notebooks can locate the tracking database using relative paths, stored artifact URIs may not resolve automatically when the repository is cloned to another computer.

The original experiment records and model artifacts are preserved for reproducibility and audit purposes.

To reproduce the deployment workflow in another environment, users may need to configure MLflow tracking and artifact paths or rerun the relevant training and logging steps to generate environment-specific artifacts.

The deployment simulation was tested successfully in the original development environment but is not presented as a continuously operating production service.

## 10. Reports and Documentation

The repository includes reports and notebooks documenting methodology, implementation, evaluation results, limitations, and findings.

Key Part 3 reports are:

`part3_machine_learning/final_capstone_report.pdf`

`part3_machine_learning/responsible_ai_report.docx`

Each part contributes to the complete Smart City Traffic Intelligence capstone portfolio.

## 11. Responsible Use and Future Improvements

The project is intended for educational and analytical purposes.

Future improvements could include more recent traffic observations, additional road corridors, real accident records, chronological model validation, real-time data integration, and production-grade model governance.

Any real-world use should be subject to appropriate human oversight, operational validation, and monitoring.

## 12. Author

**Tetsuya Tanaka**

NUS School of Computing

AI, Machine Learning and Data Science Capstone Project
