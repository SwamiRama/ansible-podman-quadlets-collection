# Ansible Collection - community.podman_quadlets

[![CI](https://github.com/globalbots/ansible-podman-quadlets/workflows/CI/badge.svg?branch=main)](https://github.com/globalbots/ansible-podman-quadlets/actions)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-community.podman__quadlets-660198.svg)](https://galaxy.ansible.com/community/podman_quadlets)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)

This collection provides Ansible modules and roles for managing Podman containers using systemd Quadlets.

## What are Podman Quadlets?

Quadlets are a native systemd integration for Podman that allows you to define containers, networks, and volumes as systemd units. This provides:

- **Better system integration**: Containers are managed as native systemd services
- **Automatic startup**: Containers start on boot without additional configuration
- **Dependency management**: Define dependencies between containers, networks, and volumes
- **Native logging**: Logs are available through journald
- **Resource management**: Use systemd's resource control features

## Requirements

- Ansible >= 2.14
- Podman >= 4.4
- Python >= 3.9
- systemd

## Installation

```bash
ansible-galaxy collection install community.podman_quadlets
```

Or include it in your `requirements.yml`:

```yaml
---
collections:
  - name: community.podman_quadlets
    version: ">=1.0.0"
```

## Quick Start

### Simple Container Example

```yaml
---
- name: Deploy nginx container with Quadlets
  hosts: localhost
  tasks:
    - name: Create nginx container
      community.podman_quadlets.podman_quadlet_container:
        name: nginx
        image: docker.io/nginx:latest
        state: present
        ports:
          - host_port: "8080"
            container_port: "80"
```

### Using the Role

```yaml
---
- name: Deploy application stack
  hosts: container_hosts
  vars:
    project_name: myapp
    containers:
      - name: webapp.container
        service_description: "My Web Application"
        container_image: "myapp:latest"
        container_name: "webapp"
        environment_variables:
          DATABASE_URL: "postgresql://db/myapp"
        ports:
          - host_port: "80"
            container_port: "8000"
        networks:
          - "internal.network"
        volumes:
          - host_path: "webapp-data.volume"
            container_path: "/data"
  roles:
    - community.podman_quadlets.podman_quadlets
```

## Modules

### podman_quadlet_container

Manage Podman containers using Quadlets.

```yaml
- name: Create container with full options
  community.podman_quadlets.podman_quadlet_container:
    name: myapp
    image: myapp:latest
    state: present
    environment:
      KEY: value
    volumes:
      - host_path: /data
        container_path: /app/data
    ports:
      - host_port: "8080"
        container_port: "80"
    networks:
      - internal
    labels:
      app: myapp
      env: prod
    auto_update: registry
    restart_policy: always
```

### podman_quadlet_network

Manage Podman networks using Quadlets.

```yaml
- name: Create network
  community.podman_quadlets.podman_quadlet_network:
    name: internal
    state: present
    subnet: 10.89.0.0/24
    gateway: 10.89.0.1
    internal: true
```

### podman_quadlet_volume

Manage Podman volumes using Quadlets.

```yaml
- name: Create volume
  community.podman_quadlets.podman_quadlet_volume:
    name: app-data
    state: present
    driver: local
    labels:
      app: myapp
```

### podman_quadlet_secret

Manage Podman secrets for use with containers.

```yaml
- name: Create secret
  community.podman_quadlets.podman_quadlet_secret:
    name: db-password
    data: "supersecret"
    state: present
```

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `podman_quadlets_base_dir` | `~/.config/containers/systemd` | Directory for quadlet files |
| `podman_quadlets_project_name` | **required** | Project name |
| `podman_quadlets_containers` | `[]` | List of containers to deploy |
| `podman_quadlets_service_state` | `started` | Desired service state |
| `podman_quadlets_service_enabled` | `true` | Enable services on boot |
| `podman_quadlets_auto_update` | `registry` | Auto-update policy |
| `podman_quadlets_create_volumes` | `true` | Auto-create volumes |
| `podman_quadlets_create_networks` | `true` | Auto-create networks |

## Examples

### WordPress with MariaDB

```yaml
---
- name: Deploy WordPress stack
  hosts: localhost
  vars:
    project_name: wordpress
    containers:
      - name: wordpress-db.container
        container_image: docker.io/mariadb:11
        container_name: wordpress-db
        environment_variables:
          MARIADB_ROOT_PASSWORD: "{{ vault_root_password }}"
          MARIADB_DATABASE: wordpress
          MARIADB_USER: wordpress
          MARIADB_PASSWORD: "{{ vault_db_password }}"
        volumes:
          - host_path: wordpress-db.volume
            container_path: /var/lib/mysql
        networks:
          - wordpress.network

      - name: wordpress.container
        container_image: docker.io/wordpress:latest
        container_name: wordpress
        required_services: wordpress-db.service
        after_services: wordpress-db.service
        environment_variables:
          WORDPRESS_DB_HOST: wordpress-db
          WORDPRESS_DB_USER: wordpress
          WORDPRESS_DB_PASSWORD: "{{ vault_db_password }}"
          WORDPRESS_DB_NAME: wordpress
        ports:
          - host_port: "8080"
            container_port: "80"
        volumes:
          - host_path: wordpress-data.volume
            container_path: /var/www/html
        networks:
          - wordpress.network
  roles:
    - community.podman_quadlets.podman_quadlets
```

### Using Secrets

```yaml
---
- name: Deploy app with secrets
  hosts: localhost
  tasks:
    - name: Create database password secret
      community.podman_quadlets.podman_quadlet_secret:
        name: db-password
        data: "{{ vault_db_password }}"

    - name: Create application container
      community.podman_quadlets.podman_quadlet_container:
        name: myapp
        image: myapp:latest
        secrets:
          db-password: DATABASE_PASSWORD
```

## Directory Structure

After deployment, quadlet files are created in the following structure:

```
~/.config/containers/systemd/
├── myapp.container
├── myapp.network
└── myapp-data.volume
```

These are automatically loaded by systemd and can be managed with standard systemd commands:

```bash
# Check status
systemctl --user status myapp.service

# Start/stop services
systemctl --user start myapp.service
systemctl --user stop myapp.service

# View logs
journalctl --user -u myapp.service
```

## Testing

The collection includes comprehensive tests:

```bash
# Run all tests
make test

# Run specific test suites
make test-sanity
make test-units
make test-integration
make test-molecule
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/globalbots/ansible-podman-quadlets/issues)
- [Discussions](https://github.com/globalbots/ansible-podman-quadlets/discussions)
- [Wiki](https://github.com/globalbots/ansible-podman-quadlets/wiki)

## Authors

- GlobalBots Team ([@globalbots](https://github.com/globalbots))

## Acknowledgments

- The Podman team for creating Quadlets
- The Ansible community for the excellent automation framework
- All contributors who help improve this collection