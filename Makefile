.PHONY: infra

infra:
	bash ./kube/setup.sh

delete:
	bash ./bin/teardown.sh

delete-cluster:
	kind delete cluster --name airflow-assessment-cluster