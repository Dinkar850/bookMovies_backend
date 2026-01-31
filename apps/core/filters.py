import django_filters


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Filter to be used by filtersets in other apps for selecing multiple comma separated string values"""


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Filter to be used by filtersets in other apps for selecing multiple comma separated numerical values for IDs"""
