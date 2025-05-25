#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, GlobalBots Team <team@globalbots.net>
# MIT License

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_text


class PodmanQuadletBase:
    """Base class for Podman Quadlet operations."""
    
    def __init__(self, module):
        self.module = module
        self.check_mode = module.check_mode
        
    def _expand_path(self, path):
        """Expand user and environment variables in path."""
        return os.path.expanduser(os.path.expandvars(path))
    
    def _ensure_directory(self, path):
        """Ensure directory exists."""
        expanded_path = self._expand_path(path)
        if not os.path.exists(expanded_path):
            if not self.check_mode:
                os.makedirs(expanded_path, mode=0o750)
            return True
        return False
    
    def _read_file(self, path):
        """Read file contents."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError as e:
            return None
    
    def _write_file(self, path, content, mode=0o640):
        """Write content to file."""
        if self.check_mode:
            return True
            
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(path))
        try:
            with os.fdopen(temp_fd, 'w') as f:
                f.write(content)
            
            # Set permissions
            os.chmod(temp_path, mode)
            
            # Move to final location
            os.rename(temp_path, path)
            return True
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def _file_exists(self, path):
        """Check if file exists."""
        return os.path.exists(self._expand_path(path))
    
    def _remove_file(self, path):
        """Remove file if it exists."""
        expanded_path = self._expand_path(path)
        if os.path.exists(expanded_path):
            if not self.check_mode:
                os.unlink(expanded_path)
            return True
        return False
    
    def generate_quadlet_content(self, config, quadlet_type='container'):
        """Generate quadlet file content."""
        lines = ['[Unit]']
        
        if 'service_description' in config:
            lines.append(f"Description={config['service_description']}")
        
        if 'required_services' in config and config['required_services']:
            lines.append(f"Requires={config['required_services']}")
        
        if 'after_services' in config and config['after_services']:
            lines.append(f"After={config['after_services']}")
        
        lines.append('')
        lines.append(f'[{quadlet_type.capitalize()}]')
        
        # Add type-specific configuration
        if quadlet_type == 'container':
            lines.extend(self._generate_container_config(config))
        elif quadlet_type == 'network':
            lines.extend(self._generate_network_config(config))
        elif quadlet_type == 'volume':
            lines.extend(self._generate_volume_config(config))
        
        lines.append('')
        lines.append('[Service]')
        lines.append('Restart=always')
        lines.append('')
        lines.append('[Install]')
        lines.append('WantedBy=default.target')
        
        return '\n'.join(lines)
    
    def _generate_container_config(self, config):
        """Generate container-specific configuration."""
        lines = []
        
        if 'container_image' in config:
            lines.append(f"Image={config['container_image']}")
        
        if 'container_name' in config:
            lines.append(f"ContainerName={config['container_name']}")
        
        # Environment variables
        if 'environment_variables' in config and config['environment_variables']:
            for key, value in config['environment_variables'].items():
                lines.append(f"Environment={key}={value}")
        
        # Volumes
        if 'volumes' in config and config['volumes']:
            for volume in config['volumes']:
                lines.append(f"Volume={volume['host_path']}:{volume['container_path']}")
        
        # Networks
        if 'networks' in config and config['networks']:
            for network in config['networks']:
                lines.append(f"Network={network}")
        
        # Ports
        if 'ports' in config and config['ports']:
            for port in config['ports']:
                lines.append(f"PublishPort={port['host_port']}:{port['container_port']}")
        
        # Labels
        if 'labels' in config and config['labels']:
            for key, value in config['labels'].items():
                lines.append(f"Label={key}={value}")
        
        # Secrets
        if 'secrets' in config and config['secrets']:
            for key, value in config['secrets'].items():
                lines.append(f"Secret={key},type=env,target={value}")
        
        # Auto update
        if 'auto_update' in config:
            lines.append(f"AutoUpdate={config['auto_update']}")
        
        return lines
    
    def _generate_network_config(self, config):
        """Generate network-specific configuration."""
        lines = []
        
        if 'driver' in config:
            lines.append(f"Driver={config['driver']}")
        
        if 'options' in config:
            for key, value in config['options'].items():
                lines.append(f"Options={key}={value}")
        
        return lines
    
    def _generate_volume_config(self, config):
        """Generate volume-specific configuration."""
        lines = []
        
        if 'driver' in config:
            lines.append(f"Driver={config['driver']}")
        
        if 'options' in config:
            for key, value in config['options'].items():
                lines.append(f"Options={key}={value}")
        
        return lines
    
    def manage_quadlet(self, name, state, config, quadlet_type='container'):
        """Manage a quadlet file."""
        quadlet_dir = self._expand_path(self.module.params.get('quadlet_dir', '~/.config/containers/systemd'))
        quadlet_file = os.path.join(quadlet_dir, f"{name}.{quadlet_type}")
        
        result = {
            'changed': False,
            'quadlet_file': quadlet_file,
            'service_name': f"{name}.service"
        }
        
        # Ensure directory exists
        if self._ensure_directory(quadlet_dir):
            result['changed'] = True
        
        if state == 'absent':
            if self._remove_file(quadlet_file):
                result['changed'] = True
                result['msg'] = f"Removed quadlet file {quadlet_file}"
        else:
            # Generate new content
            new_content = self.generate_quadlet_content(config, quadlet_type)
            
            # Check if file exists and compare content
            current_content = self._read_file(quadlet_file)
            
            if current_content != new_content:
                if self._write_file(quadlet_file, new_content):
                    result['changed'] = True
                    result['msg'] = f"Created/Updated quadlet file {quadlet_file}"
            else:
                result['msg'] = f"Quadlet file {quadlet_file} is up to date"
        
        return result


def generate_container_quadlet(config):
    """Helper function to generate container quadlet content."""
    base = PodmanQuadletBase(None)
    return base.generate_quadlet_content(config, 'container')