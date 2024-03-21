from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
import jwt
from rest_framework import authentication, exceptions, status
from Crm_app.models import *
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.http import HttpRequest
from functools import wraps

import base64
import random
import re
from mimetypes import guess_extension
import http.client
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def MyPagination(data, page_number, data_per_page,request):

    base_url = request.build_absolute_uri('?page_number')

    paginator = Paginator(data, data_per_page)
    page = paginator.page(page_number)
   
    if page.has_next():
        next_page = int(page_number) + 1
        next_url = str(base_url) + '=' + str(next_page) +'&data_per_page='+str(data_per_page)
    else:
        next_url = None

    if page.has_previous():
        previous_page = int(page_number) - 1
        previous_url = str(base_url) + '=' + str(previous_page) +'&data_per_page='+str(data_per_page)
    else:
        previous_url = None
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    pagination_object = {
        'current_page':page.number,
        'number_of_pages':paginator.num_pages,
        'next_url':next_url,
        'previous_url':previous_url,
        'next_page_number':page.next_page_number,
        'previous_page_number':page.previous_page_number,
        'has_next':page.has_next(),
        'has_previous':page.has_previous(),
        'has_other_pages':page.has_other_pages(),
    }
   
    return list(page_obj),(pagination_object)