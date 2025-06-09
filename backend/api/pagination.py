from rest_framework.pagination import PageNumberPagination

from .constants import SIZE_PAGE


class DefaultPagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "page"
    page_size = SIZE_PAGE
