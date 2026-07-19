from django.db import connection


class QueriesAnalysisMiddleware:
    """Middleware that logs all SQL queries executed during a request (debug use only)"""

    def __init__(self, get_response):
        """Stores the next callable in the middleware chain"""

        self.get_response = get_response

    def __call__(self, request):
        """Prints request info, execute the request, then log all executed SQL queries"""

        print(
            f"--------------------------{request.method}----{request.path}---------------------"
        )

        response = self.get_response(request)

        count = 1

        for query in connection.queries:
            print(
                f"------------------------{count}--------------------------------------------"
            )
            print(query.get("sql"))
            print()
            count = count + 1

        return response
