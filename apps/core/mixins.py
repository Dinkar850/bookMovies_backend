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
