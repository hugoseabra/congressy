"""
Command to do a database dump using database's native tools.

Originally inspired by http://djangosnippets.org/snippets/823/
"""

import os
import shutil
import subprocess
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Dump database into a file. Only PostgreSQL engine is supported.'
    db_name = None
    debug = None
    compress = None
    engine = None
    db = None
    user = None
    password = None
    host = None
    port = None
    excluded_tables = None
    empty_tables = None
    pgpass = None

    def add_arguments(self, parser):

        parser.add_argument('--destination', dest='backup_directory',
                            default='/tmp/',
                            help='Destination (path) where to place database '
                                 'dump file.'),
        parser.add_argument('--filename', dest='filename', default=False,
                            help='Name of the file, or - for stdout'),
        parser.add_argument('--db-name', dest='database_name',
                            default='default',
                            help='Name of database (as defined in '
                                 'settings.DATABASES[]) to dump.'),
        parser.add_argument('--compress', dest='compression_command',
                            help='Optional command to run (e.g., gzip) '
                                 'to compress output file.'),
        parser.add_argument('--quiet', dest='quiet', action='store_true',
                            default=False,
                            help='Be silent.'),
        parser.add_argument('--debug', dest='debug', action='store_true',
                            default=False,
                            help='Show commands that are being executed.'),
        parser.add_argument('--pgpass', dest='pgpass', action='store_true',
                            default=False,
                            help='Use the ~/.pgdump file for password instead '
                                 'of prompting (PostgreSQL only).'),
        parser.add_argument('--raw-args', dest='raw_args', default='',
                            help='Argument(s) to pass to database dump '
                                 'command as is'),

    OUTPUT_STDOUT = object()

    def handle(self, *args, **options):
        self.db_name = options.get('database_name', 'default')
        self.compress = options.get('compression_command')
        self.quiet = options.get('quiet')
        self.debug = options.get('debug')
        self.pgpass = options.get('pgpass')

        if self.db_name not in settings.DATABASES:
            raise CommandError(
                'Database %s is not defined in settings.DATABASES' % self.db_name)

        self.engine = settings.DATABASES[self.db_name].get('ENGINE')
        self.db = settings.DATABASES[self.db_name].get('NAME')
        self.user = settings.DATABASES[self.db_name].get('USER')
        self.password = settings.DATABASES[self.db_name].get('PASSWORD')
        self.host = settings.DATABASES[self.db_name].get('HOST')
        self.port = settings.DATABASES[self.db_name].get('PORT')

        backup_directory = options['backup_directory']
        filename = options['filename']

        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)

        if not filename:
            outfile = self.destination_filename(backup_directory, self.db)
        elif filename == "-":
            outfile = self.OUTPUT_STDOUT
            self.quiet = True
        else:
            outfile = os.path.join(backup_directory, filename)

        raw_args = options['raw_args']

        if 'postgresql' in self.engine:
            self.do_postgresql_backup(outfile, raw_args=raw_args)
        else:
            raise CommandError(
                'Backups of %s engine are not implemented.' % self.engine)

        if self.compress:
            self.run_command('%s %s' % (self.compress, outfile))

    @staticmethod
    def destination_filename(backup_directory, database_name):
        return os.path.join(backup_directory,
                            '%s_backup_%s.sql' % (
                                database_name,
                                time.strftime('%Y%m%d-%H%M%S')))

    def run_command(self, command):
        if self.debug:
            print(command)

        os.system(command)

    def do_postgresql_backup(self, outfile, raw_args=''):
        if not self.quiet:
            print('Executing PostgreSQL backup of database "{}" into {}'.format(
                self.db, outfile
            ))

        main_args = []
        if self.user:
            main_args += ['--username=%s' % self.user]
        if self.host:
            main_args += ['--host=%s' % self.host]
        if self.port:
            main_args += ['--port=%s' % self.port]
        if raw_args:
            main_args += [raw_args]

        excluded_args = main_args[:]

        command = 'pg_dump -w %s %s' % (' '.join(excluded_args), self.db)

        if outfile != self.OUTPUT_STDOUT:
            command += ' > %s' % outfile

        self.run_postgresql_command(command, outfile)

    def run_postgresql_command(self, command, outfile):
        if self.debug:
            print(command)

        custom_env = os.environ.copy()

        if self.password:
            custom_env['PGPASSWORD'] = self.password

        pipe = subprocess.Popen(command, shell=True, env=custom_env)

        if outfile == self.OUTPUT_STDOUT:
            shutil.copyfileobj(pipe.stdout, sys.stdout)
