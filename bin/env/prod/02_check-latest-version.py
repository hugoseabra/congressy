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
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    out, err = process.communicate()

    if err:
        puts(colored.red(err))

    return out


BASE = os.path.dirname(__file__)

REPO_LINK = '871800672816.dkr.ecr.us-east-1.amazonaws.com'
REPO_NAME = 'cgsy'

LATEST_IMAGE = shell_do(
    'docker exec -i awsecr last-image {}'.format(REPO_NAME)
)

LATEST_VERSION = str(LATEST_IMAGE).replace(
    'Repository: {}\n'.format(REPO_NAME),
    ''
)
LATEST_VERSION = str(LATEST_VERSION).replace(
    '{}/{}:'.format(REPO_LINK, REPO_NAME),
    ''
)

VERSION_FILE = os.path.join(BASE, '..', '..', '..', 'version')
VERSION = shell_do('cat {}'.format(VERSION_FILE))

VERSION = str(VERSION).rstrip('\r\n')
LATEST_VERSION = LATEST_VERSION.rstrip('\r\n')

print("LATEST VERSION: {}".format(LATEST_VERSION))
print("VERSION TO DEPLOY: {}".format(VERSION))

higher_version = semver.compare(LATEST_VERSION, VERSION) == -1

tagged_version_file = os.path.join(BASE, 'tagged_version')

with open(tagged_version_file, 'w+') as f:
    value = '1' if higher_version is True else '0'
    print("Registrando valor '{}' em '{}'.".format(
        value,
        tagged_version_file
    ))

    f.write(value)
    f.close()

previous_version_file = os.path.join(BASE, 'previous_version')

with open(previous_version_file, 'w+') as f:
    f.write(LATEST_VERSION)
    f.close()
    print("Registrando versão anterior '{}' em '{}'.".format(
        LATEST_VERSION,
        previous_version_file
    ))
