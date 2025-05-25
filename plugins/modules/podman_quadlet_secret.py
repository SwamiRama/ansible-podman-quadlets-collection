#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: podman_quadlet_secret
short_description: Manage Podman secrets for use with Quadlets
version_added: "1.0.0"
description:
  - Create, update, and delete Podman secrets that can be used with Quadlet containers
  - Secrets provide secure handling of sensitive data like passwords and API keys
options:
  name:
    description:
      - Name of the secret
    required: true
    type: str
  state:
    description:
      - Desired state of the secret
    choices: ['present', 'absent']
    default: present
    type: str
  data:
    description:
      - Secret data (will be stored securely)
      - Either data or file must be provided when state=present
    type: str
    no_log: true
  file:
    description:
      - Path to file containing the secret data
      - Either data or file must be provided when state=present
    type: path
  driver:
    description:
      - Secret driver to use
    default: file
    type: str
  driver_opts:
    description:
      - Driver-specific options
    type: dict
    default: {}
  labels:
    description:
      - Labels to apply to the secret
    type: dict
    default: {}
  force:
    description:
      - Force recreation of an existing secret
    type: bool
    default: false
author:
  - GlobalBots Team (@globalbots)
extends_documentation_fragment:
  - community.podman_quadlets.podman_quadlets
'''

EXAMPLES = r'''
- name: Create a secret from data
  community.podman_quadlets.podman_quadlet_secret:
    name: db-password
    data: "supersecretpassword"
    state: present
    labels:
      app: webapp
      type: database

- name: Create a secret from file
  community.podman_quadlets.podman_quadlet_secret:
    name: tls-cert
    file: /path/to/certificate.pem
    state: present

- name: Update a secret (force recreation)
  community.podman_quadlets.podman_quadlet_secret:
    name: api-key
    data: "new-api-key-value"
    force: true
    state: present

- name: Remove a secret
  community.podman_quadlets.podman_quadlet_secret:
    name: db-password
    state: absent
'''

RETURN = r'''
secret_id:
    description: ID of the created/updated secret
    type: str
    returned: when state=present
changed:
    description: Whether the secret was changed
    type: bool
    returned: always
'''

import os
import subprocess
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_bytes


class PodmanSecret:
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.data = module.params['data']
        self.file = module.params['file']
        self.driver = module.params['driver']
        self.driver_opts = module.params['driver_opts']
        self.labels = module.params['labels']
        self.force = module.params['force']
        
    def _run_podman_command(self, args, data=None):
        """Run a podman command and return the result."""
        cmd = ['podman', 'secret'] + args
        
        try:
            if data:
                # Pass data via stdin
                rc, stdout, stderr = self.module.run_command(
                    cmd, 
                    data=to_bytes(data),
                    check_rc=False
                )
            else:
                rc, stdout, stderr = self.module.run_command(cmd, check_rc=False)
                
            return rc, stdout, stderr
        except Exception as e:
            self.module.fail_json(msg=f"Failed to run podman command: {to_native(e)}")
    
    def secret_exists(self):
        """Check if secret exists."""
        rc, stdout, stderr = self._run_podman_command(['inspect', self.name])
        return rc == 0
    
    def get_secret_info(self):
        """Get information about an existing secret."""
        rc, stdout, stderr = self._run_podman_command(['inspect', self.name])
        if rc == 0:
            try:
                return json.loads(stdout)[0]
            except (json.JSONDecodeError, IndexError):
                return None
        return None
    
    def create_secret(self):
        """Create a new secret."""
        args = ['create']
        
        # Add driver options
        if self.driver and self.driver != 'file':
            args.extend(['--driver', self.driver])
        
        if self.driver_opts:
            for key, value in self.driver_opts.items():
                args.extend(['--driver-opt', f'{key}={value}'])
        
        # Add labels
        if self.labels:
            for key, value in self.labels.items():
                args.extend(['--label', f'{key}={value}'])
        
        # Add secret name
        args.append(self.name)
        
        # Add data source
        if self.file:
            args.append(self.file)
            rc, stdout, stderr = self._run_podman_command(args)
        elif self.data:
            args.append('-')
            rc, stdout, stderr = self._run_podman_command(args, data=self.data)
        else:
            self.module.fail_json(msg="Either 'data' or 'file' must be provided")
        
        if rc != 0:
            self.module.fail_json(msg=f"Failed to create secret: {stderr}")
        
        return True
    
    def remove_secret(self):
        """Remove an existing secret."""
        rc, stdout, stderr = self._run_podman_command(['rm', self.name])
        if rc != 0:
            self.module.fail_json(msg=f"Failed to remove secret: {stderr}")
        return True
    
    def manage_secret(self):
        """Main method to manage the secret."""
        result = {
            'changed': False,
            'name': self.name
        }
        
        exists = self.secret_exists()
        
        if self.state == 'absent':
            if exists:
                if not self.module.check_mode:
                    self.remove_secret()
                result['changed'] = True
                result['msg'] = f"Secret '{self.name}' removed"
            else:
                result['msg'] = f"Secret '{self.name}' does not exist"
        
        elif self.state == 'present':
            if exists and self.force:
                # Remove and recreate
                if not self.module.check_mode:
                    self.remove_secret()
                    self.create_secret()
                result['changed'] = True
                result['msg'] = f"Secret '{self.name}' recreated"
            elif not exists:
                # Create new secret
                if not self.module.check_mode:
                    self.create_secret()
                result['changed'] = True
                result['msg'] = f"Secret '{self.name}' created"
            else:
                # Secret exists and force is not set
                info = self.get_secret_info()
                if info:
                    result['secret_id'] = info.get('ID', '')
                result['msg'] = f"Secret '{self.name}' already exists"
        
        return result


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        data=dict(type='str', no_log=True),
        file=dict(type='path'),
        driver=dict(type='str', default='file'),
        driver_opts=dict(type='dict', default={}),
        labels=dict(type='dict', default={}),
        force=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['data', 'file']],
        required_if=[
            ['state', 'present', ['data', 'file'], True],
        ]
    )

    secret = PodmanSecret(module)
    result = secret.manage_secret()
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()