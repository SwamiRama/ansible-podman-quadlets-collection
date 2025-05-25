#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: podman_quadlet_network
short_description: Manage Podman networks using Quadlets
version_added: "1.0.0"
description:
  - Create, update, and delete Podman networks using systemd Quadlets
  - Quadlets provide native systemd integration for Podman networks
options:
  name:
    description:
      - Name of the network
    required: true
    type: str
  state:
    description:
      - Desired state of the network
    choices: ['present', 'absent']
    default: present
    type: str
  driver:
    description:
      - Network driver to use
    choices: ['bridge', 'macvlan', 'ipvlan']
    default: bridge
    type: str
  subnet:
    description:
      - Subnet for the network (e.g., 10.89.0.0/24)
    type: str
  gateway:
    description:
      - Gateway for the network
    type: str
  ip_range:
    description:
      - IP range for the network
    type: str
  ipv6:
    description:
      - Enable IPv6 on the network
    type: bool
    default: false
  internal:
    description:
      - Create an internal network (no external access)
    type: bool
    default: false
  dns_enabled:
    description:
      - Enable DNS on the network
    type: bool
    default: true
  labels:
    description:
      - Labels to apply to the network
    type: dict
    default: {}
  options:
    description:
      - Driver-specific options
    type: dict
    default: {}
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
- name: Create a simple network
  community.podman_quadlets.podman_quadlet_network:
    name: myapp
    state: present
    subnet: 10.89.0.0/24

- name: Create internal network with custom options
  community.podman_quadlets.podman_quadlet_network:
    name: internal
    state: present
    internal: true
    subnet: 172.20.0.0/16
    gateway: 172.20.0.1
    labels:
      environment: production
      app: webapp

- name: Create macvlan network
  community.podman_quadlets.podman_quadlet_network:
    name: macvlan-net
    state: present
    driver: macvlan
    options:
      parent: eth0
      mode: bridge

- name: Remove a network
  community.podman_quadlets.podman_quadlet_network:
    name: myapp
    state: absent
'''

RETURN = r'''
quadlet_file:
    description: Path to the generated quadlet file
    type: str
    returned: always
    sample: /home/user/.config/containers/systemd/myapp.network
changed:
    description: Whether the network configuration was changed
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.podman_quadlets.plugins.module_utils.podman_quadlets import PodmanQuadletBase


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        driver=dict(type='str', default='bridge', choices=['bridge', 'macvlan', 'ipvlan']),
        subnet=dict(type='str'),
        gateway=dict(type='str'),
        ip_range=dict(type='str'),
        ipv6=dict(type='bool', default=False),
        internal=dict(type='bool', default=False),
        dns_enabled=dict(type='bool', default=True),
        labels=dict(type='dict', default={}),
        options=dict(type='dict', default={}),
        quadlet_dir=dict(type='path', default='~/.config/containers/systemd'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    quadlet = PodmanQuadletBase(module)
    
    # Generate the network configuration
    network_config = {
        'name': module.params['name'] + '.network',
        'service_description': f"{module.params['name']} Network",
        'driver': module.params['driver'],
        'labels': module.params['labels'],
        'options': module.params['options'],
    }
    
    # Add optional network parameters
    if module.params['subnet']:
        network_config['subnet'] = module.params['subnet']
    if module.params['gateway']:
        network_config['gateway'] = module.params['gateway']
    if module.params['ip_range']:
        network_config['ip_range'] = module.params['ip_range']
    if module.params['ipv6']:
        network_config['ipv6'] = module.params['ipv6']
    if module.params['internal']:
        network_config['internal'] = module.params['internal']
    if not module.params['dns_enabled']:
        network_config['disable_dns'] = True
    
    result = quadlet.manage_quadlet(
        name=module.params['name'],
        state=module.params['state'],
        config=network_config,
        quadlet_type='network'
    )
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()