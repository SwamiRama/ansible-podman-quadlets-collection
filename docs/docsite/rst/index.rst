.. _community.podman_quadlets:

Community Podman Quadlets Collection
====================================

.. toctree::
   :maxdepth: 2
   :caption: Collection Documentation

   installation
   getting_started
   examples
   modules
   roles
   contributing

This collection provides Ansible modules and roles for managing Podman containers using systemd Quadlets.

What are Podman Quadlets?
-------------------------

Quadlets are a native systemd integration for Podman that allows you to define containers, networks, and volumes as systemd units. This provides:

* Better integration with the system
* Automatic startup on boot
* Dependency management between containers
* Native systemd logging
* Resource management through systemd

Requirements
------------

* Ansible >= 2.14
* Podman >= 4.4
* Python >= 3.9
* systemd

Quick Start
-----------

Install the collection::

    ansible-galaxy collection install community.podman_quadlets

Create a simple playbook:

.. code-block:: yaml

    ---
    - name: Deploy container with Quadlets
      hosts: localhost
      vars:
        project_name: myapp
        containers:
          - name: webapp.container
            service_description: "My Web App"
            container_image: "docker.io/nginx:latest"
            container_name: "webapp"
            ports:
              - host_port: "80"
                container_port: "80"
      roles:
        - community.podman_quadlets.podman_quadlets

Features
--------

* **Native systemd Integration**: Containers managed as systemd services
* **Automatic Updates**: Built-in support for automatic container updates
* **Network Management**: Create and manage Podman networks
* **Volume Management**: Persistent storage with named volumes
* **Secret Management**: Secure handling of sensitive data
* **Health Checks**: Built-in health check support
* **Idempotent**: Safe to run multiple times

Support
-------

* `Issue Tracker <https://github.com/globalbots/ansible-podman-quadlets/issues>`_
* `GitHub Repository <https://github.com/globalbots/ansible-podman-quadlets>`_
* `Discussions <https://github.com/globalbots/ansible-podman-quadlets/discussions>`_