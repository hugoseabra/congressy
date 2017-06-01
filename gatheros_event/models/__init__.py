"""
Models para Gatheros Event
"""
# @TODO Remover rules dos models e levá-los para camadas de domínios
# @TODO Manter arquivos de rules em models/rules
# @TODO Testar rules separadamente na camada de domínio
# @TODO Testar rules aplicdos aos models em Form

from .segment import Segment
from .subject import Subject
from .occupation import Occupation
from .category import Category
from .person import Person
from .organization import Organization
from .place import Place
from .member import Member
from .event import Event
from .info import Info
from .invitation import Invitation
