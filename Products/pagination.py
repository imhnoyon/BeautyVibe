from rest_framework.pagination import PageNumberPagination
from utils.api_response import APIResponse
from rest_framework import status

class CustomPagination(PageNumberPagination):
    page_size = 10  # default items per page
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return APIResponse.success(
            message="Users retrieved successfully",
            data={
                "total": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
            status_code=status.HTTP_200_OK
        )