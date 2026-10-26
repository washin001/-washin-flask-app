from flask import (
    render_template,
    session,
    redirect,
    url_for,
    flash
)

from . import main
from .forms import NameForm

from .. import db
from ..email import send_email
from ..models import User, Role, EmailSent, sao_paulo_now


@main.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        username = form.name.data.strip()
        notification_email = form.email.data.strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None:

            default_role = Role.query.filter_by(
                name='User'
            ).first()

            user = User(
                username=username,
                role=default_role
            )

            db.session.add(user)
            db.session.commit()

            session['known'] = False

            email_ok = send_email(
                user,
                notification_email
            )

            if email_ok:

                flash(
                    'E-mail enviado para o Administrador do sistema, '
                    'notificando o cadastro de um novo usuário.'
                )

            else:

                flash(
                    'Usuário cadastrado, mas o envio do e-mail falhou. '
                    'Verifique os logs e os destinatários autorizados.'
                )

        else:

            session['known'] = True

            flash(
                'Esse usuário já está cadastrado.'
            )

        session['name'] = username

        return redirect(url_for('.index'))

    users = User.query.order_by(
        User.id
    ).all()

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        known=session.get('known', False),
        users=users,
        users_count=User.query.count(),
        current_time=sao_paulo_now()
    )


@main.route('/emailsEnviados')
def emails_enviados():

    emails = EmailSent.query.order_by(
        EmailSent.sent_at.desc()
    ).all()

    return render_template(
        'emailsEnviados.html',
        emails=emails
    )