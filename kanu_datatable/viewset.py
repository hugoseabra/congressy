from collections import OrderedDict
import re
import uuid
import operator
from functools import reduce

from django.db import models
from django.utils import six
import rest_framework
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import BaseFilterBackend
from rest_framework.metadata import SimpleMetadata
from rest_framework.exceptions import ValidationError


class DataTableMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        metadata['search_fields'] = getattr(view, 'search_fields', [])
        metadata['order_columns'] = getattr(view, 'order_columns', [])
        return metadata


class DataTablePagination(LimitOffsetPagination):
    def to_html(self):
        pass

    default_limit = 20
    limit_query_param = 'length'
    offset_query_param = 'start'
    max_limit = None
    draw = None

    def get_paginated_response(self, data):
        return rest_framework.response.Response(OrderedDict([
            ('result', 'ok'),
            ('draw', data['draw']),
            ('recordsTotal', data['recordsTotal']),
            ('recordsFiltered', data['recordsFiltered']),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data['results'])
        ]))


class DataTableSearchFilter(BaseFilterBackend):
    def get_internal_type(self, queryset=None, field_name=None, field=None):
        if not field:
            field = queryset.model._meta.get_field(field_name)

        internal_type = field.get_internal_type()

        if internal_type in ('ForeignKey', 'OneToOneField'):
            return self.get_internal_type(field=field.target_field)

        return internal_type

    def construct_search(self, queryset, field_name, search_term):
        internal_type = self.get_internal_type(
            queryset=queryset,
            field_name=field_name
        )

        """
        Se o tipo não suportar busca textual, provoca
        conversão para validar o tipo
        """
        if internal_type in ('IntegerField', 'AutoField',):
            return field_name, int(search_term)
        elif internal_type in ('UUIDField',):
            return field_name, uuid.UUID(search_term)

        """ Busca textual ignorando os acentos """
        if str(search_term).startswith('^'):
            return "%s__unaccent__istartswith" % field_name, search_term[1:]
        elif str(search_term).startswith('='):
            return "%s__iexact" % field_name, search_term[1:]
        elif str(search_term).startswith('@'):
            return "%s__unaccent__search" % field_name, search_term[1:]
        if str(search_term).startswith('$'):
            return "%s__unaccent__iregex" % field_name, search_term[1:]
        else:
            return "%s__unaccent__icontains" % field_name, search_term

    def search_global(self, queryset, search_fields, search_term):
        """
        Pesquisa global usando: 'search[value]=FOO'
        """
        queries = []

        if search_term and not search_fields:
            raise ValidationError({
                "type": "@Todo: Fazer página de documentação",
                "title": "Erro na montagem da busca",
                "detail": 'Nenhum campo definido para busca',
                "search_fields": [],
                "search_term": search_term,
            })

        for search_field in search_fields:
            try:
                search_field, search_term = self.construct_search(
                    queryset,
                    six.text_type(search_field),
                    search_term)

                queries += [models.Q(**{search_field: search_term})]
            except ValueError:
                "Ignorando o erro de conversão para campos inteiro"
                pass

        # raise Exception(queries)

        return queryset.filter(reduce(operator.or_, queries))

    def search_columns(self, queryset, search_fields, columns):
        """
        Pesquisa por colunas usando:
        '?columns[2][data]=name&columns[2][search][value]=goiania'
        '?columns[1][data]=id&columns[2][search][value]=50'
        """
        queries = []

        for column in columns:
            if not column['data'] or not column['search']:
                continue

            if not column['data'] in search_fields:
                raise ValidationError({
                    "type": "@Todo: Fazer página de documentação",
                    "title": "Erro nos parâmetros da busca",
                    "detail": 'Coluna "%s" não é pesquisável' % column['data'],
                    "search_term": column['search']['value'],
                    "search_fields": search_fields,
                })

            try:
                search_field, search_term = self.construct_search(
                    queryset,
                    six.text_type(column['data']),
                    column['search']['value'])
                queries += [models.Q(**{search_field: search_term})]
            except ValueError as e:
                detail = "Uma conversão do valor '{0}' não pode ser " \
                         "feita para o campo '{1}'".format(
                    column['search']['value'],
                    column['data'],
                )

                raise ValidationError({
                    "type": "@Todo: Fazer página de documentação",
                    "title": "Erro na montagem da busca",
                    "detail": detail,
                    "internal_error": str(e),
                })

        if not queries:
            return queryset

        return queryset.filter(reduce(operator.and_, queries))

    def ordering(self, queryset, search_fields, query_params):
        """
        Implementa a ordenação usando:
            'columns[2][data]': 'name',
            'order[0][column]': '2',
            'order[0][dir]': 'asc',
        """
        columns = query_params.get('columns')

        order_params = {}
        for key in query_params.get('order'):
            order_params[int(key)] = query_params.get('order')[key]

        order = []
        for key in sorted(order_params):
            column_index = order_params[key]['column']
            column_dir = '' if not order_params[key]['dir'] == 'desc' else '-'
            column_name = columns[column_index]['data']
            order.append('%s%s' % (column_dir, column_name))

        return queryset.order_by(*order)

    def filter_queryset(self, request, queryset, view):
        """
        Filtra os registros pelos parametros enviados no formato do DataGrid
        """
        search_fields = getattr(view, 'search_fields', None)
        query_params = qs_to_dict(request.query_params)
        base = queryset

        """
        Filtros
        """
        try:
            search_term = query_params['search']['value']
            queryset = self.search_global(queryset, search_fields, search_term)
        except (KeyError, TypeError):
            pass

        try:
            columns = query_params['columns']
            queryset = self.search_columns(queryset, search_fields,
                                           columns.values())
        except (KeyError):
            pass

        """
        Ordenação
        """
        if 'order' in query_params and 'columns' in query_params:
            queryset = self.ordering(queryset, search_fields, query_params)

        return rest_framework.compat.distinct(queryset, base)


class DataTableAPIView(ListAPIView, GenericViewSet):
    pagination_class = DataTablePagination
    metadata_class = DataTableMetadata
    search_fields = ()

    """
    List a queryset.
    """

    def filter_queryset(self, queryset):
        return DataTableSearchFilter().filter_queryset(self.request, queryset,
                                                       self)

    def list(self, request, *args, **kwargs):
        response = {'draw': request.GET.get('draw', None)}

        queryset = self.get_queryset()
        response['recordsTotal'] = queryset.count()

        queryset = self.filter_queryset(queryset)
        response['recordsFiltered'] = queryset.count()

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response['results'] = serializer.data
        return self.get_paginated_response(response)


def qs_to_dict(request):
    """
    Transforma um dicionário de query string onde o nome do capo é
    codificado como dicionário para um dicionário real veja:

    De: {"order[1][column]": "1", "order[1][dir]": "asc"}
    Para: {"order": {"1": {"dir": "asc", "column": "1"}

    :param request:
    :return:
    """
    result = {}
    for name in request:
        val = request[name]
        match = re.findall('[a-zA-Z0-9_\-\.]+', name)

        if match and len(match) > 1:

            if not match[0] in result:
                result[match[0]] = {}

            if not len(match) > 2:
                result[match[0]][match[1]] = val
                continue
            elif not match[1] in result[match[0]]:
                result[match[0]][match[1]] = {}

            if not len(match) > 3:
                result[match[0]][match[1]][match[2]] = val
                continue
            elif not match[2] in result[match[0]][match[1]]:
                result[match[0]][match[1]][match[2]] = {}

            result[match[0]][match[1]][match[2]][match[3]] = val
        else:
            result[name] = val
    return result
