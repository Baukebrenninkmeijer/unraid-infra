    # Step 1: Create kind cluster
	kind get clusters | grep -q "airflow-assessment-cluster" || kind create cluster --config kube/kind-cluster.yaml

	# Step 2: Create namespace
	kubectl create namespace airflow --dry-run=client -o yaml | kubectl apply -f -

	# Step 3: Create secret
	kubectl delete -f ./kube/secrets.yaml -f ./kube/kubernetes-persistent-volumes.yaml  --ignore-not-found=true
	kubectl create -f ./kube/secrets.yaml -f ./kube/kubernetes-persistent-volumes.yaml

	# Step 4: Setup airflow
	helm upgrade --install airflow-cluster airflow-stable/airflow --namespace airflow --create-namespace --values kube/airflow-values.yaml

	# Step 4: Setup cdm api
	kubectl delete -f kube/kubernetes-datasource.yaml --ignore-not-found=true
	kubectl apply -f kube/kubernetes-datasource.yaml

	# Step 5: Setup ingress controller
	kubectl delete -f  https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml --ignore-not-found=true
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

	# Step 6: Setup postgres db
	helm upgrade --install postgresql-db oci://registry-1.docker.io/bitnamicharts/postgresql --namespace airflow -f kube/postgres-values.yaml
	kubectl delete -f kube/ingress-postgres.yaml --ignore-not-found=true
	kubectl create -f kube/ingress-postgres.yaml