import os
import click
import unittest

from flask_migrate import Migrate

from app import create_app, db
from app.models import User, EmailSent


app = create_app(
    os.getenv('FLASK_CONFIG') or 'production'
)

migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        EmailSent=EmailSent
    )


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Executa os testes de unidade."""

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(
            test_names
        )
    else:
        tests = unittest.TestLoader().discover('tests')

    result = unittest.TextTestRunner(
        verbosity=2
    ).run(tests)

    if not result.wasSuccessful():
        raise click.ClickException(
            'Um ou mais testes falharam.'
        )