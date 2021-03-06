from flask import Blueprint, request, session, render_template, redirect, url_for, g
import models.users.errors as UserErrors
from models.users.email_confirmation import EmailConfirmation
from models.users.forms import LoginForm, RegisterForm, AddFriendForm
import logging

from models.users.friend_request import FriendRequest
from models.users.notification import Notification
from models.users.user import User
from models.users.decorators import requires_access_level
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

__author__ = 'jslvtr'

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if g.user:
        return redirect(url_for('.profile'))
    log.info("Called /login endpoint, creating form")
    form = LoginForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to log user in.")
        try:
            user = User.login(email=form.email.data,
                              password=form.password.data)
            session['user_id'] = user.id
            log.info("User logged in and e-mail in session.")
        except UserErrors.UserError as e:
            log.warn("User error with message '{}', redirecting to login".format(e.message))
            return redirect(url_for('.login', message=e.message))
        log.info("User logged in, redirecting to profile.")
        return redirect(url_for('.profile'))
    log.info("Form not valid or this is GET request, presenting users/login.html template")
    return render_template('users/login.html', form=form, bg="#3498DB")


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if g.user:
        return redirect(url_for('.profile'))
    log.info("Called /register endpoint, creating form")
    form = RegisterForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to log user in.")
        try:
            user = User.register(email=form.email.data,
                                 password=form.password.data,
                                 confirm_email=True)
            log.info("User logged in and e-mail in session.")
        except UserErrors.UserError as e:
            log.warn("User error with message '{}', redirecting to login".format(e.message))
            return redirect(url_for('index', message=e.message))
        log.info("User logged in, redirecting to e-mail confirmation page.")
        return redirect(url_for('.confirm_view'))
    log.info("Form not valid or this is GET request, presenting users/register.html template")
    return render_template('users/register.html', form=form, bg="#3498DB")


@bp.route('/profile')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def profile():
    active_module = g.user.get_current_active_module()
    if active_module:
        return render_template('users/profile2.html', active_module=active_module,
                               completed_lectures=active_module.completed_lectures.all(),
                               unlocked_lectures=active_module.bought_lectures.all())
    else:
        return redirect(url_for('modules.public_modules'))


@bp.route('/logout')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def logout():
    if session.get('user_id'):
        session.clear()
        return redirect(url_for('index', warn="You have been logged out."))
    else:
        return redirect(url_for('index'))


@bp.route('/add', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def add_friend_form():
    log.info("Called /add endpoint, creating form")
    form = AddFriendForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to add friend.")
        try:
            friend_request = FriendRequest(user=g.user,
                                           new_friend=User.query.filter(User.email == form.email.data.lower()).first())
            friend_request.notify_new_friend()
            friend_request.save_to_db()
            log.info("Put request through and notified friend.")
        except UserErrors.UserError as e:
            log.warn("User error with message '{}', redirecting to login".format(e.message))
            return redirect(url_for('index', message=e.message))
        log.info("Added friend, redirecting to profile.")
        return redirect(url_for('.profile', message="Added user {} as friend.".format(form.email.data)))
    log.info("Form not valid or this is GET request, presenting users/add_friend.html template")
    return render_template('users/add_friend.html', form=form)


@bp.route('/confirm/<string:friend_request_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def confirm_friend_request(friend_request_id):
    friend_request = FriendRequest.query.get(friend_request_id)
    if friend_request:
        friend_email = friend_request.user.email
        if friend_request.new_friend.id == g.user.id:
            if friend_request.new_friend not in friend_request.user.friends:
                friend_request.user.friends.append(friend_request.new_friend)
                friend_request.new_friend.friends.append(friend_request.user)
                friend_request.user.save_to_db()
                friend_request.new_friend.save_to_db()
                friend_request.remove_from_db()
                return redirect(url_for('.profile',
                                        message="You have added {} to your friends.".format(friend_email)))
            friend_request.remove_from_db()
            return redirect(url_for('.profile',
                                    message="{} is already your friend!".format(friend_email)))
        friend_request.remove_from_db()
        return redirect(url_for('.profile',
                                warn="You are not part of this friend request!".format(friend_email)))
    return redirect(url_for('.profile', warn="Page not found, redirected you to your profile."))


@bp.route('/view/<string:user_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def view(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('users/view.html', user=user)
    return redirect(url_for('.profile', warn="The user you tried to view does not exist."))


@bp.route('/notifications')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def notifications():
    g.user.read_notifications()
    ordered_notifications = g.user.notifications.order_by(Notification.id.desc())
    return render_template('users/notifications.html',
                           notifications=ordered_notifications.filter(Notification.type != "challenge"),
                           challenges=ordered_notifications.filter(Notification.type == "challenge"))


@bp.route('/notifications/delete/<int:notification_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def delete_notification(notification_id):
    try:
        g.user.delete_notification(notification_id)
    except UserErrors.NotNotificationOwnerException as e:
        return redirect(url_for('.notifications', warn=e.message))
    return redirect(url_for('.notifications', message="Notification deleted."))


@bp.route('/notifications/clear-all')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def clear_all():
    g.user.delete_notifications_except_challenges()
    return redirect(url_for('.notifications', message="Cleared all notifications."))


@bp.route('/confirm')
def confirm_view():
    return render_template('users/confirm.html', bg="#3498DB")


@bp.route('/confirm_user/<string:confirmation_id>')
def confirm(confirmation_id):
    confirmation = EmailConfirmation.query.filter(EmailConfirmation.uuid == confirmation_id).first()
    confirmation.confirm()
    return redirect(url_for('.login', message="Thank you for confirming your e-mail. You can log in now."))
