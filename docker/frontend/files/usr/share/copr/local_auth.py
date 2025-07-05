#!/usr/bin/env python3
"""
Local Authentication Module for Oreon Build System
This provides simple local user creation and authentication without external providers.
"""

import flask
from coprs import app, db
from coprs.logic.users_logic import UsersLogic
from coprs.auth import UserAuth


class OreonLocalAuth:
    """
    Simple local authentication for Oreon Build System
    """
    
    @staticmethod
    def create_local_user(username, email=None):
        """
        Create a local user account
        """
        if not username:
            return None
            
        # Check if user already exists
        existing_user = UsersLogic.get(username).first()
        if existing_user:
            return existing_user
            
        # Create new local user
        app.logger.info("Creating local user: %s", username)
        user = UsersLogic.create_user_wrapper(
            username=username,
            email=email or f"{username}@oreon-build-system.local",
            timezone=None
        )
        
        # Set as local user (no external groups)
        user.openid_groups = {}
        
        return user
    
    @staticmethod
    def login_local_user(username, create_if_missing=True):
        """
        Log in a local user, creating if it doesn't exist
        """
        user = UsersLogic.get(username).first()
        
        if not user and create_if_missing:
            user = OreonLocalAuth.create_local_user(username)
            
        if user:
            flask.session['local_user'] = username
            app.logger.info("Local user '%s' logged in", username)
            
        return user
    
    @staticmethod
    def current_local_user():
        """
        Get current local user from session
        """
        return flask.session.get('local_user')
    
    @staticmethod
    def logout_local_user():
        """
        Log out current local user
        """
        flask.session.pop('local_user', None)


def init_local_auth():
    """
    Initialize local authentication for Oreon Build System
    """
    # Create default admin user if it doesn't exist
    admin_user = OreonLocalAuth.create_local_user('admin', 'admin@oreon-build-system.local')
    if admin_user:
        # Make sure admin user exists in database
        db.session.commit()
        app.logger.info("Default admin user created/verified") 