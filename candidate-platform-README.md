# CashFlow Datamaker - ING technical home-take assignment

Being one of the world's largest financial institutions, ING bank provides financial services to clients worldwide. 
Accounts and transactions are the core of these services, and therefore we continuously need to analyze them for
better understanding.

**As the technical home-take assignment, we kindly ask you to develop a _CashFlow Monitoring Application_.**
This application will help end-users to analyze the accounts to which the transactions are linked.

## Assignment

Your task is to create a platform that allows users to schedule the periodic monitoring of cash flows of different 
companies. The platform should have a periodic tasks that provides the following features:

* Display a list of all companies and the countries they interacted with.
* Present the balance (income - expenses) of the companies.

### Implementation

For the platform we **require** you to use the orchestrator tool [Apache Airflow](https://airflow.apache.org/) that is hosted on Kubernetes. You are free to decide how you are going to deploy Apache Airflow on Kubernetes (`yaml` files, `helm chart`, `terraform`, etc ).

For the Kubernetes setup we encourage you to use [Kubernetes in Docker (KinD)](https://kind.sigs.k8s.io/), since we think this the best solution for this assessment. You are free to use other infrastructure, but we always expect the infrastructure to be made using Infrastructure as Code.

Once you deployed Airflow on Kubernetes we ask you to create a DAG that interacts with the CDM to perform periodic monitoring of cash flows of companies. For this the DAG should interact with the CDM Rest API.

Finally, add an ingress to the Airflow webserver UI. See the [KinD ingress documentation](https://kind.sigs.k8s.io/docs/user/ingress/) on how to enable ingress on a KinD cluster.

Nice to have:
* How would you productionize the Airflow setup and the DAG. For instances if the data was 100 times as large. How would your Airflow settings and/or DAG setup change? (Implementation not required, but welcome)
* How would your platform look like when it should support multi-tenancy (i.e. multiple users)? (Implementation not required)

Please do not limit yourself to what we can come up with, we love being surprised by your awesome ideas!

## Evaluation

In order to evaluate your solution, we ask you to present your solution to two members of our team. Please provide 
the solution by uploading it through https://wetransfer.com/ the day before the interview, giving us enough time to
take a look and prepare. Please do not publish the assignment or your solution on public code repository services 
like Github.

## Requirements to perform this assessment
- Docker (Desktop)
- [Kubernetes in Docker](https://kind.sigs.k8s.io/)
- Kubectl CLI

## Final note

If you have any questions, remarks, or would like further clarification on the topic, please don't hesitate to contact us.

__Happy Hacking!__
