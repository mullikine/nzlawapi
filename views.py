import sys
import hmac
from hashlib import sha256
from flask import Blueprint, render_template, request, redirect, current_app, session
from security.auth import require_auth
Base = Blueprint('base', __name__, template_folder='templates')


@Base.route('/login')
def login():
    args = request.args
    user_id = args.get('user_id')
    user_name = args.get('name')
    timestamp = args.get('timestamp')
    provided_code = args.get('code')

    if user_id is None or timestamp is None or user_name is None or provided_code is None:
        return redirect(current_app.config.get('USERS_LOGIN_URL'))

    message = str(user_id) + str(user_name) + str(timestamp)
    hash_obj = hmac.new(key=current_app.config.get('SSO_SHARED_SECRET'), msg=message, digestmod=sha256)
    calculated_code = hash_obj.hexdigest()

    if provided_code != calculated_code:
        return redirect(current_app.config.get('USERS_LOGIN_URL'))

    session['user_id'] = user_id
    session['user_name'] = user_name

    return redirect('/')


@Base.route('/logout')
def logout():
    del session['user_id']
    return redirect('/')


@Base.route('/')
@Base.route('/open_article/<sub>')
@Base.route('/open_article/<sub>/<subsub>')
@require_auth
def browser(**args):
    return render_template('browser.html')
