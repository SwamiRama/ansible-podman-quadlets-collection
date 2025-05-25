# Contributing to community.podman_quadlets

We love your input! We want to make contributing to this project as easy and transparent as possible.

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the CHANGELOG.rst with a note describing your changes.
3. The PR will be merged once you have the sign-off of at least one maintainer.

## Any contributions you make will be under the MIT Software License

When you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project.

## Report bugs using GitHub's [issue tracker](https://github.com/globalbots/ansible-podman-quadlets/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/globalbots/ansible-podman-quadlets/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Testing

Please add tests for any new functionality. We use:

- `ansible-test` for module testing
- `molecule` for role testing
- `pytest` for unit tests

### Running Tests Locally

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
make test

# Run specific test types
make test-sanity
make test-units
make test-integration
make test-molecule