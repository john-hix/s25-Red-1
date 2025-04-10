"""Blueprint for the CueCode Dev Portal"""
import os
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from functools import wraps

#import uuid
#from common.models import CuecodeConfig, OpenAPISpec
#from common.models.base import db


def login_required(f):
    """
    function to check if user is logged in in session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def upload_config(content, filename):
    logging.info(f"Beginning to process '{filename}' ({len(content)} bytes)")
    if filename.lower().endswith(".json"):
        import time
        time.sleep(5)
        error = "" #TODO: config validation
        # cuecode_config = CuecodeConfig(config_is_finished=False, is_live=False)
        # db.session.add(cuecode_config)
        # db.session.commit()

        # openapi_spec = OpenAPISpec(
        #     openapi_spec_id=uuid.uuid4(),
        #     spec_text=content,
        #     file_name=filename,
        # )
        # db.session.add(openapi_spec)
        # db.session.commit()
        logging.info(f"Successfully saved spec '{filename}' to database.")
    else:
        error = "Invalid filetype"
    return error

class Portal:
    def __init__(self, import_name):
        self.app = Flask(import_name, template_folder='templates')
        self.app.secret_key = os.urandom(24) #TODO: load from an .env
        self.register_routes()
    def register_routes(self):
        """Registers the URL routes for portal"""

        @self.app.route('/')
        def index():
            if 'logged_in' in session:
                return redirect(url_for('account'))
            return redirect(url_for('login'))

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            # check if already logged in
            if 'logged_in' in session:
                 return redirect(url_for('account'))

            if request.method == 'POST':
                username = request.form.get('username', 'Guest') #default to guest
                session['logged_in'] = True
                session['username'] = username
                flash(f'Successful login to {username}', 'success')
                logging.info(f"Logged in user '{session.get('username', 'ERROR')}'")
                return redirect(url_for('account'))

            return render_template('login.html')

        @self.app.route('/account')
        @login_required
        def account():
            username = session.get('username', 'ERROR')
            return render_template('account.html', username=username)

        @self.app.route('/logout')
        @login_required
        def logout():
            """Logs the user out by clearing the session."""
            session.pop('logged_in', None)
            session.pop('username', None)
            flash('Succesfully logged out', 'info')
            return redirect(url_for('login'))

        @self.app.route('/account/reset', methods=['POST'])
        @login_required
        def reset_password():
            """password reset functionality"""
            flash('Successfully reset password', 'info')
            logging.info(f"Successful password reset for '{session.get('username', 'ERROR')}'")
            return redirect(url_for('account'))

        @self.app.route('/upload', methods=['POST'])
        @login_required
        def upload_openapi():
            if 'openapi_spec' not in request.files:
                flash('Missing file in request', 'danger')
                return redirect(url_for('account'))

            file = request.files['openapi_spec']

            if file.filename == '':
                flash('Missing configuration', 'warning')
                return redirect(url_for('account'))

            if file:
                filename = file.filename
                content = file.read().decode('utf-8')
                username = session.get('username', 'ERROR')
                logging.info(f"Processing '{filename}' config upload for {username}")
                response = upload_config(content, filename)
                if not response: # Empty string or None means success
                    flash(f"Successfully processed and saved '{filename}'.", 'success')
                    logging.info(f"Processing successful for '{filename}' for user '{username}'.")
                else:
                    flash(f"Error processing '{filename}': {response}", 'danger')
                    logging.error(f"Processing failed for '{filename}' for user '{username}': {response}")
                return redirect(url_for('account'))

            return redirect(url_for('account'))

    def run(self, host='localhost', port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)

portal = Portal(__name__)
portal.run(debug=True) #TODO: make variable?

