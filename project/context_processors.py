"""
Project context processor
"""
import os


def environment_version(request):
    """
    Adiciona ENVIRONMENT_VERSION no template.
    """

    return {
        'ENVIRONMENT_VERSION': os.getenv('ENVIRONMENT_VERSION'),
    }
