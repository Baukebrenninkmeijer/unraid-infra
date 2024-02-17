# Provided Resources

We included three `yaml` files for you:
- `kind-cluster.yaml`: This contains the Kubernetes in Docker (KinD) cluster definition. KinD allows to easily create a multi-node setup on your machine. For guidance on installing KinD, please see refer the [quick-start documentation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

The cluster mounts directories from your machine to the nodes of the kubernetes cluster using the `extraMounts` feature. Please refer to the [extraMount documentation section](https://kind.sigs.k8s.io/docs/user/configuration/#extra-mounts) for more information. For your convenience we provided three hostPath locations that will allow to easily sync dags, write logs and write output from Airflow. 

It is required that you change the `hostPath` to a physical location on your machine. In total, you need *three* locations for (1) dags, (2) logs and (3) output. These three locations should be the same for all nodes, for example do not use a different dag location for control-plane and worker nodes.

Afterwards you can create the cluster via 
``` bash
kind create cluster --config "kind-cluster.yaml"
```
NOTE: if you decide to not use KinD then you do not need this file

- `kubernetes-persistent-volumes.yaml`: This contains the logic to create persistent volumes in your KinD cluster based on the provided `extraMounts` the KinD cluster definition. You do not have to change the content of this file.

NOTE: if you decide to not use KinD then you do not need this file  

- `kubernetes-datasource.yaml`: This file provides the logic to create the datasource for the assessment. It contains three services:
  - `cdm-db`: Postgres database containing the data. The database **can not** be directly accessed (with username/password).
  - `cdm-api`: REST API endpoints to retrieve the data.
  - `swagger-ui`: an OpenAPI to see the details on each endpoint.

## Database (cdm-db)

We are providing 4 datasets:

1. **Company Info**: describes ING clients and the accounts they hold.
2. **SEPA Transactions**: transactions _within euro payment area only_ (transactions with `EUR` currency.)
These transactions _include only the accounts from `Company Info` dataset_.
3. **SWIFT Transactions**: _Global Transactions DataSet_ including transactions from multiple currencies and countries,
across the globe.
4. **Exchange Rates:** **1:1 mapping** between `SWIFT` and currencies seen therein. Only `SWIFT` data contains multiple
currencies. The currencies in this dataset follow `ISO Currency Codes,` a 3-letter-ISO code.

### Data schemas

For better understanding of the data and relations between, we are providing the entity relation diagram:
<br></br>
<img src=ER_diagram.png>

### Tables

#### Company Info

| Field           | Data Type | Description                                                           |
|-----------------|-----------|-----------------------------------------------------------------------|
| company_id      | Integer   | Unique identifier for the company                                     |
| ibans           | String    | List of International Banking Account Numbers (IBANs) for the company |
| name            | String    | Name of the company                                                   |
| address         | String    | Address of the company                                                |

#### SEPA

| Field     | Data Type | Description                                                                  |
|-----------|-----------|------------------------------------------------------------------------------|
| id        | Integer   | Unique identifier for the SEPA transaction                                   |
| payer     | String    | Payer's IBAN address                                                         |
| receiver  | String    | Receiver's IBAN address                                                      |
| amount    | Decimal   | Amount of the transaction                                                    |
| currency  | String    | Currency of the transaction (ISO Currency Code; always in EUR)               |
| ts        | Date      | ISO Timestamp with time zone indicating when the SEPA transaction took place |

#### SWIFT

| Field       | Data Type | Description                                                                        |
|-------------|-----------|------------------------------------------------------------------------------------|
| id          | Integer   | Unique identifier for the SWIFT transaction                                        |
| sender      | String    | Sender's IBAN address                                                              |
| beneficiary | String    | Beneficiary's IBAN address                                                         |
| amount      | Decimal   | Amount of the transaction                                                          |
| currency    | String    | Currency of the transaction (ISO Currency Code, e.g., EUR)                         |
| ts          | Date      | ISO Timestamp with time zone indicating when the SWIFT transaction took place      |

#### Exchange Rates

| Field    | Data Type | Description                                                     |
|----------|-----------|-----------------------------------------------------------------|
| currency | String    | Currency code (ISO Currency Code, e.g., EUR)                    |
| eur_rate | Decimal   | Exchange rate of the currency mapped to EUR                     |
| usd_rate | Decimal   | Exchange rate of the currency mapped to USD                     |

## Rest API (cdm-api)

We provide a sample REST API, that exposes 4 endpoints, one for each dataset:

- `/companies` provides ALL `Company Info` details.
- `/transactions/sepa` provides `SEPA` transactions for only the accounts in `Company Info`. This endpoint
returns data for a number of records (default=5000) at a time therefore it needs to be polled repeatedly.
- `/transactions/swift` provides `SWIFT` transactions for accounts _**globally**_. This endpoint returns data for
a number of records (default=5000) at a time therefore it needs to be polled repeatedly.
- `/exchange-rates` provides currencies' exchange rates for `SWIFT` transactions for accounts _**globally**_.

### Swagger (swagger-ui)

The details for each endpoint can be analysed with Swagger UI that runs on <http://127.0.0.1/>.

## Glossary

- IBAN - International Banking Account Number: For the scope of this assignment, candidate can assume that all valid
IBANs start with a 2-letter ISO-CountryCode. An account, or IBAN are synonymous.
- SEPA - Single Euro Payments Area: Consists transactions only in euros (for countries that are inside the Euro Payment
Zone), using `euro` as the default currency.
- SWIFT - Global Payment Messaging System which has transactions of `multiple currencies`, being executed globally.
- Exchange Rates: This table includes the information of currencies with their current exchange rates, mapped out to
either EUR or USD. The currencies in the table follow `ISO Currency Codes`, which is a 3-letter-ISO-Code.
