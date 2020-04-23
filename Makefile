USER_ID = $(shell id -u)

build_web:
	docker build \
		--build-arg COMMIT_ID=$(GIT_COMMIT_ID) \
		--target test \
		-t idis/web-test:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t idis/web-test:latest \
		-f dockerfiles/web/Dockerfile \
		.
	docker build \
		--build-arg COMMIT_ID=$(GIT_COMMIT_ID) \
		--target dist \
		-t idis/web:$(GIT_COMMIT_ID)-$(GIT_BRANCH_NAME) \
		-t idis/web:latest \
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

vars_git_commit_id := $(shell git describe --always --dirty)
vars_git_branch_name := $(shell git rev-parse --abbrev-ref HEAD | sed "s/[^[:alnum:]]//g")
vars_git_docker_images_file = idis_docker_images$(vars_git_commit_id)$(vars_git_branch_name).tgz

clean_vars:
	-rm vars/anonserver_make_vars.yml
	-rmdir vars

refresh_vars: clean_vars vars/anonserver_make_vars.yml

vars_dir:
	mkdir vars

vars: clean_vars vars/anonserver_make_vars.yml

vars/anonserver_make_vars.yml: vars_dir

	@echo "git_commit_id: \"$(vars_git_commit_id)\"" > $@
	@echo "git_branch_name: \"$(vars_git_branch_name)\"" >> $@
	@echo "vars_git_docker_images_file: \"$(vars_git_docker_images_file)\"" >> $@

docker_images_tgz: vars
	mkdir -p release/docker_images
	docker save idis/web:latest idis/http:latest redis:4.0 mher/flower postgres:10.7 | gzip -c > release/docker_images/$(vars_git_docker_images_file)