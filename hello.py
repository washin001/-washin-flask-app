import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

from flask import Flask, render_template, session, redirect, url_for

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(
    os.path.join(basedir, '.env')
)


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


SAO_PAULO = ZoneInfo('America/Sao_Paulo')


def agora():
    return datetime.now(SAO_PAULO)


bootstrap = Bootstrap(app)

moment = Moment(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(64),
        unique=True,
        index=True
    )

    def __repr__(self):

        return '<User %r>' % self.username


class EmailSent(db.Model):

    __tablename__ = 'emails_sent'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender = db.Column(
        db.String(128),
        nullable=False
    )

    recipient = db.Column(
        db.Text,
        nullable=False
    )

    subject = db.Column(
        db.String(255),
        nullable=False
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    sent_at = db.Column(
        db.DateTime,
        default=agora,
        nullable=False
    )

    def __repr__(self):

        return '<EmailSent %r>' % self.subject


class NameForm(FlaskForm):

    name = StringField(
        'Qual é o seu nome?',
        validators=[DataRequired()]
    )

    email_admin = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField(
        'Submit'
    )


@app.shell_context_processor
def make_shell_context():

    return dict(
        db=db,
        User=User,
        EmailSent=EmailSent
    )


def send_email(user, enviar_admin=False):

    api_url = os.getenv('API_URL')

    api_key = os.getenv('API_KEY')

    api_from = os.getenv('API_FROM')

    admin_email = os.getenv('FLASKY_ADMIN')

    student_email = os.getenv('FLASKY_STUDENT')


    recipients = []


    if student_email:

        recipients.append(student_email)


    if enviar_admin and admin_email:

        recipients.append(admin_email)


    if not api_url:

        print('ERRO: API_URL não configurada.')

        return False


    if not api_key:

        print('ERRO: API_KEY não configurada.')

        return False


    if not api_from:

        print('ERRO: API_FROM não configurada.')

        return False


    if not recipients:

        print('ERRO: nenhum destinatário configurado.')

        return False


    subject = '[Flask] Novo usuário'


    email_text = (
        'Novo usuário cadastrado: '
        + user.username
        + '\n\n'
        + 'Prontuário: PT303755X'
        + '\n'
        + 'Nome do aluno: WASHINGTON SOUSA'
        + '\n'
        + 'Usuário cadastrado: '
        + user.username
    )


    try:

        response = requests.post(

            api_url,

            auth=(
                'api',
                api_key
            ),

            data={

                'from': api_from,

                'to': recipients,

                'subject': subject,

                'html': render_template(

                    'mail/new_user.html',

                    user=user,

                    prontuario='PT303755X',

                    aluno='WASHINGTON SOUSA'

                )

            },

            timeout=30
        )


        if response.ok:

            print('E-mail enviado com sucesso.')

            print(
                'Destinatários:',
                recipients
            )


            email_sent = EmailSent(

                sender='WASHINGTON SOUSA',

                recipient=', '.join(
                    recipients
                ),

                subject=subject,

                text=email_text,

                sent_at=agora()

            )


            db.session.add(email_sent)

            db.session.commit()


            print(
                'E-mail registrado no banco de dados.'
            )

            return True


        else:

            print(
                'ERRO AO ENVIAR E-MAIL:',
                response.status_code,
                response.text
            )

            return False


    except Exception as e:

        print(
            'ERRO DE CONEXÃO COM O MAILGUN:',
            e
        )

        return False


@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        '404.html'
    ), 404


@app.errorhandler(500)
def internal_server_error(e):

    return render_template(
        '500.html'
    ), 500


@app.route(
    '/',
    methods=['GET', 'POST']
)
def index():

    form = NameForm()


    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.name.data
        ).first()


        if user is None:

            user = User(
                username=form.name.data
            )

            db.session.add(user)

            db.session.commit()

            session['known'] = False


            send_email(

                user,

                enviar_admin=form.email_admin.data

            )


        else:

            session['known'] = True


        session['name'] = form.name.data


        return redirect(
            url_for('index')
        )


    users = User.query.order_by(
        User.id
    ).all()


    users_count = User.query.count()


    return render_template(

        'index.html',

        form=form,

        name=session.get('name'),

        known=session.get(
            'known',
            False
        ),

        users=users,

        users_count=users_count

    )


@app.route(
    '/emailsEnviados'
)
def emails_enviados():

    emails = EmailSent.query.order_by(
        EmailSent.sent_at.desc()
    ).all()


    return render_template(

        'emailsEnviados.html',

        emails=emails

    )
