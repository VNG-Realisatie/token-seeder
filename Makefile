git_short_hash = `git rev-parse --short HEAD`
git_release = `git describe --tags --abbrev=0`
project_name = 'token-seeder'

create-image-tagged:
	echo "creating image"
	echo "docker build ${project_name}:$(git_short_hash)"
	docker build -t $(project_name):$(git_short_hash) .

create-image:
	echo "creating image"
	echo "docker build ${project_name}:$(git_release)"
	docker build -t $(project_name):$(git_release) . --no-cache

push-image: create-image
	echo "pushing image"
	docker push $(project_name):$(git_release)

push-image-tagged: create-image
	echo "pushing image"
	docker push $(project_name):$(git_short_hash)

run-image: create-image
	echo "running image"
	docker run --name $(project_name) -e TOKEN_ISSUER_SECRET=YOUR_SECRET -e TOKEN_ISSUER_IDENTIFIER=YOUR_IDENTIFIER -d $(project_name):$(git_release)

run-image-locally: create-image-tagged
	echo "running image"
	docker run --name $(project_name) -e TOKEN_ISSUER_SECRET=YOUR_SECRET -e TOKEN_ISSUER_IDENTIFIER=YOUR_IDENTIFIER -d $(project_name):$(git_short_hash)
