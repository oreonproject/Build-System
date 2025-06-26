"""
ISO Builder Logic for Oreon Build System

This module provides the business logic for ISO building functionality,
including queuing builds, managing templates, and handling build processes.
"""

import os
import json
import tempfile
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any

from coprs import db, app
from coprs.models import ISOBuild, ISOProject, ISOTemplate
from coprs.logic.coprs_logic import CoprsLogic
from coprs.exceptions import ObjectNotFound, InsufficientRightsException


class ISOBuilderLogic:
    """
    Logic class for ISO building operations
    """

    @staticmethod
    def queue_build(iso_build: ISOBuild) -> bool:
        """
        Queue an ISO build for processing.
        
        Args:
            iso_build: The ISOBuild instance to queue
            
        Returns:
            bool: True if successfully queued, False otherwise
        """
        try:
            # Set initial status
            iso_build.status = 'pending'
            iso_build.submitted_on = datetime.utcnow()
            
            # Generate task ID
            iso_build.task_id = f"iso-{iso_build.id}-{int(datetime.utcnow().timestamp())}"
            
            # TODO: Implement actual queuing to background worker
            # For now, just mark as queued
            db.session.commit()
            
            app.logger.info(f"ISO build {iso_build.id} queued successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to queue ISO build {iso_build.id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def cancel_build(iso_build: ISOBuild) -> bool:
        """
        Cancel a running or pending ISO build.
        
        Args:
            iso_build: The ISOBuild instance to cancel
            
        Returns:
            bool: True if successfully cancelled, False otherwise
        """
        try:
            if iso_build.status not in ['pending', 'running']:
                raise ValueError(f"Cannot cancel build in status: {iso_build.status}")
            
            # TODO: Implement actual cancellation of background task
            iso_build.status = 'canceled'
            iso_build.ended_on = datetime.utcnow()
            iso_build.error_message = "Build cancelled by user"
            
            db.session.commit()
            
            app.logger.info(f"ISO build {iso_build.id} cancelled successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to cancel ISO build {iso_build.id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_build_logs(iso_build: ISOBuild) -> str:
        """
        Retrieve build logs for an ISO build.
        
        Args:
            iso_build: The ISOBuild instance
            
        Returns:
            str: The build log content
        """
        try:
            if iso_build.build_log:
                return iso_build.build_log
            
            # Try to read from log file if available
            if iso_build.result_dir:
                log_file = os.path.join(iso_build.result_dir, 'build.log')
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
            return "No logs available yet."
            
        except Exception as e:
            app.logger.error(f"Failed to get logs for ISO build {iso_build.id}: {str(e)}")
            return f"Error reading logs: {str(e)}"

    @staticmethod
    def get_kickstart_templates() -> List[Dict[str, Any]]:
        """
        Get all available kickstart templates.
        
        Returns:
            List of template dictionaries
        """
        try:
            templates = []
            
            # Get public templates from database
            public_templates = ISOTemplate.query.filter_by(is_public=True).all()
            for template in public_templates:
                templates.append(template.to_dict())
            
            # Add built-in templates
            builtin_templates = ISOBuilderLogic._get_builtin_templates()
            templates.extend(builtin_templates)
            
            return templates
            
        except Exception as e:
            app.logger.error(f"Failed to get kickstart templates: {str(e)}")
            return []

    @staticmethod
    def get_kickstart_template(template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific kickstart template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary or None if not found
        """
        try:
            # Check database templates first
            template = ISOTemplate.query.filter_by(name=template_name).first()
            if template:
                return template.to_dict(include_content=True)
            
            # Check built-in templates
            builtin_templates = ISOBuilderLogic._get_builtin_templates()
            for template in builtin_templates:
                if template['name'] == template_name:
                    return template
            
            return None
            
        except Exception as e:
            app.logger.error(f"Failed to get template {template_name}: {str(e)}")
            return None

    @staticmethod
    def validate_kickstart(content: str) -> Dict[str, Any]:
        """
        Validate kickstart content for syntax and basic requirements.
        
        Args:
            content: Kickstart file content
            
        Returns:
            Dictionary with validation results
        """
        try:
            result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'info': []
            }
            
            if not content.strip():
                result['valid'] = False
                result['errors'].append("Kickstart content is empty")
                return result
            
            lines = content.split('\n')
            
            # Basic syntax validation
            required_sections = ['%packages', '%end']
            found_sections = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('%'):
                    section = line.split()[0]
                    found_sections.append(section)
            
            # Check for required sections
            if '%packages' not in found_sections:
                result['warnings'].append("No %packages section found - ISO may be very minimal")
            
            if '%end' not in found_sections:
                result['errors'].append("Missing %end directive")
                result['valid'] = False
            
            # Check for common requirements
            has_url_or_repo = any(line.strip().startswith(('url', 'repo')) for line in lines)
            if not has_url_or_repo:
                result['warnings'].append("No repository configuration found - build may fail")
            
            # Check for root password or user creation
            has_auth = any(line.strip().startswith(('rootpw', 'user')) for line in lines)
            if not has_auth:
                result['warnings'].append("No root password or user account configured")
            
            result['info'].append(f"Kickstart has {len(lines)} lines")
            result['info'].append(f"Found sections: {', '.join(found_sections)}")
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'warnings': [],
                'info': []
            }

    @staticmethod
    def create_livemedia_command(iso_build: ISOBuild) -> List[str]:
        """
        Create the livemedia-creator command for building ISO.
        
        Args:
            iso_build: The ISOBuild instance
            
        Returns:
            List of command arguments
        """
        cmd = ['livemedia-creator']
        
        # Basic options
        cmd.extend(['--make-iso'])
        
        # Add kickstart
        if iso_build.kickstart_path:
            cmd.extend(['--ks', iso_build.kickstart_path])
        else:
            # Create temporary kickstart file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ks', delete=False) as f:
                f.write(iso_build.kickstart_content)
                cmd.extend(['--ks', f.name])
        
        # Add build options from JSON
        options = iso_build.build_options_dict
        
        if options.get('iso_only'):
            cmd.append('--iso-only')
        
        if options.get('no_virt'):
            cmd.append('--no-virt')
        
        if options.get('nomacboot'):
            cmd.append('--nomacboot')
        
        # Set volume ID
        cmd.extend(['--volid', iso_build.volid])
        
        # Set release version
        cmd.extend(['--releasever', iso_build.release_version])
        
        # Set output directory
        if iso_build.result_dir:
            cmd.extend(['--resultdir', iso_build.result_dir])
        
        # Memory and timeout
        memory = options.get('memory', 2048)
        cmd.extend(['--ram', str(memory)])
        
        return cmd

    @staticmethod
    def _get_builtin_templates() -> List[Dict[str, Any]]:
        """
        Get built-in kickstart templates.
        
        Returns:
            List of built-in template dictionaries
        """
        return [
            {
                'name': 'oreon-minimal',
                'description': 'Minimal Oreon Linux installation',
                'category': 'minimal',
                'is_official': True,
                'kickstart_content': """# Oreon Linux Minimal Installation
text
lang en_US.UTF-8
keyboard us
timezone America/New_York

# Root password (please change!)
rootpw --plaintext oreon

# Disk configuration
clearpart --all --initlabel
autopart

# Package selection
%packages --default
@core
%end

# Post-installation
%post
echo "Welcome to Oreon Linux!" > /etc/motd
%end
""",
                'supported_architectures': ['x86_64', 'aarch64'],
                'default_release_version': '10'
            },
            {
                'name': 'oreon-desktop',
                'description': 'Oreon Linux with GNOME desktop environment',
                'category': 'desktop',
                'is_official': True,
                'kickstart_content': """# Oreon Linux Desktop Installation
text
lang en_US.UTF-8
keyboard us
timezone America/New_York

# Root password (please change!)
rootpw --plaintext oreon

# User account
user --name=oreon --password=oreon --plaintext --gecos="Oreon User"

# Disk configuration
clearpart --all --initlabel
autopart

# Network configuration
network --bootproto=dhcp --device=link --activate

# Package selection
%packages --default
@core
@gnome-desktop-environment
@multimedia
@development-tools
firefox
libreoffice
%end

# Services
services --enabled=gdm,NetworkManager

# Post-installation
%post
echo "Welcome to Oreon Linux Desktop!" > /etc/motd
%end
""",
                'supported_architectures': ['x86_64'],
                'default_release_version': '10'
            },
            {
                'name': 'oreon-server',
                'description': 'Oreon Linux server installation',
                'category': 'server',
                'is_official': True,
                'kickstart_content': """# Oreon Linux Server Installation
text
lang en_US.UTF-8
keyboard us
timezone UTC

# Root password (please change!)
rootpw --plaintext oreon

# Disk configuration
clearpart --all --initlabel
autopart

# Network configuration
network --bootproto=dhcp --device=link --activate

# Package selection
%packages --default
@core
@server-product-environment
openssh-server
httpd
mariadb-server
%end

# Services
services --enabled=sshd,httpd,mariadb

# Firewall
firewall --enabled --service=ssh,http,https

# Post-installation
%post
echo "Welcome to Oreon Linux Server!" > /etc/motd
systemctl enable sshd
%end
""",
                'supported_architectures': ['x86_64', 'aarch64'],
                'default_release_version': '10'
            }
        ]

    @staticmethod
    def estimate_build_time(iso_build: ISOBuild) -> int:
        """
        Estimate build time in minutes based on build configuration.
        
        Args:
            iso_build: The ISOBuild instance
            
        Returns:
            Estimated build time in minutes
        """
        base_time = 30  # Base time for minimal build
        
        # Check kickstart content for package groups that affect build time
        content = iso_build.kickstart_content or ""
        
        # Desktop environments add significant time
        if any(group in content.lower() for group in ['gnome', 'kde', 'xfce', 'desktop']):
            base_time += 45
        
        # Development tools
        if 'development' in content.lower():
            base_time += 20
        
        # Multimedia packages
        if 'multimedia' in content.lower():
            base_time += 15
        
        # Architecture affects build time
        if iso_build.architecture in ['aarch64', 'armhfp']:
            base_time += 10
        
        return base_time 