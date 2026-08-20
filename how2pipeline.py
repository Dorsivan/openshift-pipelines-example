apiVersion: datasciencepipelinesapplications.opendatahub.io/v1
kind: DataSciencePipelinesApplication
metadata:
  name: dspa
  namespace: my-project
spec:
  apiServer:
    cABundle:
      configMapName: my-trusted-ca
      configMapKey: ca-bundle.crt

    
    
    from kfp import kubernetes


CA_CONFIGMAP = "pipeline-trusted-ca"
CA_MOUNT_DIR = "/etc/pki/pipeline-ca"
CA_FILE = f"{CA_MOUNT_DIR}/ca-bundle.crt"


def configure_ca(task):

    kubernetes.use_config_map_as_volume(
        task,
        config_map_name=CA_CONFIGMAP,
        mount_path=CA_MOUNT_DIR,
    )

    task.set_env_variable(
        name="PIP_CERT",
        value=CA_FILE,
    )

    task.set_env_variable(
        name="REQUESTS_CA_BUNDLE",
        value=CA_FILE,
    )

    task.set_env_variable(
        name="SSL_CERT_FILE",
        value=CA_FILE,
    )

    return task
    
    
    @dsl.component(
    base_image="python:3.11",
    packages_to_install=[
        "requests",
        "pyyaml",
    ],
)
def download_data():
    import requests

    response = requests.get(
        "https://something.internal.example"
    )

    print(response.status_code)


@dsl.component(
    base_image="python:3.11",
    packages_to_install=[
        "pandas",
    ],
)
def process_data():
    import pandas

    print("processing")
    
    
    
    @dsl.pipeline(name="my-pipeline")
def pipeline():

    download_task = download_data()
    configure_ca(download_task)

    process_task = process_data()
    configure_ca(process_task)