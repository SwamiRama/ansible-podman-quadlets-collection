#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: podman_quadlet_container
short_description: Manage Podman containers using Quadlets
version_added: "1.0.0"
description:
  - Create, update, and delete Podman containers using systemd Quadlets
  - Quadlets provide native systemd integration for Podman containers
options:
  name:
    description:
      - Name of the container
    required: true
    type: str
  state:
    description:
      - Desired state of the container
    choices: ['present', 'absent', 'started', 'stopped']
    default: present
    type: str
  image:
    description:
      - Container image to use
    required: true
    type: str
  environment:
    description:
      - Environment variables for the container
    type: dict
    default: {}
  volumes:
    description:
      - List of volumes to mount
    type: list
    elements: dict
    suboptions:
      host_path:
        description: Path on the host
        type: str
        required: true
      container_path:
        description: Path in the container
        type: str
        required: true
  networks:
    description:
      - List of networks to connect to
    type: list
    elements: str
    default: []
  labels:
    description:
      - Labels to apply to the container
    type: dict
    default: {}
  ports:
    description:
      - Port mappings
    type: list
    elements: dict
    suboptions:
      host_port:
        description: Port on the host
        type: str
        required: true
      container_port:
        description: Port in the container
        type: str
        required: true
  secrets:
    description:
      - Secrets to mount in the container
    type: dict
    default: {}
  auto_update:
    description:
      - Enable automatic updates
    type: str
    choices: ['registry', 'local', 'disabled']
    default: 'registry'
  restart_policy:
    description:
      - Restart policy for the container
    type: str
    choices: ['always', 'on-failure', 'unless-stopped', 'no']
    default: 'always'
  quadlet_dir:
    description:
      - Directory to store quadlet files
    type: path
    default: ~/.config/containers/systemd
author:
  - GlobalBots Team (@globalbots)
extends_documentation_fragment:
  - community.podman_quadlets.podman_quadlets
'''

EXAMPLES = r'''
- name: Create a simple container
  community.podman_quadlets.podman_quadlet_container:
    name: nginx
    image: docker.io/nginx:latest
    state: present
    ports:
      - host_port: "8080"
        container_port: "80"

- name: Create container with environment and volumes
  community.podman_quadlets.podman_quadlet_container:
    name: webapp
    image: myapp:latest
    environment:
      DATABASE_URL: "postgresql://localhost/myapp"
      DEBUG: "false"
    volumes:
      - host_path: webapp-data.volume
        container_path: /data
    networks:
      - internal.network
    labels:
      app: webapp
      env: production

- name: Remove a container
  community.podman_quadlets.podman_quadlet_container:
    name: nginx
    state: absent
'''

RETURN = r'''
quadlet_file:
    description: Path to the generated quadlet file
    type: str
    returned: always
    sample: /home/user/.config/containers/systemd/nginx.container
changed:
    description: Whether the container configuration was changed
    type: bool
    returned: always
service_name:
    description: Name of the systemd service
    type: str
    returned: always
    sample: nginx.service
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.podman_quadlets.plugins.module_utils.podman_quadlets import (
    PodmanQuadletBase,
    generate_container_quadlet
)


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent', 'started', 'stopped']),
        image=dict(type='str', required=True),
        environment=dict(type='dict', default={}),
        volumes=dict(type='list', elements='dict', default=[]),
        networks=dict(type='list', elements='str', default=[]),
        labels=dict(type='dict', default={}),
        ports=dict(type='list', elements='dict', default=[]),
        secrets=dict(type='dict', default={}),
        auto_update=dict(type='str', default='registry', choices=['registry', 'local', 'disabled']),
        restart_policy=dict(type='str', default='always', choices=['always', 'on-failure', 'unless-stopped', 'no']),
        quadlet_dir=dict(type='path', default='~/.config/containers/systemd'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    quadlet = PodmanQuadletBase(module)
    
    # Generate the container configuration
    container_config = {
        'name': module.params['name'] + '.container',
        'service_description': f"{module.params['name']} Container",
        'container_image': module.params['image'],
        'container_name': module.params['name'],
        'environment_variables': module.params['environment'],
        'volumes': module.params['volumes'],
        'networks': module.params['networks'],
        'labels': module.params['labels'],
        'ports': module.params['ports'],
        'secrets': module.params['secrets'],
        'auto_update': module.params['auto_update'],
    }
    
    result = quadlet.manage_quadlet(
        name=module.params['name'],
        state=module.params['state'],
        config=container_config,
        quadlet_type='container'
    )
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()