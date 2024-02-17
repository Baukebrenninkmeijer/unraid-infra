# ING Assessment - CashFlow Monitoring Application

By: Bauke Brenninkmeijer, 08-02-2024

## Introduction

This repository holds my assessment for the ING bank. The assignment was to create a platform that allows users to schedule the periodic monitoring of cash flows of different companies. The platform should have a periodic tasks that provides the following features:

- The countries the companies interacted with.
- The balance (income - expenses) of the companies.

While the way of delivery was unspecified, the current setup puts those results in a view on the output database. This is not the most effective way, but given the time allowed, the most efficient.

The current platform looks as follows:

- Airflow running on kubernetes, deployed with Helm.
- CDM API running, as was delivered in the assignment.
- Postgresql database running on kubernetes, deployed with Helm. This is a third database, next to the airflow one and CDM one, to keep clear segregation of data.

The setup is done with KinD, a kubernetes in docker solution. This is a lightweight way to run kubernetes on your local machine. 

The general solution looks as follows:

- One DAG that is currently run monthly, but can be changed to any frequency. This DAG interacts with the CDM API and stores the results in the database. It has separate tasks for each API endpoints, and stores the results in the database. The SEPA and SWIFT transactions or transformed into the same data model and stored in the `transactions` table. The companies are stored in the `companies` table and the rates are stored in the `rate` table. 
- One DAG that creates the views that are used to create the required output. This is currently not stored somewhere or visually represented, which would be next steps. The views that are created are `interacted_countries` and `account_balance`. The first one shows the countries the companies interacted with, and the second one shows the balance of the companies.

## Setup

To start with this project, please run the following commands:

```bash
make infra
```

This will create the required cluster in KinD and install the necessary components, and will host the airflow frontend on `localhost/airflow`. The swagger API is hosted on `localhost/cdm-api`. In a production setting, you likely don't want this to be exposed to the internet, but for this assessment it's fine and it made debugging a whole lot easier.


Teardown can be down with:

```bash
make delete
make delete-cluster
```

## Notes on the data

- id of the transactions are not unique.
- Whole transactions are duplicated.
- The columns of swift and sepa are different for sender/receiver.
- Currency can be empty for SWIFT transactions.

## Notes on the cdm source

- The swagger webpage didn't seem to work. When forwarding I got a XSS error, and the swagger json also had a duplicate key which threw an error. I extracted the swagger json and an external swagger UI, which worked fine.

## Next steps

This project is a first iteration of the platform. Time was limited but next steps I would have taken are: 

1. Create a more visual representation of the data, such as a dashboard or a report.
2. Segment the data into different stages, such as raw, cleaned, transformed and output. This would allow for easier debugging and more resilient processing.
3. Tie together all components with Terraform, which are currently in the make script. This will be a more structural approach to the infrastructure as code.
4. Add more tests, such as unit tests for the remaining untested components, for the DAG and integration tests for the API.
5. Move to a datalake architecture, where the data is stored in a more scalable and flexible way, such as parquet files on cloud storage. This would allow for more scalable and flexible querying.

## Extra questions

> * How would you productionize the Airflow setup and the DAG. For instances if the data was 100 times as large. How would your Airflow settings and/or DAG setup change? (Implementation not required, but welcome)
The current setup is not made for large amounts of data, and would need quite some changes to facilitate larger data sizes. For example, I currently ingest all rates and all companies everytime the dag is ran, which would not be feasible/efficient normally. Both storage and compute would be bottlenecks with much larger data. One: the database is curently a row-based database, and would need to be changed to a column-based database or a columnar data format stored on cloud storage, such as parquet or delta tables to facilitate large scale analytical queries. Two: the compute is not scalable currently, and relies on the specific kubernetes cluster that may or may not be flexible. While airflow can scale quite well with many tasks and dags, it's not a compute framework that allows for larger-than-memory data processing. While you can try to work around this with smart work distribution, I would recommend to use a different framework for this, such as spark, ray or dask. For the ingestion of the data, you can argue that reducing the query window would reduce the data size and that might still work for the ingestion. The analytical queries will be the bottleneck here, and would need to be changed to a more scalable solution.

> * How would your platform look like when it should support multi-tenancy (i.e. multiple users)? (Implementation not required)
It seems airflow has quite extensive support for multi-tenancy. The current setup is not multi-tenant, but it seems that it is possible to create a multi-tenant setup with airflow. This would require a different setup of the database, and a different setup of the airflow users. Using namespaces in kubernetes would be a good way to separate the different tenants and their resources on a more technical level.
