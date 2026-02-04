from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from apps.core.pagination import BaseCursorPagination


class ReadOnlyModelViewset(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that has:
    - actions: `list`, `retrieve`
    - default pagination set to `BaseCursorPagination`
    - attached filter backends and search filters
    """

    pagination_class = BaseCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]


class ModelViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Viewset that has:
    - actions: list`, `create`
    - default pagination set to `BaseCursorPagination`
    - attached filter backends and search filters
    """

    pagination_class = BaseCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
