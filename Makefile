.PHONY: setup
setup:
	docker build --tag django_material_demo .
	docker create -p 3000:8000 -it --name django_material_demo_container django_material_demo
	
.PHONY: start
start:
	docker start -ai django_material_demo_container

.PHONY: clean
clean:
	docker rm django_material_demo_container
