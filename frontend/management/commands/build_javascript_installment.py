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
        js_dir_path = os.path.join(
            settings.BASE_DIR,
            'frontend',
            'static',
            'assets',
            'js',
            'installment',
        )

        js_main_file = 'cgsy-installment.js';
        js_main_file_path = os.path.join(js_dir_path, js_main_file)

        if options['show'] is True:
            print()
            print('BASE PATH: {}'.format(js_dir_path))
            print('FINAL FILE: {}'.format(js_main_file_path))

        if not os.path.isdir(js_dir_path):
            self.stdout.write(self.style.ERROR(
                'Diretório inválido: {}'.format(js_dir_path)
            ))
            return

        files = self.get_file_paths(js_dir_path)
        files.sort()

        content = ''
        for file_path in files:
            file_name = file_path.split(os.path.sep)[-1]

            if file_name == js_main_file:
                continue

            if options['show'] is True:
                print('   - {}'.format(file_name))
                continue

            self.stdout.write(self.style.SUCCESS(
                'Aquivo: {}'.format(file_name)
            ))

            with open(file_path, 'r') as f:
                content += uglipyjs.compile(f.read()).decode('utf-8')
                f.close()

        if options['show'] is False and options['fake'] is False and content:
            self.stdout.write(self.style.SUCCESS(
                'Novo Aquivo: {}'.format(js_main_file)
            ))
            with open(js_main_file_path, 'w') as f:
                f.write(content)
                f.close()


    def get_file_paths(self, directory_path):
        if not os.path.isdir(directory_path):
            return []

        files = []
        for path in os.listdir(directory_path):
            path = os.path.join(directory_path, path)

            if os.path.isdir(path):
                files += self.get_file_paths(path)
                continue

            if not fnmatch.fnmatch(path, '*.js'):
                continue

            files.append(path)

        return files