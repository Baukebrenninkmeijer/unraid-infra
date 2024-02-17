# Prerequisites for KinD

1. Install kubectl using `brew install kubectl`.
2. Install KinD using `brew install kind`
3. Start docker daemon
4. Create KinD cluster with `kind create cluster`
5.


## Kubernetes

- kubelet: small application running on a node that manages work
- pod: container env on a node, that runs one or many containers. When using KinD, each node is a container and kubernetes runs it's own pods within these docker containers.

Check status:

- Create cluster: `kind create cluster --config "kind-cluster.yaml"`
- Create namespace: `kubectl create namespace airflow`
- Create secrets and storage: `kubectl create -f .\kube\secrets.yaml -f .\kubernetes-persistent-volumes.yaml`
- Status of cluster: `kubectl cluster-info --context kind-airflow-assessment-cluster`
- Install airflow: `helm upgrade --install airflow-cluster airflow-stable/airflow --namespace airflow --create-namespace --values kube/airflow-values.yaml`
- Setup cdm api: `kubectl apply -f kubernetes-datasource.yaml`
- Install nginx as ingress controller: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml`
- Delete ingress namespace and recreate: `kubectl delete namespace ingress-nginx ; kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml`

Install postgresql with helm: `helm upgrade --install postgresql-db oci://registry-1.docker.io/bitnamicharts/postgresql --namespace airflow -f kube/postgres-values.yaml`
Install ingress for postgres:  `kubectl create -f kube/ingress-postgres.yaml`

Port forwarding for airflow:

- `kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow`
- `kubectl port-forward svc/swagger-ui-external 8081:8081 --namespace cdm`

Testing of api:
` curl.exe http://127.0.0.1/cdm-api/companies -k -v`


URL to connect with pods in different namespace: 
`curl -X get cdm-api.cdm.svc.cluster.local/companies`

Waiting for something to finish in kubernetes:
```
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```


# Deletion

- deletion of helm object doesn't remove pods: `helm delete airflow --namespace airflow`

# Clear memory
`wsl --shutdown`


## Notes

1. Lijst met wat je nog zou doen, ivm met tijd tekort.
2. Voor python: gebruik linter/formatter.
3. Schrijf een paar unit/integration tests. Beschrijf hoe je dit verder zou toepassen als er meer tijd was. 
4. Componenten hun samenspel testen of hele end-to-end flow. 
5. Discuss secret management: 
   1. Add secret store or env variables.
6. Voeg een makkelijke database toe voor querying en storage
7. Presenteer resultaten in een simpele web UI (Streamlit/flask)
8. Schrijf readme