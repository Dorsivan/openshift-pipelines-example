from typing import List, Dict

from kfp import dsl, compiler, kubernetes


@dsl.component(
    base_image="python:3.12"
)
def read_config(config_yaml: str):
    import yaml

    config = yaml.safe_load(config_yaml)

    print("Received YAML:")
    print(config)


@dsl.component(
    base_image="python:3.12"
)
def use_storage(pvc_label: str):
    import os

    print(f"PVC description: {pvc_label}")

    with open("/data/test.txt", "w") as f:
        f.write(f"Hello from {pvc_label}\n")

    print(os.listdir("/data"))


@dsl.pipeline(name="runtime-config-and-dynamic-pvcs")
def pipeline(
    # Requirement 1:
    # Completely arbitrary YAML configuration.
    config_yaml: str,

    # Requirement 2:
    # Runtime description of PVCs to create.
    pvc_specs: List[Dict[str, str]],
):
    # ---------------------------------------------------------
    # Requirement 1: consume the YAML configuration
    # ---------------------------------------------------------

    config_task = read_config(
        config_yaml=config_yaml
    )

    # ---------------------------------------------------------
    # Requirement 2: dynamically create PVCs
    # ---------------------------------------------------------

    with dsl.ParallelFor(
        items=pvc_specs
    ) as pvc:

        create_pvc = kubernetes.CreatePVC(
            pvc_name_suffix=pvc.suffix,
            access_modes=["ReadWriteOnce"],
            size=pvc.size,
            storage_class_name=pvc.storage_class,
        )

        worker = use_storage(
            pvc_label=pvc.suffix
        )

        kubernetes.mount_pvc(
            worker,
            pvc_name=create_pvc.outputs["name"],
            mount_path="/data",
        )


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="pipeline.yaml",
    )
    
kfp run create \
    --experiment-name demo \
    --package-file pipeline.yaml \
    config_yaml="$(cat my-config.yaml)" \
    pvc_specs='[
      {
        "suffix": "-dataset",
        "size": "10Gi",
        "storage_class": "ocs-storagecluster-ceph-rbd"
      },
      {
        "suffix": "-models",
        "size": "50Gi",
        "storage_class": "ocs-storagecluster-ceph-rbd"
      },
      {
        "suffix": "-scratch",
        "size": "100Gi",
        "storage_class": "ocs-storagecluster-ceph-rbd"
      }
    ]'


