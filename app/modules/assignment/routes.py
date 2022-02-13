from flask import render_template, flash, redirect, url_for, request, \
    current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.main.models import User
from app.modules.assignment.models import Assignment
from app.modules.role.models import Role
from app.modules.assignment.forms import AssignmentForm, ApproveAssignmentForm
from flask_babel import _
from datetime import datetime
from app.main.models import Audit
from dateutil.relativedelta import relativedelta


@bp.route('/assignment/add', methods=['GET', 'POST'])
@login_required
def assignment_add():
    if 'cancel' in request.form:
        return redirect(request.referrer)

    form = AssignmentForm(formdata=request.form)

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        print(f"logged in user {current_user.username}")
        requestor = User.query.filter_by(
            username=current_user.username).first_or_404()
        if requestor is None:
            flash('logged in user is required')
            return redirect(request.referrer)

        assignment = Assignment(comment=form.comment.data,
                                start=form.start.data,
                                stop=form.stop.data
                                )

        assignment.user = user
        assignment.role = role
        assignment.status = "requested"
        assignment.request_ts = datetime.now()
        print(f'requestor: {requestor.username}')
        assignment.requestor = requestor.username
        db.session.add(assignment)
        db.session.commit()

        Audit().auditlog_new_post('assignment', original_data=assignment.to_dict(),
                                  record_name=assignment.__tablename__)
        flash(_('New assignment is now requested!'))

        return redirect(url_for('main.index'))

    else:

        return render_template('assignment.html', title=_('Add Assignment'),
                               form=form)


@bp.route('/assignment/edit/', methods=['GET', 'POST'])
@login_required
def assignment_edit():

    assignmentid = request.args.get('assignment')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'delete' in request.form:
        return redirect(url_for('main.assignment_delete', assignment=assignmentid))
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='assignment', module_id=assignmentid))

    assignment = Assignment.query.get(assignmentid)
    original_data = assignment.to_dict()

    if assignment is None:
        render_template('service.html', title=_('assignment is not defined'))

    print(f"logged in user {current_user.username}")
    requestor = User.query.filter_by(
        username=current_user.username).first_or_404()
    if requestor is None:
        flash('logged in user is required')
        return redirect(request.referrer)

    form = AssignmentForm(formdata=request.form, obj=assignment)

    if request.method == 'POST' and form.validate_on_submit():

        assignment.comment = form.comment.data
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        assignment.comment = form.comment.data
        assignment.start = form.start.data
        assignment.stop = form.stop.data
        assignment.user = user
        assignment.role = role
        assignment.status = "requested"
        assignment.request_ts = datetime.now()
        print(f'requestor: {requestor.username}')
        assignment.requestor = requestor.username
        db.session.commit()

        Audit().auditlog_update_post('assignment', original_data=original_data,
                                     updated_data=assignment.to_dict(),
                                     record_name=assignment.__tablename__)
        flash(_('Your changes have been saved.'))

        return redirect(url_for('main.index'))

    else:
        form.user.data = assignment.user_id
        form.role.data = assignment.role_id
        return render_template('assignment.html', title=_('Edit assignment'),
                               form=form)


@bp.route('/assignment/approve/', methods=['GET', 'POST'])
@login_required
def assignment_approve():

    assignmentid = request.args.get('assignment')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='assignment',
                                module_id=assignmentid))

    assignment = Assignment.query.get(assignmentid)

    if assignment is None:
        flash(_('assignment is not found'))
        return redirect(url_for('main.index'))

    if 'view_role' in request.form:
        return redirect(url_for('main.role_view', role=assignment.role.id))
    if 'view_user' in request.form:
        return redirect(url_for('main.user', username=assignment.user.username))

    original_data = assignment.to_dict()

# todo add admin check

    form = ApproveAssignmentForm(formdata=request.form, obj=assignment)

    if request.method == 'POST' and form.validate_on_submit():

        if 'deny' in request.form:
            assignment.status = "denied-by-approver"
            assignment.approver = current_user.username
            db.session.commit()
            flash(
                f"Pending Assignment to role: {assignment.role.name} for: {assignment.user.username} was denied")
        elif 'postpone' in request.form:
            assignment.status = "postponed-by-approver"
            assignment.approver = current_user.username
            flash(
                f"Pending Assignment to role: {assignment.role.name} for: {assignment.user.username} was postponed")

        elif 'approve' in request.form:
            assignment.status = "approved"
            assignment.approver = current_user.username
            db.session.commit()
            flash(
                f"Assignment to role: {assignment.role.name} for: {assignment.user.username} was approved")
            for r in assignment.role.resources:
                from app.modules.access.models import Access
                access = Access(user_id=assignment.user_id, resource_id=r.id,
                                status="requested", request_ts=datetime.now(),
                                start=datetime.now(),
                                stop=datetime.now() + relativedelta(years=1),
                                assignment_id=assignment.id,
                                approver=assignment.approver,
                                approve_ts=datetime.now(),
                                requestor=assignment.requestor
                                )
                db.session.add(access)
                db.session.commit()

        Audit().auditlog_update_post(module='assignment', original_data=original_data,
                                     updated_data=assignment.to_dict(),
                                     record_name=assignment.__tablename__)
        return redirect(url_for('main.index'))

    else:
        form.user.data = assignment.user.username
        form.role.data = assignment.role.name
        return render_template('assignment.html', title=_('Approved assignment'),
                               form=form)


@bp.route('/assignment/list/', methods=['GET', 'POST'])
@login_required
def assignment_list():

    page = request.args.get('page', 1, type=int)
    pending = request.args.get('pending', 0, type=int)

    ac = None
    if pending:
        ac = Assignment.query.filter_by(status="requested").paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        ac = Assignment.query.order_by(Assignment.id).paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.assignment_list', page=ac.next_num) \
        if ac.has_next else None
    prev_url = url_for('main.assignment_list', page=ac.prev_num) \
        if ac.has_prev else None

    return render_template('assignment.html', title=_('List assignment'),
                           assignments=ac.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/assignment/delete/', methods=['GET', 'POST'])
@login_required
def assignment_delete():

    assignmentid = request.args.get('assignment')
    assignment = Assignment.query.get(assignmentid)

    if assignment is None:
        flash(_('assignment was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    # check if pyraadmin
    deleted_msg = f'assignment deleted for: {assignment.user.username} to: {assignment.role.name}\n'
    flash(deleted_msg)
    db.session.delete(assignment)
    db.session.commit()

    Audit().auditlog_delete_post('access', data=assignment.to_dict(),
                                 record_name=assignment.__class__.__name__.lower())

    return redirect(url_for('main.index'))
