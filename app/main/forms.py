from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField

from wtforms.validators import DataRequired, Regexp


class NameForm(FlaskForm):

    name = StringField(
        'Qual é o seu nome?',
        validators=[DataRequired()]
    )

    email = StringField(
        'Qual é o seu email (Envio de notificação do novo usuário)?',
        validators=[
            DataRequired(),
            Regexp(
                r'^[^@\s]+@[^@\s]+\.[^@\s]+$',
                message='Digite um endereço de e-mail válido.'
            )
        ]
    )

    submit = SubmitField('Submit')