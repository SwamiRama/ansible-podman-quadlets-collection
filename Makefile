# Makefile for community.podman_quadlets collection

COLLECTION_NAME = community.podman_quadlets
COLLECTION_VERSION = $(shell grep version: galaxy.yml | cut -d ' ' -f 2)
NAMESPACE = $(shell grep namespace: galaxy.yml | cut -d ' ' -f 2)
NAME = $(shell grep name: galaxy.yml | cut -d ' ' -f 2)

# Python interpreter
PYTHON = python3
PIP = $(PYTHON) -m pip

# Ansible commands
ANSIBLE_GALAXY = ansible-galaxy
ANSIBLE_TEST = ansible-test
ANSIBLE_LINT = ansible-lint
ANSIBLE_PLAYBOOK = ansible-playbook

# Directories
BUILD_DIR = build
DIST_DIR = dist
DOCS_DIR = docs

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: all
all: test build ## Run all tests and build

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -rf *.tar.gz
	rm -rf .pytest_cache
	rm -rf .tox
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.PHONY: deps
deps: ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r tests/unit/requirements.txt
	$(ANSIBLE_GALAXY) collection install -r requirements.yml --force

.PHONY: format
format: ## Format Python code
	black plugins/
	isort plugins/

.PHONY: lint
lint: lint-yaml lint-ansible lint-python ## Run all linters

.PHONY: lint-yaml
lint-yaml: ## Lint YAML files
	yamllint .

.PHONY: lint-ansible
lint-ansible: ## Lint Ansible files
	$(ANSIBLE_LINT)

.PHONY: lint-python
lint-python: ## Lint Python files
	flake8 plugins/
	pylint plugins/ || true

.PHONY: test
test: test-sanity test-units test-integration ## Run all tests

.PHONY: test-sanity
test-sanity: ## Run sanity tests
	$(ANSIBLE_TEST) sanity --docker -v --color

.PHONY: test-units
test-units: ## Run unit tests
	$(ANSIBLE_TEST) units --docker -v --color --python 3.10

.PHONY: test-integration
test-integration: ## Run integration tests
	$(ANSIBLE_TEST) integration --docker -v --color

.PHONY: test-molecule
test-molecule: ## Run molecule tests
	molecule test

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	pytest tests/unit/ --cov=plugins --cov-report=html --cov-report=term

.PHONY: build
build: clean ## Build the collection artifact
	$(ANSIBLE_GALAXY) collection build --force

.PHONY: install
install: build ## Install the collection locally
	$(ANSIBLE_GALAXY) collection install $(NAMESPACE)-$(NAME)-$(COLLECTION_VERSION).tar.gz --force

.PHONY: publish
publish: build ## Publish to Ansible Galaxy
	$(ANSIBLE_GALAXY) collection publish $(NAMESPACE)-$(NAME)-$(COLLECTION_VERSION).tar.gz

.PHONY: docs
docs: ## Build documentation
	cd $(DOCS_DIR) && $(MAKE) html

.PHONY: docs-serve
docs-serve: docs ## Serve documentation locally
	cd $(DOCS_DIR)/build/html && $(PYTHON) -m http.server

.PHONY: version
version: ## Show collection version
	@echo "Collection: $(NAMESPACE).$(NAME)"
	@echo "Version: $(COLLECTION_VERSION)"

.PHONY: changelog
changelog: ## Generate changelog
	antsibull-changelog generate

.PHONY: release
release: clean test build ## Create a new release
	@echo "Creating release $(COLLECTION_VERSION)"
	@echo "Don't forget to:"
	@echo "  1. Update CHANGELOG.rst"
	@echo "  2. Tag the release: git tag v$(COLLECTION_VERSION)"
	@echo "  3. Push tags: git push --tags"
	@echo "  4. Run: make publish"

.PHONY: dev-setup
dev-setup: deps ## Setup development environment
	pre-commit install
	@echo "Development environment ready!"

.PHONY: check
check: lint test ## Run all checks (lint + test)

.PHONY: validate
validate: ## Validate collection metadata
	$(ANSIBLE_GALAXY) collection validate .

.PHONY: watch
watch: ## Watch for changes and run tests
	watchmedo auto-restart --patterns="*.py;*.yml;*.yaml" --recursive -- make test-units