.PHONY: infra

infra:
	kube/setup.sh

delete:
	helm uninstall airflow-cluster -n airflow --ignore-not-found
	kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml --ignore-not-found=true
	kubectl delete -f kube/kubernetes-datasource.yaml --ignore-not-found=true
	kubectl delete -f ./kube/secrets.yaml -f ./kube/kubernetes-persistent-volumes.yaml --ignore-not-found=true
	kubectl delete all --all -n airflow --ignore-not-found=true
	kubectl delete namespace airflow --ignore-not-found=true


delete-cluster:
	kind delete cluster --name airflow-assessment-cluster