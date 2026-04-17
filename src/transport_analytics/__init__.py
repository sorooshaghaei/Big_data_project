#Mehdi AGHAEI

from importlib import import_module

__all__ = [
    "PostgresConfig",
    "ProjectPaths",
    "PipelineArtifacts",
    "add_time_features",
    "build_daily_fact_table",
    "build_station_fact_table",
    "enrich_daily_with_context",
    "infer_city",
    "load_postgres_artifacts",
    "run_local_pipeline",
    "run_stage_workflow",
    "stage_one_plan",
]

_EXPORTS = {
    "PostgresConfig": ".config",
    "infer_city": ".context",
    "add_time_features": ".features",
    "run_stage_workflow": ".methods",
    "stage_one_plan": ".methods",
    "load_postgres_artifacts": ".postgres",
    "PipelineArtifacts": ".pipeline",
}


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
