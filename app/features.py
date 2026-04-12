from flask import Blueprint, render_template
from flask_login import login_required, current_user

features_bp = Blueprint('features', __name__, url_prefix='/features')


@features_bp.route('/dashboard')
@login_required
def dashboard():
    """Features dashboard page."""
    return render_template('features/dashboard.html')
