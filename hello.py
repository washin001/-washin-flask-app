from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Washington_PT303755X_Aula050'


class NameForm(FlaskForm):
    name = StringField(
        'What is your name?',
        validators=[DataRequired()]
    )

    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        old_name = session.get('name')

        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')

        session['name'] = form.name.data

        return redirect(url_for('index'))

    return render_template(
        'index.html',
        form=form,
        name=session.get('name')
    )


@app.route('/identificacao')
def identificacao():

    return render_template(
        'identificacao.html',
        nome='Washington',
        prontuario='PT303755X',
        professor='Fabio Teixeira'
    )


@app.route('/contextorequisicao')
def contexto_requisicao():

    return render_template('contexto.html')


if __name__ == '__main__':
    app.run()