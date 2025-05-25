#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: podman_quadlet_volume
short_description: Manage Podman volumes using Quadlets
version_added: "1.0.0"
description:
  - Create, update, and delete Podman volumes using systemd Quadlets
  - Quadlets provide native systemd integration for Podman volumes
options:
  name:
    description:
      - Name of the volume
    required: true
    type: str
  state:
    description:
      - Desired state of the volume
    choices: ['present', 'absent']
    default: present
    type: str
  driver:
    description:
      - Volume driver to use
    default: local
    type: str
  labels:
    description:
      - Labels to apply to the volume
    type: dict
    default: {}
  options:
    description:
      - Driver-specific options
    type: dict
    default: {}
  copy:
    description:
      - Copy data from container directory when volume is created
    type: bool
    default: true
  device:
    description:
      - Device to mount (for certain drivers)
    type: str
  type:
    description:
      - Mount type (for certain drivers)
    type: str
  mount_options:
    description:
      - Mount options (comma-separated)
    type: str
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
- name: Create a simple volume
  community.podman_quadlets.podman_quadlet_volume:
    name: webapp-data
    state: present
    labels:
      app: webapp
      environment: production

- name: Create volume with specific options
  community.podman_quadlets.podman_quadlet_volume:
    name: database-data
    state: present
    driver: local
    options:
      type: tmpfs
      device: tmpfs
      o: "size=100m,uid=1000"

- name: Create NFS volume
  community.podman_quadlets.podman_quadlet_volume:
    name: shared-data
    state: present
    driver: local
    options:
      type: nfs
      o: "addr=nfs-server.example.com,rw"
      device: ":/exports/data"

- name: Remove a volume
  community.podman_quadlets.podman_quadlet_volume:
    name: webapp-data
    state: absent
'''

RETURN = r'''
quadlet_file:
    description: Path to the generated quadlet file
    type: str
    returned: always
    sample: /home/user/.config/containers/systemd/webapp-data.volume
changed:
    description: Whether the volume configuration was changed
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.podman_quadlets.plugins.module_utils.podman_quadlets import PodmanQuadletBase


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        driver=dict(type='str', default='local'),
        labels=dict(type='dict', default={}),
        options=dict(type='dict', default={}),
        copy=dict(type='bool', default=True),
        device=dict(type='str'),
        type=dict(type='str'),
        mount_options=dict(type='str'),
        quadlet_dir=dict(type='path', default='~/.config/containers/systemd'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    quadlet = PodmanQuadletBase(module)
    
    # Generate the volume configuration
    volume_config = {
        'name': module.params['name'] + '.volume',
        'service_description': f"{module.params['name']} Volume",
        'driver': module.params['driver'],
        'labels': module.params['labels'],
        'options': module.params['options'],
        'copy': module.params['copy'],
    }
    
    # Add optional volume parameters
    if module.params['device']:
        volume_config['device'] = module.params['device']
    if module.params['type']:
        volume_config['type'] = module.params['type']
    if module.params['mount_options']:
        volume_config['mount_options'] = module.params['mount_options']
    
    result = quadlet.manage_quadlet(
        name=module.params['name'],
        state=module.params['state'],
        config=volume_config,
        quadlet_type='volume'
    )
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()