build_web:
	docker build \
		--build-arg COMMIT_ID=$(GIT_COMMIT_ID) \
		--target test \
		-t idis/web-test:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t idis/web-test:latest \
		-f dockerfiles/web/Dockerfile \
		.

build_http:
	docker build \
		-t idis/http:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t idis/http:latest \
		dockerfiles/http

build: build_web build_http

push_web:
	docker push idis/web:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME)
	docker push idis/web:latest

push_http:
	docker push idis/http:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME)
	docker push idis/http:latest

push: push_web push_http

migrations:
	docker-compose run -u $(USER_ID) --rm web python manage.py makemigrations

.PHONY: docs
docs:
	docker-compose run --rm -v `pwd`/docs:/docs -u $(USER_ID) web bash -c "cd /docs && make html"