import requests

from flask import current_app, render_template

from . import db
from .models import EmailSent, sao_paulo_now


def send_email(user, enviar_admin=False):
    api_url = current_app.config.get('API_URL')
    api_key = current_app.config.get('API_KEY')
    api_from = current_app.config.get('API_FROM')

    student_email = current_app.config.get('FLASKY_STUDENT')
    admin_email = current_app.config.get('FLASKY_ADMIN')

    recipients = []

    if student_email:
        recipients.append(student_email)

    if enviar_admin and admin_email:
        recipients.append(admin_email)

    if not api_url or not api_key or not api_from or not recipients:
        current_app.logger.error(
            'Configuração incompleta para envio de e-mail.'
        )
        return False

    subject = '[Flask] Novo usuário'

    email_text = (
        'Novo usuário cadastrado: ' + user.username
        + '\n\nProntuário: PT303755X'
        + '\nNome do aluno: WASHINGTON SOUSA'
        + '\nUsuário cadastrado: ' + user.username
    )

    try:
        response = requests.post(
            api_url,
            auth=('api', api_key),
            data={
                'from': api_from,
                'to': recipients,
                'subject': subject,
                'text': email_text,
                'html': render_template(
                    'mail/new_user.html',
                    user=user,
                    prontuario='PT303755X',
                    aluno='WASHINGTON SOUSA'
                )
            },
            timeout=30
        )

        if not response.ok:
            current_app.logger.error(
                'Erro Mailgun: %s - %s',
                response.status_code,
                response.text
            )
            return False

        email_sent = EmailSent(
            sender='WASHINGTON SOUSA',
            recipient=', '.join(recipients),
            subject=subject,
            text=email_text,
            sent_at=sao_paulo_now()
        )

        db.session.add(email_sent)
        db.session.commit()

        current_app.logger.info(
            'E-mail enviado e registrado no banco.'
        )

        return True

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            'Erro ao enviar ou registrar o e-mail.'
        )
        return False