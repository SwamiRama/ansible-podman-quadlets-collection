Getting Started
===============

This guide will help you get started with the community.podman_quadlets collection.

Prerequisites
-------------

Before using this collection, ensure you have:

1. **Podman 4.4+** installed
2. **Ansible 2.14+** installed
3. **Python 3.9+** installed
4. A system with **systemd** support

Installation
------------

Install the collection using ansible-galaxy::

    ansible-galaxy collection install community.podman_quadlets

Or add to your requirements.yml::

    ---
    collections:
      - name: community.podman_quadlets
        version: ">=1.0.0"

First Steps
-----------

1. **Simple Container Deployment**

   Create a playbook to deploy a basic nginx container::

       ---
       - name: Deploy nginx container
         hosts: localhost
         tasks:
           - name: Create nginx container
             community.podman_quadlets.podman_quadlet_container:
               name: nginx
               image: docker.io/nginx:latest
               ports:
                 - host_port: "8080"
                   container_port: "80"

2. **Using the Role**

   For more complex deployments, use the provided role::

       ---
       - name: Deploy application stack
         hosts: container_hosts
         vars:
           project_name: myapp
           containers:
             - name: webapp.container
               container_image: "myapp:latest"
               container_name: "webapp"
               ports:
                 - host_port: "80"
                   container_port: "8000"
         roles:
           - community.podman_quadlets.podman_quadlets

3. **Verify Deployment**

   After running your playbook, verify the deployment::

       # Check service status
       systemctl --user status webapp.service
       
       # View logs
       journalctl --user -u webapp.service
       
       # List quadlet files
       ls ~/.config/containers/systemd/

Understanding Quadlets
----------------------

Quadlets are systemd unit files that define Podman containers, networks, and volumes. They provide:

- **Native systemd integration**: Containers are first-class systemd services
- **Automatic dependency management**: Define relationships between containers
- **Built-in health checks**: systemd monitors container health
- **Centralized logging**: All logs go through journald

Next Steps
----------

- Review the :doc:`examples` for common deployment patterns
- Explore the :doc:`modules` reference for detailed options
- Read about the :doc:`roles` for declarative management