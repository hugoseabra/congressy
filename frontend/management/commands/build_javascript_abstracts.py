import fnmatch
import os

import uglipyjs
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Construir arquivo principal de javascript abstracts.'

    def add_arguments(self, parser):
        parser.add_argument('--fake',
                            action='store_true',
                            dest='fake',
                            help='Do not create unified file.')
        parser.add_argument('--show',
                            action='store_true',
                            dest='show',
                            help='Show files which will be processed.')

    def handle(self, *args, **options):
        js_abstracts_path = os.path.join(
            settings.BASE_DIR,
            'frontend',
            'static',
            'assets',
            'js',
            'abstracts',
        )

        js_main_file = 'cgsy-abstracts.js';
        js_main_file_path = os.path.join(js_abstracts_path, js_main_file)

        if options['show'] is True:
            print()
            print('BASE PATH: {}'.format(js_abstracts_path))
            print('FINAL FILE: {}'.format(js_main_file_path))

        if not os.path.isdir(js_abstracts_path):
            self.stdout.write(self.style.ERROR(
                'Diretório inválido: {}'.format(js_abstracts_path)
            ))
            return

        pattern = "*.js"
        js_files = os.listdir(js_abstracts_path)
        js_files.sort()

        content = ''
        for file_name in js_files:
            if file_name == js_main_file:
                continue

            if options['show'] is True:
                print('   - {}'.format(file_name))
                continue

            self.stdout.write(self.style.SUCCESS(
                'Aquivo: {}'.format(file_name)
            ))

            if fnmatch.fnmatch(file_name, pattern):
                with open(os.path.join(js_abstracts_path, file_name),
                          'r') as f:
                    content += uglipyjs.compile(f.read()).decode('utf-8')
                    f.close()

        if options['show'] is False and options['fake'] is False and content:
            self.stdout.write(self.style.SUCCESS(
                'Novo Aquivo: {}'.format(js_main_file)
            ))
            with open(js_main_file_path, 'w') as f:
                f.write(content)
                f.close()
