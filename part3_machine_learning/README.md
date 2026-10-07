# Smart City Traffic Intelligence — Part 3: Machine Learning and AI

**Author:** Tetsuya Tanaka

## Overview

Part 3 extends the analytics and Python feature-engineering work from Parts 1 and 2 into a historical traffic-intelligence prototype. It covers supervised learning, clustering and association rules, deep learning and explainability, MLflow experiment tracking, travel-time recommendations, a local FastAPI deployment simulation, and responsible AI.

**Scope:** The Metro Interstate Traffic Volume dataset contains 48,187 processed hourly observations from a single westbound I-94 corridor near Minneapolis–St. Paul, covering October 2012 to September 2018. The engineered dataset contains 30 columns; the deployed traffic-volume regressor uses 25 numerical predictors.

> **Important — accident-data disclosure:** No real accident dataset was used in this project. Accident risk was represented using a documented proxy based on congestion derived from traffic volume together with severe or low-visibility weather conditions. This proxy is **not** an observed accident outcome or a validated accident probability. Travel recommendations identify historically lower-traffic times, **not** safer routes.

## Tasks and results

| Task | Component | Main output |
| --- | --- | --- |
| 1 | Supervised learning | Logistic Regression and Random Forest classification of the accident-risk **proxy**; Linear Regression and Random Forest traffic-volume regression |
| 2 | Unsupervised learning | K-means traffic-condition clustering (K=6, silhouette score 0.5254) and Apriori association rules |
| 3 | Deep learning and explainability | Keras neural-network traffic-volume prediction and SHAP explanations of a comparable Random Forest model |
| 4 | Advanced AI technique | MLflow experiment tracking, model comparison and run history |
| 5 | Traffic recommendation system | Historical travel-time recommendations by day type, hour and weather, with minimum-sample safeguards and fallback |
| 6 | MLOps and deployment simulation | Reconstructed Random Forest model logged to MLflow; local FastAPI `/predict` function; MAE monitoring and PASS/ALERT examples |
| 7 | Responsible and sustainable AI | Data coverage, proxy-label bias, uneven errors, oversight, governance and compute-resource trade-offs |

### Selected performance results

| Experiment | MAE | R² |
| --- | ---: | ---: |
| Linear Regression baseline (Task 4 MLflow) | 813.7666 | 0.7259 |
| Random Forest Regressor (Task 4 MLflow, v2) | 271.3004 | 0.9442 |
| Neural Network (Task 3 saved execution) | 297.8235 | 0.9395 |
| Reconstructed Random Forest deployment candidate (Task 6) | 270.0103 | 0.9448 |

The original Task 4 completed Random Forest run did not expose a deployable model artifact. Task 6 reconstructed a candidate using the recorded settings, stored it in a **separate** MLflow run, and verified that the stored model could be reloaded. The reconstruction is not claimed to be a binary-identical copy.

## Repository contents

This README describes the **current working layout**. The Part 3 deliverable may also be packaged as a separate `capstone_part3` folder, provided its input paths and MLflow artifact locations are updated and tested.

```text
smart-city-traffic-capstone/
├── part2_python/
│   └── engineered_traffic_data.csv     # generated in Part 2; required input
└── part3_machine_learning/
    ├── README.md
    ├── task1_supervised_ml.ipynb
    ├── task2_unsupervised_ml.ipynb.ipynb
    ├── task3_deep_learning_explainability.ipynb
    ├── task4_mlflow_experiment_tracking.ipynb
    ├── task5_traffic_recommendation_system.ipynb
    ├── task6_mlops_deployment_simulation.ipynb
    ├── task7_responsible_sustainable_ai.ipynb
    ├── mlflow_tracking.db
    ├── mlruns/                           # MLflow artifact store
    ├── deployment_features.txt
    ├── figures/
    ├── *.log                             # task and monitoring logs
    ├── final_capstone_report.docx
    └── responsible_ai_report.docx
```

The listing documents the expected files based on the working folder. **Check actual filenames before running:** Task 2 currently has a doubled `.ipynb` extension. Do not rename or relocate notebooks without checking relative paths and re-running affected cells. `mlruns/` and the SQLite database must be preserved together with any referenced model artifacts.

## Environment and installation

- Python 3 with Jupyter Notebook or JupyterLab
- Core packages used across the notebooks include `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `mlxtend`, `tensorflow`/`keras`, `shap`, `mlflow`, `fastapi`, and `pydantic`.
- Depending on the installed MLflow serialization backend, `skops` may also be required. `joblib` is useful for an alternative trusted local artifact workflow.

Install the packages in a dedicated environment, for example:

```bash
python -m pip install jupyter pandas numpy scikit-learn matplotlib seaborn mlxtend tensorflow shap mlflow fastapi pydantic skops joblib
```

These are project dependencies, **not a pinned, tested lockfile**. Package/API compatibility may vary; record the actual working versions for reproducible reruns. Do not load untrusted model artifacts.

## How to run

1. Open a terminal in `smart-city-traffic-capstone/part3_machine_learning/` and start Jupyter (`jupyter lab` or `jupyter notebook`).
2. Ensure `../part2_python/engineered_traffic_data.csv` exists. If not, run the Part 2 pipeline/feature-engineering workflow first.
3. Open Tasks 1–3 for supervised, unsupervised and deep-learning analyses; run cells in notebook order.
4. Open Task 4 to inspect or recreate MLflow experiments. Its SQLite tracking database is `mlflow_tracking.db` in the Part 3 working folder.
5. Open Task 5 and run its cells to generate historical travel-time recommendations. Plain-language recommendations are printed for end users; internal progress uses Python logging.
6. Open Task 6 after Task 4's MLflow history is available. It loads experiment metadata, reconstructs and logs a deployment candidate when necessary, reloads the saved model, defines the FastAPI `/predict` route, and runs a **local notebook demonstration** plus monitoring and alerting scenarios.
7. Task 7 is a Markdown-based Responsible AI assessment; read it together with `responsible_ai_report.docx` and `final_capstone_report.docx`.

**Execution cautions:** Running Task 6's model-logging cell again creates another MLflow run and may take time or substantial memory. Existing completed deployment runs can be reused if the notebook is adjusted accordingly. Moving notebooks into a `notebooks/` subfolder changes relative paths; update those paths and test again before submission. The Task 6 FastAPI function was exercised locally; a persistent network server is **not** part of the demonstrated deployment.

## Deployment and monitoring illustration

- The local FastAPI application defines `POST /predict`, accepting a `features` dictionary with the 25 numeric predictors in the training feature schema.
- Example held-out observation: predicted traffic volume **4,659.6**, observed **4,924.0**.
- Task 6 monitoring baseline: Task 4 Random Forest MAE **271.3004**.
- Demonstration alert threshold: **1.5 × baseline MAE ≈ 406.95**.
- Simulated MAE **320.0** → **PASS / Normal**; MAE **450.0** → **ALERT / Requires investigation**.

These are simulations, not live production monitoring or calibrated operational thresholds.

## Logging and responsible use

Internal status and progress are recorded using Python's `logging` module. User-facing CLI-style recommendation text may use `print()`. The project does not support real-time navigation, city-wide generalization or validated accident prediction. Rare weather and unusual time periods may be underrepresented, and random train/test splitting may overestimate performance on future periods. Operational use would require recent data, time-based and subgroup evaluation, human approval, model monitoring and a rollback process.

## Reports and submission

- `final_capstone_report.docx`: methodology, findings and integration across **Part 3 Tasks 1–7**.
- `responsible_ai_report.docx`: separate bias, fairness, governance and sustainability report.
- The **Part 3 deliverable** is distinct from the **Final Capstone Submission**, which combines the outputs of Parts 1, 2 and 3 in one portfolio/repository.

Before submission, verify that notebooks, logs, the MLflow database **and its artifacts**, model/deployment files, recommendation engine, both reports and this README are included and that paths work in the submitted layout.

MLflow Portability Note

The MLflow tracking database (mlflow_tracking.db) contains artifact URIs referencing the original local Windows project directory.

Although the notebooks locate the tracking database using relative paths, the artifact locations stored within the database may not resolve automatically when the repository is cloned to another computer.

The original MLflow experiment records and model artifacts are preserved for reproducibility and audit purposes.

To reproduce the workflow in another environment, users should configure the local MLflow tracking URI and update the artifact references as appropriate, or rerun the relevant model training and logging steps to create new environment-specific artifacts.

The deployment simulation was successfully tested in the original development environment. However, model loading from the stored MLflow runs may require additional configuration on another computer.
