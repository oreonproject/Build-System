"""
ISO Builder Views for Oreon Build System

This module provides views for building custom ISO images using kickstart files
and livemedia-creator technology.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

from coprs import db, app
from coprs.forms import ISOBuildForm, ISOProjectForm
from coprs.models import ISOBuild, ISOProject, User
from coprs.logic.iso_builder import ISOBuilderLogic
from coprs.helpers import generate_api_token

iso_ns = Blueprint("iso_ns", __name__, url_prefix="/iso")

@iso_ns.route("/")
def iso_index():
    """ISO Builder main page showing recent builds and overview."""
    recent_builds = ISOBuild.query.order_by(ISOBuild.submitted_on.desc()).limit(10).all()
    build_stats = {
        'total': ISOBuild.query.count(),
        'successful': ISOBuild.query.filter_by(status='succeeded').count(),
        'failed': ISOBuild.query.filter_by(status='failed').count(),
        'running': ISOBuild.query.filter_by(status='running').count()
    }
    
    return render_template("iso/index.html", 
                         recent_builds=recent_builds,
                         build_stats=build_stats)

@iso_ns.route("/new", methods=["GET", "POST"])
@login_required
def new_iso_build():
    """Create a new ISO build from kickstart file."""
    form = ISOBuildForm()
    
    if form.validate_on_submit():
        try:
            # Handle kickstart file upload
            ks_file = form.kickstart_file.data
            if ks_file:
                filename = secure_filename(ks_file.filename)
                ks_path = os.path.join(app.config['UPLOAD_FOLDER'], 'kickstarts', filename)
                os.makedirs(os.path.dirname(ks_path), exist_ok=True)
                ks_file.save(ks_path)
            
            # Create ISO build record
            iso_build = ISOBuild(
                name=form.iso_name.data,
                version=form.version.data,
                architecture=form.architecture.data,
                kickstart_path=ks_path if ks_file else None,
                kickstart_content=form.kickstart_content.data,
                volid=form.volid.data,
                release_version=form.release_version.data,
                user=current_user,
                submitted_on=datetime.utcnow(),
                status='pending',
                build_options=json.dumps({
                    'make_iso': form.make_iso.data,
                    'iso_only': form.iso_only.data,
                    'no_virt': form.no_virt.data,
                    'nomacboot': form.nomacboot.data,
                    'timeout': form.timeout.data or 3600,
                    'memory': form.memory.data or 2048
                })
            )
            
            db.session.add(iso_build)
            db.session.commit()
            
            # Queue the build
            ISOBuilderLogic.queue_build(iso_build)
            
            flash(f"ISO build '{iso_build.name}' has been queued successfully!", "success")
            return redirect(url_for("iso_ns.iso_build_detail", build_id=iso_build.id))
            
        except Exception as e:
            flash(f"Error creating ISO build: {str(e)}", "danger")
            db.session.rollback()
    
    return render_template("iso/new.html", form=form)

@iso_ns.route("/build/<int:build_id>")
def iso_build_detail(build_id):
    """Show details of a specific ISO build."""
    iso_build = ISOBuild.query.get_or_404(build_id)
    
    return render_template("iso/build_detail.html", iso_build=iso_build)

@iso_ns.route("/build/<int:build_id>/logs")
def iso_build_logs(build_id):
    """Show build logs for an ISO build."""
    iso_build = ISOBuild.query.get_or_404(build_id)
    
    try:
        log_content = ISOBuilderLogic.get_build_logs(iso_build)
    except Exception as e:
        log_content = f"Error reading logs: {str(e)}"
    
    return render_template("iso/build_logs.html", 
                         iso_build=iso_build,
                         log_content=log_content)

@iso_ns.route("/build/<int:build_id>/cancel", methods=["POST"])
@login_required
def cancel_iso_build(build_id):
    """Cancel a running ISO build."""
    iso_build = ISOBuild.query.get_or_404(build_id)
    
    if iso_build.user != current_user and not current_user.admin:
        flash("You don't have permission to cancel this build.", "danger")
        return redirect(url_for("iso_ns.iso_build_detail", build_id=build_id))
    
    if iso_build.status in ['running', 'pending']:
        try:
            ISOBuilderLogic.cancel_build(iso_build)
            flash("Build cancellation requested.", "info")
        except Exception as e:
            flash(f"Error cancelling build: {str(e)}", "danger")
    else:
        flash("Build cannot be cancelled in current state.", "warning")
    
    return redirect(url_for("iso_ns.iso_build_detail", build_id=build_id))

@iso_ns.route("/projects")
def iso_projects():
    """List all ISO projects."""
    projects = ISOProject.query.order_by(ISOProject.created_on.desc()).all()
    return render_template("iso/projects.html", projects=projects)

@iso_ns.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_iso_project():
    """Create a new ISO project for grouping related builds."""
    form = ISOProjectForm()
    
    if form.validate_on_submit():
        try:
            project = ISOProject(
                name=form.name.data,
                description=form.description.data,
                user=current_user,
                created_on=datetime.utcnow()
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash(f"ISO project '{project.name}' created successfully!", "success")
            return redirect(url_for("iso_ns.iso_project_detail", project_id=project.id))
            
        except Exception as e:
            flash(f"Error creating project: {str(e)}", "danger")
            db.session.rollback()
    
    return render_template("iso/new_project.html", form=form)

@iso_ns.route("/projects/<int:project_id>")
def iso_project_detail(project_id):
    """Show details of an ISO project."""
    project = ISOProject.query.get_or_404(project_id)
    builds = ISOBuild.query.filter_by(project_id=project_id).order_by(ISOBuild.submitted_on.desc()).all()
    
    return render_template("iso/project_detail.html", project=project, builds=builds)

@iso_ns.route("/api/builds/<int:build_id>/status")
def api_build_status(build_id):
    """API endpoint for real-time build status updates."""
    iso_build = ISOBuild.query.get_or_404(build_id)
    
    return jsonify({
        'id': iso_build.id,
        'status': iso_build.status,
        'progress': iso_build.progress or 0,
        'started_on': iso_build.started_on.isoformat() if iso_build.started_on else None,
        'ended_on': iso_build.ended_on.isoformat() if iso_build.ended_on else None,
        'result_url': iso_build.result_url
    })

@iso_ns.route("/templates")
def kickstart_templates():
    """Show available kickstart templates."""
    templates = ISOBuilderLogic.get_kickstart_templates()
    return render_template("iso/templates.html", templates=templates)

@iso_ns.route("/templates/<template_name>")
def kickstart_template_detail(template_name):
    """Show details of a specific kickstart template."""
    template = ISOBuilderLogic.get_kickstart_template(template_name)
    if not template:
        flash("Template not found.", "danger")
        return redirect(url_for("iso_ns.kickstart_templates"))
    
    return render_template("iso/template_detail.html", template=template) 