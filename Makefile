.PHONY: setup
setup:
	docker build --tag mysite-main .
	docker create -p 3000:8000 -it --name mysite-container mysite-main
	
.PHONY: start
start:
	docker start -ai mysite-container

.PHONY: clean
clean:
	docker rm mysite-container
