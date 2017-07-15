""" Executa comandos do GIT. """

from subprocess import PIPE, Popen

from django.conf import settings


def get_git_revision():
    """ Resgata revisão atual do projeto do branch master. """
    command = [
        'cat',
        '{BASE_DIR}/.git/refs/heads/master'.format(BASE_DIR=settings.BASE_DIR)
    ]
    output = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return output.communicate()[0]
