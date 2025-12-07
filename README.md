# airflow-dbt-postgres-data-pipeline
Using Airflow for data pipeline &amp; dbt for data transformation on postgresql
# *Project Overview*
Models a modern ETL (Extract, Transform, Load) data pipeline architecture, providing a clear blueprint for moving raw data from files into a production-ready data warehouse.

# *Problem To Be Solved*
The project solves the problem of unreliable, manually managed, and untransformed data ingestion. Without this pipeline, an organization faces the following common challenges:
1. Manual Data Movement: Relying on manual scripts or commands to load data, which is prone to human error and difficult to scale or schedule.
2. Lack of Transformation Logic: Raw source data (like individual customer, order, and order-item files) is not structured or aggregated into readily usable business entities, forcing analysts to manually clean and join data for every report.
3. Absence of Data Quality: Without a framework like dbt, there is no standardized way to version control, test, or document data transformations, leading to inconsistencies and distrust in the final reports.

# *Business Impact*
The direct impact of implementing this architecture is the creation of a single source of truth for core business metrics.
*  Trusted Data: The use of dbt for defining transformations and running data quality tests (as inferred by dbt_project.yml) ensures that all data models are reliable and accurate.
*  Faster Decision-Making: Analysts and business users can query highly structured and pre-calculated tables (e.g., a "fact_orders" or "dim_customer" table) instead of spending time on data preparation.
*  Reduced Operational Overhead: Automating the entire process with Airflow reduces the maintenance burden and frees up engineering time from manual data tasks.

# *Business Leverage*
The combination of these specific tools offers significant leverage by introducing software engineering best practices to data warehousing.
*  Modularity and Reusability (dbt): Transformations are written as modular SQL models, allowing new analysis to leverage existing base models, reducing redundant code and ensuring consistency across departments.
*  Scalability (Airflow): Airflow can effortlessly manage increasing data volumes and pipeline complexity by adding new DAGs (Directed Acyclic Graphs) and parallelizing tasks without redesigning the core infrastructure.
*  Documentation: dbt provides automatic documentation generation, ensuring that all metrics and transformations are clearly defined and understood by everyone in the organization.
# *Project Flow*
1. Create database on PostgreSQL using SQL
   ```sql
   CREATE DATABASE customers_db;
   ```
2. Create docker-compose.yml with dbt project
   ```lvim
   volumes:
     ...
     # Existing: Mount local dbt project (includes dbt_project.yml and profiles.yml)
      - /home/mulyo/dbt_snowflake/customers/:/usr/local/airflow/dbt_project:rw
     ...
   ```
3. Install into dedicated VENV path through Dockerfile
   ```bash
    # The dbt executable will now be at /opt/dbt_venv/bin/dbt
     RUN python -m venv /opt/dbt_venv && \
     /opt/dbt_venv/bin/pip install --no-cache-dir \
     dbt-postgres
   ```  

# *Assumption*
1. PostgreSQL database (exp: customers_db) for database/data warehouse, I use postgreSQL under docker container.
2. Airflow running using docker container, build & run using docker-compose.yml
3. DBT (Data Build Tool) on docker, build with Dockerfile with setup to communicate from Airflow
