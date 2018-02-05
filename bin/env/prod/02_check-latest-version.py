###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: verifica última versão publicada
#
# Busca a última com versão (padrão semver) mais alta e compara com a versão
# do build. Se diferente e maior, persistir em um arquivo com valor "1".
###############################################################################

import os
import subprocess

import semver
from clint.textui import colored, puts


def shell_do(cmd, **kwargs):
    process = subprocess.Popen(cmd.format(**kwargs), shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    out, err = process.communicate()

    if err:
        puts(colored.red(err))

    return out


BASE = os.path.dirname(__file__)

REPO_LINK = '871800672816.dkr.ecr.us-east-1.amazonaws.com'
REPO_NAME = 'cgsy'

LATEST_IMAGE = shell_do(
    'docker exec -i awsecr last-image {}'.format(REPO_NAME)
).rstrip('\r\n')

LATEST_VERSION = LATEST_IMAGE.replace(
    "Repository: {}\n".format(REPO_NAME),
    ''
)
LATEST_VERSION = LATEST_VERSION.replace(
    '{}/{}:'.format(REPO_LINK, REPO_NAME),
    ''
)

VERSION_FILE = os.path.join(BASE, '..', '..', '..', 'version')
VERSION = shell_do('cat {}'.format(VERSION_FILE))

VERSION = VERSION.rstrip('\r\n')
LATEST_VERSION = LATEST_VERSION.rstrip('\r\n')

print("VERSION: " + VERSION)
print("LATEST VERSION: " + LATEST_VERSION)

higher_version = semver.compare(LATEST_VERSION, VERSION) == -1

with open('tagged_version', 'w+') as f:
    f.write('1' if higher_version is True else '0')
    f.close()
