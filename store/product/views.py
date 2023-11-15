from django.shortcuts import render

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from .models import HistoryProducts

def custom_admin_view(request):
    sql_query = """
        SELECT ean, qty, date
        FROM public.history_products;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        results = cursor.fetchall()

    # You can process the results as needed, or simply display them in the response.
    result_str = '\n'.join([', '.join(map(str, row)) for row in results])

    return HttpResponse(result_str, content_type="text/plain")

