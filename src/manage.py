import json

import click as click
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


@click.group()
def cli():
    """
    This script is for logging into the application

    Use the command then the option

    Examples: start -c config/config.json
              create-db -db postgres -p postgres -h localhost -u postgres


    """
    pass


@cli.command()
@click.option('--dbname',
              '-db',
              default='postgres',
              help='Database name')
@click.option('--password',
              '-p',
              default='postgres',
              help='Password')
@click.option('--host',
              '-h',
              default='localhost',
              help='Host')
@click.option('--user',
              '-u',
              default='postgres',
              help='Username')
def create_db(dbname, password, user, host):
    """
    Database creation |
    Read more create-db --help
    """
    conn = psycopg2.connect(dbname=dbname,
                            user=user,
                            password=password,
                            host=host
                            )  # type: connection
    config = json.load(open('config/config.json'))['db']['connect']
    user = config['user']
    dbname = config['dbname']
    password = config['password']
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("create user {} with encrypted password %s;".format(user),
                   (password,))
    cursor.execute('CREATE database {} WITH owner {};'.format(dbname, user))
    conn.commit()
    cursor.close()
    conn.close()
