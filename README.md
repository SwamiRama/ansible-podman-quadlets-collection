# Ansible Collection - community.podman_quadlets

[![CI](https://github.com/globalbots/ansible-podman-quadlets/workflows/CI/badge.svg?branch=main)](https://github.com/globalbots/ansible-podman-quadlets/actions)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-community.podman__quadlets-660198.svg)](https://galaxy.ansible.com/community/podman_quadlets)

This collection provides Ansible modules and roles for managing Podman containers using systemd Quadlets.

## What are Podman Quadlets?

Quadlets are a native systemd integration for Podman that allows you to define containers, networks, and volumes as systemd units. This provides better integration with the system, automatic startup, and dependency management.

## Requirements

- Ansible >= 2.14
- Podman >= 4.4
- Python >= 3.9
- systemd

## Installation

```bash
ansible-galaxy collection install community.podman_quadlets