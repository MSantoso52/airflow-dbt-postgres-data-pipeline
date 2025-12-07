# Note: Using python3.11 as it's the standard for Airflow 3.1.3
FROM apache/airflow:3.1.3-python3.11

# 1. Install System Dependencies (Must run as root for permissions)
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Install dbt into a dedicated VENV path
# The dbt executable will now be at /opt/dbt_venv/bin/dbt
RUN python -m venv /opt/dbt_venv && \
    /opt/dbt_venv/bin/pip install --no-cache-dir \
    dbt-postgres

# 3. Switch back to the Airflow user (standard best practice)
USER airflow

# *** NOTE: The dbt project files (models, profiles.yml) are mounted 
#           at runtime by docker-compose.yaml, so no COPY is needed. ***
