from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from apps.slot import models as SlotModels

from .pagination import BaseCursorPagination


class UpcomingSlotsQuerySetMixin:
    """Sets querysets and prefetch arguments and provides `base_queryset` method that returns entries for which slots are available"""

    queryset = None
    prefetch_related_args = ()

    def base_queryset(self, now):
        return (
            self.queryset.filter(slots__is_active=True, slots__date_time__gte=now)
            .distinct()
            .prefetch_related(*self.prefetch_related_args)
        )


class UpcomingSlotsPrefetchMixin(UpcomingSlotsQuerySetMixin):
    """Provides `slots_prefetch_queryset` method for returning slots for entries that have a reverse foreign key relation with slots model"""

    def slots_prefetch_queryset(self, qs, now):
        return qs.prefetch_related(
            Prefetch(
                "slots",
                queryset=SlotModels.Slot.objects.filter(
                    is_active=True,
                    date_time__gte=now,
                )
                .select_related("movie", "cinema", "language")
                .order_by("date_time"),
                to_attr="active_slots",
            )
        )


class ListConfigMixin(generics.ListAPIView):
    """Base list api view mixin for attaching pagination classes and filter backends"""

    pagination_class = BaseCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
