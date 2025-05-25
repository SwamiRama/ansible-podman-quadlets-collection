#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError


def extract_volumes(containers):
    """Extract unique volumes from container definitions."""
    volumes = []
    seen = set()
    
    for container in containers:
        if 'volumes' in container:
            for volume in container['volumes']:
                if 'host_path' in volume and volume['host_path'].endswith('.volume'):
                    if volume['host_path'] not in seen:
                        seen.add(volume['host_path'])
                        volumes.append(volume['host_path'])
    
    return volumes


def extract_networks(containers):
    """Extract unique networks from container definitions."""
    networks = []
    seen = set()
    
    for container in containers:
        if 'networks' in container:
            for network in container['networks']:
                if network not in seen and network.endswith('.network'):
                    seen.add(network)
                    networks.append(network)
    
    return networks


def quadlet_format(value, key=None):
    """Format values for quadlet files."""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (list, tuple)):
        return ' '.join(str(v) for v in value)
    elif isinstance(value, dict):
        if key == 'labels':
            return ['{}={}'.format(k, v) for k, v in value.items()]
        elif key == 'environment':
            return ['{}={}'.format(k, v) for k, v in value.items()]
    return str(value)


def to_systemd_unit_name(name):
    """Convert a name to a valid systemd unit name."""
    # Replace invalid characters with hyphens
    import re
    name = re.sub(r'[^a-zA-Z0-9:._-]', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)
    return name


class FilterModule(object):
    """Ansible filters for podman quadlets."""

    def filters(self):
        return {
            'extract_volumes': extract_volumes,
            'extract_networks': extract_networks,
            'quadlet_format': quadlet_format,
            'to_systemd_unit_name': to_systemd_unit_name,
        }