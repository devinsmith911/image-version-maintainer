# image-version-maintainer
Verifies/detects and checks Docker image versions in Compose files

How does this work?

- Detects all `image:` declarations in docker-compose file specified
- Splits the detection and determines repo, image and version of image
- NOTE: Currently only supports images tagged with semver versions. 
  - Will remove v in the beginning of the version if it exists (example repo: library/traefik)
- Queries specified registry for the list of tags in the repo (dockerhub by default)
- Compares the version declared in file to the list of tags and returns if there are new versions
- Can exit 1 if hard version control is defined (--major, --minor or --patch flags) - Primarily for use in CI pipelines

TO DO:
- Split into better classes 
- Handle semver version detection better
- Figure out how to support other versioning styles - some sort of config map?

```
usage: parse_version.py [-h] --compose-file COMPOSE_FILE
                        [--registry-username REGISTRY_USERNAME]
                        [--registry-password REGISTRY_PASSWORD]
                        [--registry-auth-domain REGISTRY_AUTH_DOMAIN]
                        [--registry-auth-service REGISTRY_AUTH_SERVICE]
                        [--registry-api-domain REGISTRY_API_DOMAIN]
                        [--log-level LOG_LEVEL] [--major] [--minor] [--patch]

optional arguments:
  -h, --help            show this help message and exit
  --compose-file COMPOSE_FILE
                        Compose file to process
  --registry-username REGISTRY_USERNAME
                        Set user for registry to authenticate against
  --registry-password REGISTRY_PASSWORD
                        Set password for registry to authenticate against
  --registry-auth-domain REGISTRY_AUTH_DOMAIN
                        Set the auth domain for registry
  --registry-auth-service REGISTRY_AUTH_SERVICE
                        Set auth service for registry
  --registry-api-domain REGISTRY_API_DOMAIN
                        Set auth domain for registry api
  --log-level LOG_LEVEL
                        Logging level
  --major               Exit 1 if there is new major version available
  --minor               Exit 1 if there is new minor version available
  --patch               Exit 1 if there is new patch version available
```