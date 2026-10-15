from flask import render_template, session, redirect, url_for, flash

from . import main
from .forms import NameForm

from .. import db
from ..email import send_email
from ..models import User, EmailSent


@main.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        username = form.name.data.strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None:

            user = User(username=username)

            db.session.add(user)
            db.session.commit()

            session['known'] = False

            # Envia para o aluno e para o administrador.
            email_ok = send_email(
                user,
                enviar_admin=True
            )

            if email_ok:
                flash(
                    'E-mail enviado para os destinatários configurados.'
                )
            else:
                flash(
                    'Usuário cadastrado, mas houve uma falha no envio '
                    'do e-mail. Confira os logs da aplicação.'
                )

        else:

            session['known'] = True

        session['name'] = username

        return redirect(url_for('.index'))

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        known=session.get('known', False)
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