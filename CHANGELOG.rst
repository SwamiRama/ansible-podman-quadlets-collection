================================
community.podman_quadlets v1.0.0
================================

.. contents:: Topics

v1.0.0
======

Release Summary
---------------

Initial release of the community.podman_quadlets collection, providing comprehensive support for managing Podman containers using systemd Quadlets.

Major Changes
-------------

- Initial implementation of podman_quadlet_container module for managing containers
- Initial implementation of podman_quadlet_network module for managing networks  
- Initial implementation of podman_quadlet_volume module for managing volumes
- Initial implementation of podman_quadlet_secret module for managing secrets
- Added podman_quadlets role for declarative container management
- Added podman_setup role for Podman installation and configuration

New Modules
-----------

- podman_quadlet_container - Manage Podman containers using Quadlets
- podman_quadlet_network - Manage Podman networks using Quadlets
- podman_quadlet_volume - Manage Podman volumes using Quadlets
- podman_quadlet_secret - Manage Podman secrets for use with Quadlets

New Roles
---------

- podman_quadlets - Comprehensive role for managing containers, networks, and volumes
- podman_setup - Role for installing and configuring Podman

New Plugins
-----------

Filter
~~~~~~

- extract_volumes - Extract unique volumes from container definitions
- extract_networks - Extract unique networks from container definitions
- quadlet_format - Format values for quadlet files
- to_systemd_unit_name - Convert names to valid systemd unit names