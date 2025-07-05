#!/usr/bin/env python3
"""
Authentication Patch for Oreon Build System
This patches the existing COPR authentication to support local users
"""

import flask
from coprs import app
from coprs.auth import UserAuth as OriginalUserAuth
from local_auth import OreonLocalAuth


class PatchedUserAuth:
    """
    Patched UserAuth that checks local users first
    """

    @staticmethod
    def logout():
        """
        Log out the current user (local or external)
        """
        OreonLocalAuth.logout_local_user()
        # Also call original logout for any external auth
        OriginalUserAuth.logout()

    @staticmethod
    def current_username():
        """
        Check local user first, then external auth
        """
        # Check local user first
        local_user = OreonLocalAuth.current_local_user()
        if local_user:
            return local_user
        
        # Fall back to external auth
        return OriginalUserAuth.current_username()

    @staticmethod
    def user_object(oid_resp=None, username=None):
        """
        Get or Create a `models.User` object, checking local users first
        """
        # If username is provided, check if it's a local user
        if username:
            local_user = OreonLocalAuth.current_local_user()
            if local_user == username:
                return OreonLocalAuth.login_local_user(username, create_if_missing=True)
        
        # Fall back to original method for external auth
        return OriginalUserAuth.user_object(oid_resp, username)

    @staticmethod
    def get_or_create_user(username, email=None, timezone=None):
        """
        Get the user from DB, or create a new local user
        """
        return OriginalUserAuth.get_or_create_user(username, email, timezone)


def patch_authentication():
    """
    Patch the authentication system to use local auth
    """
    # Replace UserAuth methods with patched versions
    import coprs.auth
    coprs.auth.UserAuth = PatchedUserAuth
    
    app.logger.info("Authentication system patched for local users")


def setup_local_login_menu():
    """
    Setup login menu to show local login option
    """
    from coprs.context_processors import app
    
    @app.context_processor
    def local_login_menu():
        """
        Override login menu to use local authentication
        """
        menu = []
        
        if flask.g.user:
            # User authenticated
            user = flask.g.user
            menu.append({
                'link': flask.url_for('coprs_ns.coprs_by_user', username=user.name),
                'desc': user.name,
            })

            menu.append({
                'link': flask.url_for('local_auth.local_logout'),
                'desc': 'log out',
            })
        else:
            # Show local login
            menu.append({
                'link': flask.url_for('local_auth.local_login'),
                'desc': 'log in',
            })

        return dict(login_menu=menu)


# Apply patches when module is imported
if __name__ != '__main__':
    patch_authentication()
    setup_local_login_menu() 