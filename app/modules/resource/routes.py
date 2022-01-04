from flask import render_template, flash, redirect, url_for, request, \
    current_app
from flask_login import login_required
from app import db
from app.main import bp
from app.main.models import Service
from app.modules.resource.models import Resource
from app.modules.resource.forms import ResourceForm
from flask_babel import _


@bp.route('/resource/add', methods=['GET', 'POST'])
@login_required
def resource_add():
    if 'cancel' in request.form:
        return redirect(request.referrer)

    form = ResourceForm(formdata=request.form)

    ip = request.args.get('ip')
    if ip:
        form.ipaddress.data = ip

    if request.method == 'POST' and form.validate_on_submit():
        service = Service.query.get(form.service.data)
        if service is None:
            flash('Service is required')
            return redirect(request.referrer)

        resource = Resource(name=form.name.data,
                            comment=form.comment.data,
                            environment=form.environment.data,
                            external_id=form.external_id.data
                            )

        resource.service = service
        db.session.add(resource)
        db.session.commit()
        current_app.audit.auditlog_new_post('resource', original_data=resource.to_dict(), record_name=resource.name)
        flash(_('New resource is now posted!'))

        return redirect(url_for('main.index'))

    else:

        return render_template('resource.html', title=_('Add Resource'),
                               form=form)


@bp.route('/resource/edit/', methods=['GET', 'POST'])
@login_required
def resource_edit():

    resourceid = request.args.get('resource')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'delete' in request.form:
        return redirect(url_for('main.resource_delete', resource=resourceid))
    if 'copy' in request.form:
        return redirect(url_for('main.resource_copy', copy_from_resource=resourceid))
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='resource', module_id=resourceid))
    if 'ports' in request.form:
        return redirect(url_for('main.resource_port_list', resource=resourceid))

    resource = Resource.query.get(resourceid)
    original_data = resource.to_dict()

    if resource is None:
        render_template('service.html', title=_('Resource is not defined'))

    form = ResourceForm(formdata=request.form, obj=resource)

    if request.method == 'POST' and form.validate_on_submit():

        resource.name = form.name.data
        resource.comment = form.comment.data
        resource.environment=form.environment.data
        resource.external_id=form.external_id.data

        db.session.commit()
        current_app.audit.auditlog_update_post('resource', original_data=original_data, updated_data=resource.to_dict(), record_name=resource.name)
        flash(_('Your changes have been saved.'))

        return redirect(url_for('main.index'))

    else:

        form.name.data = resource.name
        form.comment.data = resource.comment
        form.external_id.data = resource.external_id
        return render_template('resource.html', title=_('Edit Resource'),
                               form=form)


@bp.route('/resource/list/', methods=['GET', 'POST'])
@login_required
def resource_list():

    page = request.args.get('page', 1, type=int)
    service_name = request.args.get('service')
    service = Service.query.filter_by(name=service_name).first()

    resources = None
    if service:
        resources = Resource.query.filter_by(service_id=service.id).paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        resources = Resource.query.order_by(Resource.name).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.resource_list', page=resources.next_num) \
        if resources.has_next else None
    prev_url = url_for('main.resource_list', page=resources.prev_num) \
        if resources.has_prev else None

    return render_template('resource.html', title=_('Resource'),
                           resources=resources.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/resource/delete/', methods=['GET', 'POST'])
@login_required
def resource_delete():

    resourceid = request.args.get('resource')
    resource = Resource.query.get(resourceid)

    if resource is None:
        flash(_('Resource was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    deleted_msg = 'Resource deleted: %s\n' % (resource.name)
    flash(deleted_msg)
    db.session.delete(resource)
    db.session.commit()
    current_app.audit.auditlog_delete_post('resource', data=resource.to_dict(), record_name=resource.name)

    return redirect(url_for('main.index'))
