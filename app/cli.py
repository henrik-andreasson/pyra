from flask import render_template, current_app
import click
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
from sqlalchemy import func
import time
from app import db
from app.modules.access.models import Access
from flask_babel import _


def register(app):
    @app.cli.group()
    def chat():
        """chat commands."""
        pass

    @chat.command()
    @click.argument('start')
    @click.argument('stop')
    def send(start, stop):
        """send expiring access chat remninders."""
        if current_app.config['ROCKET_ENABLED'] != 1:
            print("rocket sending is disabled %s" %
                  current_app.config['ROCKET_ENABLED'])
            return

        print("start: %s stop: %s" % (start, stop))

        access = Access.query.filter(func.datetime(Access.stop) > start,
                                     func.datetime(Access.stop) < stop).all()

        rocket = RocketChat(current_app.config['ROCKET_USER'],
                            current_app.config['ROCKET_PASS'],
                            server_url=current_app.config['ROCKET_URL'])

        for a in access:
            stopdate = a.stop.strftime("%Y-%m-%d")
            msg = f'''Access for: @{a.user.username} \
                    to: {a.role.name} \
                    expires at: {stopdate} \
                    mgr: @{a.role.service.manager.username} \
                    please act on this as needed'''

            pprint(rocket.chat_post_message(msg, channel=current_app.
                                            config['ROCKET_CHANNEL']).json())
            time.sleep(1)

    @app.cli.group()
    def mail():
        """mail commands."""
        pass

    @mail.command()
    @click.argument('start')
    @click.argument('stop')
    def mailsend(start, stop):
        """send expiring access today."""
        print("start: %s stop: %s" % (start, stop))
        if current_app.config['MAIL_ENABLED'] is False:
            print("mail sending is disabled")
            return

        access = Access.query.filter(func.datetime(Access.stop) > start,
                                     func.datetime(Access.stop) < stop).all()

        from app.email import send_email

        for a in access:
            stopdate = a.stop.strftime("%Y-%m-%d")

            send_email(f'[PYRA] Role: {a.role.name} is expiring at {stopdate}',
                       sender=current_app.config['MAIL_DEFAULT_SENDER'],
                       recipients=[a.user.email],
                       text_body=render_template('email/expiring_access.txt',
                                                 access=a),
                       html_body=render_template('email/expiring_access.html',
                                                 access=a))

    @app.cli.group()
    def user():
        """user commands."""
        pass

    @user.command()
    @click.argument('username')
    @click.argument('password')
    @click.argument('email')
    def new(username, password, email):
        """create new user."""
        from app.main.models import User
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    @user.command()
    @click.argument('username')
    @click.argument('password')
    def passwd(username, password):
        """set password user."""
        from app.main.models import User
        user = User.query.filter_by(username=username).first()
        if user is None:
            print("User not found")
        else:
            user.set_password(password)
            db.session.commit()

    @user.command()
    @click.argument('username')
    @click.argument('role')
    def role(username, role):
        """set user role to user or admin."""
        from app.main.models import User
        user = User.query.filter_by(username=username).first()
        if user is None:
            print("User not found")
        else:
            if role in ['user', 'admin']:
                user.set_role(role)
                db.session.commit()
                print(f'role: {role} set for user')
            else:
                print('Not supported role, user or admin only')

    @user.command()
    def list():
        """list users"""
        from app.main.models import User
        users = User.query.all()
        for u in users:
            print(f'username: {u.username} email: {u.email} role: {u.role}')
            db.session.commit()
