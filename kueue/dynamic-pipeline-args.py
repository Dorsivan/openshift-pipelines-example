from typing import List, Dict

from kfp import dsl, compiler, kubernetes


# ============================================================
# Requirement 1:
# Receive arbitrary YAML contents
# ============================================================

@dsl.component(
    base_image="python:3.11",
    packages_to_install=[
        "pyyaml==6.0.2",
    ],
)
def consume_yaml(config_yaml: str):
    import yaml

    config = yaml.safe_load(config_yaml)

    print("Received configuration:")
    print(config)


# ============================================================
# Requirement 2 + 3:
# Run a CLI with arbitrary arguments.
#
# NOTE:
# We give this a default image only so that the component
# definition is valid.
#
# The pipeline will override the image at runtime.
# ============================================================

@dsl.component(
    base_image="python:3.11",
)
def run_cli(cli_args: List[str]):
    import subprocess

    command = [
        "my-cli",
        *cli_args,
    ]

    print("Executing:")
    print(command)

    subprocess.run(
        command,
        check=True,
    )


# ============================================================
# Pipeline
# ============================================================

@dsl.pipeline(
    name="dynamic-runtime-pipeline",
)
def pipeline(
    # Completely independent requirement:
    config_yaml: str,

    # Image used by run_cli
    image_name: str,

    # Arbitrary CLI arguments
    cli_args: List[str],

    # Completely independent PVC requirement
    pvc_specs: List[Dict[str, str]],
):

    # --------------------------------------------------------
    # YAML requirement
    # --------------------------------------------------------

    yaml_task = consume_yaml(
        config_yaml=config_yaml,
    )

    # --------------------------------------------------------
    # Dynamic image + dynamic CLI args
    # --------------------------------------------------------

    cli_task = run_cli(
        cli_args=cli_args,
    )

    # THIS is what makes the image runtime-configurable.
    cli_task.set_container_image(image_name)

    # --------------------------------------------------------
    # Dynamic PVC requirement
    # --------------------------------------------------------

    with dsl.ParallelFor(
        items=pvc_specs,
    ) as pvc:

        create_pvc = kubernetes.CreatePVC(
            pvc_name_suffix=pvc.suffix,
            access_modes=["ReadWriteOnce"],
            size=pvc.size,
            storage_class_name=pvc.storage_class,
        )


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="pipeline.yaml",
    )
    
    
kfp run create \
    --experiment-name my-experiment \
    --package-file pipeline.yaml \
    image_name=quay.io/my-company/trainer:v3 \
    config_yaml="$(cat config.yaml)" \
    cli_args='["train","--epochs","20","--batch-size","64"]' \
    pvc_specs='[
      {
        "suffix":"-data",
        "size":"20Gi",
        "storage_class":"ocs-storagecluster-ceph-rbd"
      },
      {
        "suffix":"-models",
        "size":"100Gi",
        "storage_class":"ocs-storagecluster-ceph-rbd"
      }
    ]'
    
