from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave-secreta-washington'


def tempo_decorrido(delta):
    """Retorna um texto tipo 'an hour', '5 minutes', 'a day' a partir de um timedelta."""
    segundos = int(delta.total_seconds())

    if segundos < 60:
        return "a few seconds"

    minutos = segundos // 60
    if minutos == 1:
        return "a minute"
    if minutos < 60:
        return f"{minutos} minutes"

    horas = minutos // 60
    if horas == 1:
        return "an hour"
    if horas < 24:
        return f"{horas} hours"

    dias = horas // 24
    if dias == 1:
        return "a day"
    return f"{dias} days"


@app.route('/', methods=['GET', 'POST'])
def home():

    nome = None
    sobrenome = None
    instituicao = None
    disciplina = None

    if request.method == 'POST':
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        instituicao = request.form.get('instituicao')
        disciplina = request.form.get('disciplina')

    agora = datetime.now()
    horario = agora.strftime('%B %d, %Y %-I:%M %p')

    # Guarda/lê o horário da última visita na sessão do usuário
    ultima_visita = session.get('ultima_visita')
    session['ultima_visita'] = agora.isoformat()

    mensagem_tempo = ''
    if ultima_visita:
        delta = agora - datetime.fromisoformat(ultima_visita)
        mensagem_tempo = tempo_decorrido(delta)

    return render_template(
        'index.html',
        nome=nome,
        sobrenome=sobrenome,
        instituicao=instituicao,
        disciplina=disciplina,
        ip=request.remote_addr,
        host=request.host,
        horario=horario,
        mensagem_tempo=mensagem_tempo
    )


@app.route('/login', methods=['GET', 'POST'])
def login():

    mensagem = ''

    if request.method == 'POST':

        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == 'admin' and senha == '1234':
            mensagem = 'Login realizado com sucesso!'
        else:
            mensagem = 'Usuário ou senha inválidos.'

    return render_template(
        'login.html',
        mensagem=mensagem
    )


@app.route('/identificacao')
def identificacao():
    return render_template('identificacao.html')


@app.route('/contexto')
def contexto():
    return render_template('contexto.html')


if __name__ == '__main__':
    app.run(debug=True)