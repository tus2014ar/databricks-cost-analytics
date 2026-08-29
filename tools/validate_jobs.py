"""
validate_jobs.py — schema check for Databricks Asset Bundle job YAML configs.

Catches a malformed job definition (missing task chain, missing parameters,
missing git_source) before it would fail at `databricks bundle deploy` time.
Run in CI on every push.
"""
import sys

import yaml

REQUIRED_JOB_KEYS = {"name", "tasks", "git_source", "parameters"}
REQUIRED_TASK_KEYS = {"task_key"}


def validate_job_file(path: str) -> list[str]:
    errors = []
    with open(path) as f:
        doc = yaml.safe_load(f)

    jobs = doc.get("resources", {}).get("jobs", {})
    if not jobs:
        return [f"{path}: no jobs found under resources.jobs"]

    for job_name, job in jobs.items():
        missing = REQUIRED_JOB_KEYS - job.keys()
        if missing:
            errors.append(f"{path}::{job_name}: missing top-level keys {missing}")

        tasks = job.get("tasks", [])
        if not tasks:
            errors.append(f"{path}::{job_name}: no tasks defined")

        task_keys_seen = set()
        for i, task in enumerate(tasks):
            missing_task = REQUIRED_TASK_KEYS - task.keys()
            if missing_task:
                errors.append(f"{path}::{job_name}: task[{i}] missing keys {missing_task}")
            key = task.get("task_key")
            if key in task_keys_seen:
                errors.append(f"{path}::{job_name}: duplicate task_key '{key}'")
            task_keys_seen.add(key)

        # every depends_on reference must point at a real task_key in this job
        for task in tasks:
            for dep in task.get("depends_on", []):
                dep_key = dep.get("task_key")
                if dep_key not in task_keys_seen:
                    errors.append(
                        f"{path}::{job_name}: task '{task.get('task_key')}' depends on "
                        f"unknown task_key '{dep_key}'"
                    )

    return errors


def main(paths: list[str]) -> int:
    all_errors = []
    for path in paths:
        all_errors.extend(validate_job_file(path))

    if all_errors:
        print(f"FAILED — {len(all_errors)} issue(s):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"Validated {len(paths)} job file(s). All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
