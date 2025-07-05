#!/usr/bin/env python3
"""
Local Authentication Routes for Oreon Build System
"""

import flask
from flask import render_template, request, redirect, url_for, flash
from coprs import app
from local_auth import OreonLocalAuth

# Create blueprint for local auth routes
local_auth = flask.Blueprint('local_auth', __name__)


@local_auth.route('/local_login/', methods=['GET', 'POST'])
def local_login():
    """
    Simple local login - just enter username
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Please enter a username', 'error')
            return render_template('local_login.html')
        
        # Validate username (basic validation)
        if not username.isalnum() and '-' not in username and '_' not in username:
            flash('Username can only contain letters, numbers, hyphens, and underscores', 'error')
            return render_template('local_login.html')
        
        if len(username) < 3 or len(username) > 30:
            flash('Username must be between 3 and 30 characters', 'error')
            return render_template('local_login.html')
        
        # Login/create user
        user = OreonLocalAuth.login_local_user(username, create_if_missing=True)
        
        if user:
            flash(f'Welcome to Oreon Build System, {username}!', 'success')
            next_url = request.args.get('next') or url_for('coprs_ns.coprs_show')
            return redirect(next_url)
        else:
            flash('Login failed. Please try again.', 'error')
    
    return render_template('local_login.html')


@local_auth.route('/local_logout/')
def local_logout():
    """
    Local logout
    """
    username = OreonLocalAuth.current_local_user()
    OreonLocalAuth.logout_local_user()
    
    if username:
        flash(f'Goodbye, {username}!', 'info')
    
    return redirect(url_for('coprs_ns.coprs_show'))


# Template for local login
LOCAL_LOGIN_TEMPLATE = '''
{% extends "layout.html" %}

{% block title %}Login - Oreon Build System{% endblock %}

{% block body %}
<div class="container">
    <div class="row">
        <div class="col-md-6 col-md-offset-3">
            <div class="oreon-card">
                <div class="oreon-card-header">
                    <h3 class="oreon-card-title">Login to Oreon Build System</h3>
                </div>
                <div class="panel-body">
                    <form method="POST">
                        <div class="oreon-form-group">
                            <label for="username" class="oreon-form-label">Username:</label>
                            <input type="text" 
                                   class="oreon-form-control" 
                                   id="username" 
                                   name="username" 
                                   placeholder="Enter your username"
                                   required
                                   autofocus>
                            <small class="help-block">
                                Enter any username to login. If this is your first time, an account will be created automatically.
                            </small>
                        </div>
                        <button type="submit" class="oreon-btn oreon-btn-primary">
                            <i class="fa fa-sign-in"></i> Login
                        </button>
                    </form>
                </div>
            </div>
            
            <div class="text-center" style="margin-top: 30px;">
                <p class="text-muted">
                    <strong>Local Authentication:</strong> No external accounts required.<br>
                    Simply enter a username to create your local Oreon Build System account.
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Register template
@app.template_global()
def get_local_login_template():
    return LOCAL_LOGIN_TEMPLATE


def register_local_auth_routes(app):
    """
    Register local authentication routes with the Flask app
    """
    app.register_blueprint(local_auth) 