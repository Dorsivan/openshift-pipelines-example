# OpenShift AI Pipelines Example

An example ML pipeline for **Red Hat OpenShift AI** (RHOAI 3.4+). It trains a
scikit-learn RandomForest classifier on the Iris dataset, evaluates it, and
conditionally exports the model when accuracy meets a configurable threshold.

## Pipeline overview

```
load_and_preprocess_data
         |
     train_model
         |
    evaluate_model
         |
   [accuracy >= 0.90?]
         |
    export_model
```

| Step | What it does |
|------|-------------|
| **load_and_preprocess_data** | Loads Iris, splits train/test, applies StandardScaler |
| **train_model** | Fits a RandomForestClassifier |
| **evaluate_model** | Computes accuracy, F1, classification report |
| **export_model** | Copies the model artifact if accuracy >= threshold (conditional) |

## Pipeline parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `test_size` | `0.2` | Fraction of data held out for testing |
| `n_estimators` | `100` | Number of trees in the RandomForest |
| `max_depth` | `5` | Maximum tree depth |
| `accuracy_threshold` | `0.90` | Minimum accuracy to trigger model export |

## Files

| File | Description |
|------|-------------|
| `pipeline.py` | KFP v2 Python pipeline source |
| `iris_training_pipeline.yaml` | Compiled pipeline YAML (ready to upload) |
| `requirements.txt` | Python dependencies for local compilation |

## Quick start: upload to OpenShift AI

You can use the **pre-compiled YAML** (`iris_training_pipeline.yaml`) directly
without installing anything locally.

### 1. Create a project (if you don't have one)

1. Log in to the **OpenShift AI dashboard**.
2. Click **Projects** in the left sidebar.
3. Click **Create project**, give it a name (e.g. `iris-pipeline-demo`), and
   click **Create**.

### 2. Configure a pipeline server

Before importing pipelines you need a pipeline server in your project:

1. Open your project and go to the **Pipelines** tab.
2. Click **Configure pipeline server**.
3. Provide an S3-compatible object storage connection (e.g. MinIO or AWS S3)
   for pipeline artifact storage:
   - **Access key**, **Secret key**, **Endpoint**, **Bucket name**
4. Click **Configure**.
5. Wait until the pipeline server status shows **Available**.

### 3. Import the pipeline

1. In your project, go to the **Pipelines** tab.
2. Click **Import pipeline**.
3. Enter a name (e.g. `Iris Classifier Training`).
4. Choose **Upload a file** and select `iris_training_pipeline.yaml`.
5. Click **Import**.

### 4. Create a run

1. On the **Pipelines** tab, find your imported pipeline.
2. Click the **action menu** (three dots) and select **Create run**.
3. Adjust pipeline parameters if desired (or keep defaults).
4. Click **Create** to start the run.

### 5. Monitor the run

1. Go to the **Runs** tab in your project.
2. Click on your run to see the pipeline graph and step status.
3. Click individual steps to view logs and output artifacts.

## Recompile from source (optional)

If you modify `pipeline.py`, recompile the YAML:

```bash
pip install -r requirements.txt
python pipeline.py
# -> produces iris_training_pipeline.yaml
```

> **Note:** Requires Python 3.9-3.12 (kfp 2.x does not yet support Python 3.13+).
> If using Fedora 43+ with Python 3.14, compile in a container:
> ```bash
> podman run --rm -v "$(pwd):/work:Z" -w /work python:3.11-slim \
>   bash -c "pip install -q kfp==2.12.1 && python pipeline.py"
> ```

## Base images

All pipeline steps use `registry.redhat.io/ubi9/python-311:latest` (Red Hat
Universal Base Image). If your cluster cannot pull from `registry.redhat.io`,
swap the `base_image` in `pipeline.py` to a mirror or to
`quay.io/modh/runtime-images:runtime-python-3.11-ubi9`.
