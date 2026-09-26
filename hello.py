import os

import requests
from dotenv import load_dotenv

from flask import Flask, render_template, session, redirect, url_for

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# ============================================================
# CONFIGURAÇÕES
# ============================================================

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(
    os.path.join(basedir, '.env')
)


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ============================================================
# EXTENSÕES
# ============================================================

bootstrap = Bootstrap(app)

moment = Moment(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ============================================================
# MODELO ROLE
# ============================================================

class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(64),
        unique=True
    )

    users = db.relationship(
        'User',
        backref='role',
        lazy='dynamic'
    )

    def __repr__(self):

        return '<Role %r>' % self.name


# ============================================================
# MODELO USER
# ============================================================

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

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id')
    )

    def __repr__(self):

        return '<User %r>' % self.username


# ============================================================
# FORMULÁRIO
# ============================================================

class NameForm(FlaskForm):

    name = StringField(
        'What is your name?',
        validators=[DataRequired()]
    )

    role = SelectField(
        'Role?',
        coerce=int,
        validators=[DataRequired()]
    )

    email_admin = BooleanField(
        'Enviar por e-mail para flaskaulasweb@zohomail.com'
    )

    submit = SubmitField(
        'Submit'
    )


# ============================================================
# CONTEXTO DO FLASK SHELL
# ============================================================

@app.shell_context_processor
def make_shell_context():

    return dict(
        db=db,
        User=User,
        Role=Role
    )


# ============================================================
# ENVIO DE E-MAIL PELO MAILGUN
# ============================================================

def send_email(user, enviar_admin=False):

    api_url = os.getenv('API_URL')

    api_key = os.getenv('API_KEY')

    api_from = os.getenv('API_FROM')

    admin_email = os.getenv('FLASKY_ADMIN')

    student_email = os.getenv('FLASKY_STUDENT')


    # --------------------------------------------------------
    # DESTINATÁRIOS
    # --------------------------------------------------------

    recipients = []


    # O e-mail institucional sempre recebe.

    if student_email:

        recipients.append(student_email)


    # O e-mail do professor/admin só recebe
    # quando o checkbox estiver marcado.

    if enviar_admin and admin_email:

        recipients.append(admin_email)


    # --------------------------------------------------------
    # VALIDAÇÕES
    # --------------------------------------------------------

    if not api_url:

        print(
            'ERRO: API_URL não configurada.'
        )

        return


    if not api_key:

        print(
            'ERRO: API_KEY não configurada.'
        )

        return


    if not api_from:

        print(
            'ERRO: API_FROM não configurada.'
        )

        return


    if not recipients:

        print(
            'ERRO: nenhum destinatário configurado.'
        )

        return


    # --------------------------------------------------------
    # ENVIO
    # --------------------------------------------------------

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

                'subject':
                    '[Flask] User Cadastrado no Banco',

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

            print(
                'E-mail enviado com sucesso.'
            )

            print(
                'Destinatários:',
                recipients
            )

        else:

            print(
                'ERRO AO ENVIAR E-MAIL:',
                response.status_code,
                response.text
            )


    except Exception as e:

        print(
            'ERRO DE CONEXÃO COM O MAILGUN:',
            e
        )


# ============================================================
# ERRO 404
# ============================================================

@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        '404.html'
    ), 404


# ============================================================
# ERRO 500
# ============================================================

@app.errorhandler(500)
def internal_server_error(e):

    return render_template(
        '500.html'
    ), 500


# ============================================================
# HOME
# ============================================================

@app.route(
    '/',
    methods=['GET', 'POST']
)
def index():

    form = NameForm()


    # --------------------------------------------------------
    # CARREGA AS FUNÇÕES DO BANCO
    # --------------------------------------------------------

    roles = Role.query.order_by(
        Role.id
    ).all()


    form.role.choices = [

        (
            role.id,
            role.name
        )

        for role in roles

    ]


    # --------------------------------------------------------
    # CADASTRO
    # --------------------------------------------------------

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.name.data
        ).first()


        selected_role = db.session.get(
            Role,
            form.role.data
        )


        # ====================================================
        # NOVO USUÁRIO
        # ====================================================

        if user is None:

            user = User(

                username=form.name.data,

                role=selected_role

            )


            db.session.add(user)

            db.session.commit()


            session['known'] = False


            # ------------------------------------------------
            # ENVIO DO E-MAIL
            # ------------------------------------------------

            send_email(

                user,

                enviar_admin=form.email_admin.data

            )


        # ====================================================
        # USUÁRIO JÁ EXISTENTE
        # ====================================================

        else:

            user.role = selected_role

            db.session.commit()

            session['known'] = True


        session['name'] = form.name.data


        return redirect(
            url_for('index')
        )


    # --------------------------------------------------------
    # DADOS DA PÁGINA
    # --------------------------------------------------------

    users = User.query.order_by(
        User.id
    ).all()


    users_count = User.query.count()


    roles_count = Role.query.count()


    grouped_users = {}


    for role in roles:

        grouped_users[role.name] = (

            role.users

            .order_by(
                User.username
            )

            .all()

        )


    return render_template(

        'index.html',

        form=form,

        name=session.get('name'),

        known=session.get(
            'known',
            False
        ),

        users=users,

        roles=roles,

        grouped_users=grouped_users,

        users_count=users_count,

        roles_count=roles_count

    )