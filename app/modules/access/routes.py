from flask import render_template, flash, redirect, url_for, request, \
    current_app
from flask_login import login_required
from app import db, audit
from app.main import bp
from app.models import User
from app.modules.access.models import Access
from app.modules.role.models import Role
from app.modules.resource.models import Resource
from app.modules.role.forms import RoleForm
from app.modules.resource.forms import ResourceForm
from app.modules.access.forms import AccessForm
from flask_babel import _


@bp.route('/access/add', methods=['GET', 'POST'])
@login_required
def access_add():
    if 'cancel' in request.form:
        return redirect(request.referrer)

    form = AccessForm(formdata=request.form)

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        access = Access(comment=form.comment.data,
                        start=form.start.data,
                        stop=form.stop.data
                        )

        access.user = user
        access.role = role
        db.session.add(access)
        db.session.commit()
        audit.auditlog_new_post('access', original_data=access.to_dict(), record_name=access.__tablename__)
        flash(_('New access is now posted!'))

        return redirect(url_for('main.index'))

    else:

        return render_template('access.html', title=_('Add Access'),
                               form=form)


@bp.route('/access/edit/', methods=['GET', 'POST'])
@login_required
def access_edit():

    accessid = request.args.get('access')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'delete' in request.form:
        return redirect(url_for('main.access_delete', access=accessid))
    if 'copy' in request.form:
        return redirect(url_for('main.access_copy', copy_from_access=accessid))
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='access', module_id=accessid))
    if 'ports' in request.form:
        return redirect(url_for('main.access_port_list', access=accessid))

    access = Access.query.get(accessid)
    original_data = access.to_dict()

    if access is None:
        render_template('service.html', title=_('Access is not defined'))

    form = AccessForm(formdata=request.form, obj=access)

    if request.method == 'POST' and form.validate_on_submit():

        access.comment = form.comment.data
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        access.comment = form.comment.data
        access.start = form.start.data
        access.stop = form.stop.data
        access.user = user
        access.role = role

        db.session.commit()
        audit.auditlog_update_post('access', original_data=original_data, updated_data=access.to_dict(), record_name=access.__tablename__)
        flash(_('Your changes have been saved.'))

        return redirect(url_for('main.index'))

    else:
        form.user.data = access.user_id
        form.role.data = access.role_id
        return render_template('access.html', title=_('Edit Access'),
                               form=form)


@bp.route('/access/list/', methods=['GET', 'POST'])
@login_required
def access_list():

    page = request.args.get('page', 1, type=int)
    accesses = Access.query.order_by(Access.id).paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.access_list', page=accesses.next_num) \
        if accesses.has_next else None
    prev_url = url_for('main.access_list', page=accesses.prev_num) \
        if accesses.has_prev else None

    return render_template('access.html', title=_('Access'),
                           accesses=accesses.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/access/delete/', methods=['GET', 'POST'])
@login_required
def access_delete():

    accessid = request.args.get('access')
    access = Access.query.get(accessid)

    if access is None:
        flash(_('Access was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    deleted_msg = 'Access deleted: %s\n' % (access.name)
    flash(deleted_msg)
    db.session.delete(access)
    db.session.commit()
    audit.auditlog_delete_post('access', data=access.to_dict(), record_name=access.name)

    return redirect(url_for('main.index'))
