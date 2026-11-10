import secrets
import re

from sqlalchemy.exc import IntegrityError
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Response,
)
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from . import db
from .models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _create_demo_user() -> User:
    """Create an anonymous participant account without personal data."""
    for _ in range(10):
        participant_id = str(secrets.randbelow(900_000_000) + 100_000_000)
        user = User(email=f'demo-{participant_id}@demo.invalid')
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(email=user.email).first() is not None:
                continue
            raise
        else:
            return user

    raise RuntimeError(
        'Es konnte keine eindeutige Teilnahme-ID erzeugt werden.'
    )


def _find_demo_user(participant_id: str) -> User | None:
    """Find a demo user from the anonymous participant ID."""
    normalized_id = participant_id.strip().upper()
    if normalized_id.startswith('DEMO-'):
        normalized_id = normalized_id[5:]
    # Keep legacy IDs restorable while all new IDs use nine digits.
    if not re.fullmatch(r'(?:[0-9]{9}|[0-9A-F]{16})', normalized_id):
        return None
    return User.query.filter_by(
        email=f'demo-{normalized_id}@demo.invalid'
    ).first()


def _participant_id(user: User) -> str:
    """Return the user-facing nine-digit participant ID."""
    return user.email.split('@', 1)[0].removeprefix('demo-')


@auth_bp.route('/download-participant-id')
@login_required
def download_participant_id():
    participant_id = _participant_id(current_user)
    if not re.fullmatch(r'\d{9}', participant_id):
        return Response('Teilnehmer-ID nicht verfügbar.', status=404)
    response = Response(
        f'Teilnahme-ID: {participant_id}\n',
        mimetype='text/plain',
    )
    response.headers['Content-Disposition'] = (
        f'attachment; filename="teilnahme-id-{participant_id}.txt"'
    )
    return response


def _redirect_after_login():
    next_page = request.args.get('next')
    if not next_page or urlparse(next_page).netloc != '':
        next_page = url_for('main.home')
    return redirect(next_page)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        if request.form.get('action') == 'restore':
            participant_id = request.form.get('participant_id', '')
            user = _find_demo_user(participant_id)
            if user is None:
                flash(
                    'Die Teilnehmer-ID wurde nicht gefunden. Bitte prüfe deine Eingabe.',
                    'danger',
                )
                return render_template('auth/login.html')
            login_user(user)
            flash('Deine bestehende Teilnahme wurde geöffnet.', 'success')
            return _redirect_after_login()

        user = _create_demo_user()
        login_user(user)
        flash(
            f'Deine Teilnehmer-ID für die Umfrage: {_participant_id(user)}',
            'info',
        )
        return render_template(
            'auth/participant_started.html',
            download_url=url_for('auth.download_participant_id'),
            next_url=_redirect_after_login().location,
        )
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
