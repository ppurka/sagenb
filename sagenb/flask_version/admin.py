import os
from flask import Module, url_for, render_template, request, session, redirect, g, current_app
from decorators import login_required, admin_required, with_lock
from flask.ext.babel import Babel, gettext, ngettext, lazy_gettext
_ = gettext
from sagenb.notebook.misc import encode_response

admin = Module('sagenb.flask_version.admin')

def random_password(length=8):
    from random import choice
    import string
    chara = string.letters + string.digits
    return ''.join([choice(chara) for i in range(length)])

@admin.route('/manage_users')
@admin_required
@with_lock
def users(reset=None):
    from sagenb.misc.misc import SAGE_VERSION
    template_dict = {}
    template_dict['sage_version'] = SAGE_VERSION
    if reset:
        from random import choice
        import string
        chara = string.letters + string.digits
        password = ''.join([choice(chara) for i in range(8)])
        try:
            U = g.notebook.user_manager().user(reset)
            g.notebook.user_manager().set_password(reset, password)
        except KeyError:
            pass
        template_dict['reset'] = [reset, password]

    template_dict['number_of_users'] = len(g.notebook.user_manager().valid_login_names()) if len(g.notebook.user_manager().valid_login_names()) > 1 else None
    users = sorted(g.notebook.user_manager().valid_login_names())
    del users[users.index('admin')]
    template_dict['users'] = [g.notebook.user_manager().user(username) for username in users]
    return render_template(os.path.join('html', 'settings', 'manage_users.html'), **template_dict)

@admin.route('/reset_user_password', methods = ['POST'])
@admin_required
@with_lock
def reset_user_password():
    user = request.values['username']
    password = random_password()
    try:
        # U = g.notebook.user_manager().user(user)
        g.notebook.user_manager().set_password(user, password)
    except KeyError:
        pass

    return encode_response({
        'message': _('The temporary password for the new user <strong>%(username)s</strong> is <strong>%(password)s</strong>',
                          username=user, password=password)
    })

@admin.route('/suspend_user', methods = ['POST'])
@admin_required
@with_lock
def suspend_user():
    user = request.values['username']
    try:
        U = g.notebook.user_manager().user(user)
        U.set_suspension()
    except KeyError:
        pass

    return encode_response({
        'message': _('User <strong>%(username)s</strong> has been suspended/unsuspended.', username=user)
    })

@admin.route('/add_user', methods = ['POST'])
@admin_required
@with_lock
def add_user():
    from sagenb.notebook.misc import is_valid_username
    from sagenb.misc.misc import SAGE_VERSION
    template_dict = {'admin': g.notebook.user_manager().user(g.username).is_admin(),
            'username': g.username, 'sage_version': SAGE_VERSION}
    if 'username' in request.values:
        if request.values['cancel']:
            return redirect(url_for('users'))
        username = request.values['username']
        if not is_valid_username(username):
            return encode_response({
                'error': _('<strong>Invalid username!</strong>')
            })

        password = random_password()
        if username in g.notebook.user_manager().usernames():
            return encode_response({
                'error': _('The username <strong>%(username)s</strong> is already taken!', username=username)
            })
        g.notebook.user_manager().add_user(username, password, '', force=True)
        return encode_response({
            'message': _('The temporary password for the new user <strong>%(username)s</strong> is <strong>%(password)s</strong>',
                          username=username, password=password)
        })
    else:
        return render_template(os.path.join('html', 'settings', 'admin_add_user.html'),
                               **template_dict)

@admin.route('/notebooksettings', methods=['GET', 'POST'])
@admin_required
@with_lock
def notebook_settings():
    from sagenb.misc.misc import SAGE_VERSION
    updated = {}
    if 'form' in request.values:
        updated = g.notebook.conf().update_from_form(request.values)

    # Make changes to the default language used
    if 'default_language' in request.values:
        from flask.ext.babel import refresh
        refresh()
        current_app.config['BABEL_DEFAULT_LOCALE'] = request.values['default_language']

    template_dict = {}
    template_dict['sage_version'] = SAGE_VERSION
    template_dict['auto_table'] = g.notebook.conf().html_table(updated)
    template_dict['admin'] = g.notebook.user_manager().user(g.username).is_admin()
    template_dict['username'] = g.username

    return render_template(os.path.join('html', 'settings', 'notebook_settings.html'),
                           **template_dict)

