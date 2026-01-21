from rest_framework.pagination import CursorPagination


class BaseCursorPagination(CursorPagination):
    """Base pagination to be used in all pagination classes"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    ordering = ("-created_at", "-id")
