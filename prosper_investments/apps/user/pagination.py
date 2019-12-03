from rest_framework.pagination import PageNumberPagination


class UserInOrganisationPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'page'
    max_page_size = 100
