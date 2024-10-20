from datetime import datetime, timedelta
from .serializers import *
from django.contrib.auth import authenticate, login
import random
import string
from rest_framework.decorators import action
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from rest_framework.response import Response
from .models import *
from django.db.models import Sum, F
import requests
import ast
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count
from razorpay.errors import SignatureVerificationError
from rest_framework.views import APIView
from rest_framework import status,generics
from django.db.models import Q
from Crypto.Util.Padding import pad, unpad 
import logging
from django.utils.html import strip_tags
from django.urls import reverse
from django.shortcuts import render
from django.core.files.base import ContentFile
import os
from django.utils import timezone
from django.core.files.storage import default_storage
import uuid
import base64
from rest_framework.pagination import PageNumberPagination
from django.contrib import messages
from django.shortcuts import redirect
import razorpay
from rest_framework.decorators import api_view
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ValidationError
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
from .backend import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import unquote
from django.db.models import F
from django.db import transaction
from django.db import transaction, IntegrityError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class RoleAPIView(APIView):
    def get(self, request, pk=None):
        if pk is None:
           
            roles = Role.objects.all()
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data)
        else:
            
            try:
                role = Role.objects.get(pk=pk)
                serializer = RoleSerializer(role)
                return Response(serializer.data)
            except Role.DoesNotExist:
                return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data.get('role_name')

            if Role.objects.filter(role_name=role_name).exists():
                return Response({"message": "Role with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"message": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data.get('role_name')

            if Role.objects.exclude(pk=pk).filter(role_name=role_name).exists():
                return Response({"message": "Role with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            role = Role.objects.get(pk=pk)
            role.delete()
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Role.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)


def convertBase64(image, image_name, username, folder_name):
    if image is None:
        return None

    split_base_url_data = image.split(';base64,')[1]
    imgdata1 = base64.b64decode(split_base_url_data)
    filename1 = "/amx-crm/site/public/media/" + str(folder_name) + "/" + str(username) + image_name + '.png'
    fname1 = '/' + str(folder_name) + '/' + str(username) + image_name + '.png'
    ss = open(filename1, 'wb')
    ss.write(imgdata1)
    ss.close()

    return fname1


class PartnerAPIView(APIView):
    def get(self, request, pk=None):
        # Retrieve query parameters
        page_number = request.query_params.get('page_number')
        data_per_page = request.query_params.get('data_per_page')
        search_param = request.GET.get('search', '')

        if page_number and data_per_page:
            # Paginated response
            users = CustomUser.objects.filter(Q(role_id__role_name="Partner") | Q(role_id__role_name="Super_admin")).order_by('-id')

            if search_param:
                users = users.filter(
                    Q(first_name__icontains=search_param) |
                    Q(last_name__icontains=search_param) |
                    Q(email__icontains=search_param) |
                    Q(mobile_number__icontains=search_param)
                )

            # Use Django Paginator for pagination
            paginator = Paginator(users, data_per_page)
            try:
                paginated_users = paginator.page(page_number)
            except EmptyPage:
                return Response({"message": "No results found for the given page number"}, status=404)

            serialized_users = CustomUserSerializer(paginated_users, many=True, context={'request': request}).data
            len_of_data = paginator.count

            return Response({
                'result': {
                    'status': 'GET ALL with pagination',
                    'pagination': {
                        'current_page': paginated_users.number,
                        'number_of_pages': paginator.num_pages,
                        'next_url': self.get_next_url(request, paginated_users),
                        'previous_url': self.get_previous_url(request, paginated_users),
                        'has_next': paginated_users.has_next(),
                        'has_previous': paginated_users.has_previous(),
                        'has_other_pages': paginated_users.has_other_pages(),
                        'len_of_data': len_of_data,
                    },
                    'data': serialized_users,
                },
            })
        else:
            # Non-paginated response
            try:

                if pk:
                    # Get partner by ID
                    partner = CustomUser.objects.get(Q(pk=pk), Q(role_id__role_name="Partner") | Q(role_id__role_name="Super_admin"))
                    partner.save()

                    serializer = CustomUserSerializer(partner, context={'request': request})

                    return Response({
                        'status': 'GET by ID',
                        **serializer.data,
                    }, status=200)
 
                else:
                    # Get all partners without pagination
                    users = CustomUser.objects.filter(Q(role_id__role_name="Partner") | Q(role_id__role_name="Super_admin")).order_by('-id')

                    if search_param:
                        users = users.filter(
                            Q(first_name__icontains=search_param) |
                            Q(last_name__icontains=search_param) |
                            Q(email__icontains=search_param) |
                            Q(mobile_number__icontains=search_param)
                        )

                    len_of_data = len(users)

                    return Response({
                        'result':{
                        'status': 'GET ALL without pagination',
                        'len_of_data': len_of_data,
                        'data': [
                            {
                                **CustomUserSerializer(user, context={'request': request}).data,
                                
                            }
                            for user in users
                        ],
                    }})
            except ObjectDoesNotExist:
                return Response({"message": "Partner not found"}, status=404)

    def get_next_url(self, request, paginated_users):
        if paginated_users.has_next():
            return request.build_absolute_uri(
                f"?page_number={paginated_users.next_page_number}&data_per_page={paginated_users.paginator.per_page}")
        return None

    def get_previous_url(self, request, paginated_users):
        if paginated_users.has_previous():
            return request.build_absolute_uri(
                f"?page_number={paginated_users.previous_page_number}&data_per_page={paginated_users.paginator.per_page}")
        return None

        
    # def get(self, request, pk=None):
    #     data = request.data
    #     page_number = request.query_params.get('page_number')
    #     data_per_page = request.query_params.get('data_per_page')
    #     pagination = request.query_params.get('pagination')
    #     search_param = request.GET.get('search', '')

    #     if pagination:
            
    #         if pk is None and not search_param:
    #             users = CustomUser.objects.filter(role_id__role_name="Partner").order_by('-id')
    #         elif pk is None:
    #             users = CustomUser.objects.filter(role_id__role_name="Partner").filter(
    #                 Q(first_name__icontains=search_param) |
    #                 Q(last_name__icontains=search_param) |
    #                 Q(email__icontains=search_param) |
    #                 Q(mobile_number__icontains=search_param)
    #             ).order_by('-id')
    #         else:
    #             try:
    #                 partner = CustomUser.objects.get(pk=pk, role_id__role_name="Partner")
    #                 serializer = CustomUserSerializer(partner, context={'request': request})
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
    #             except CustomUser.DoesNotExist:
    #                 return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

           
    #         paginator = Paginator(users, data_per_page)
    #         try:
    #             paginated_users = paginator.page(page_number)
    #         except EmptyPage:
    #             return Response({"message": "No results found for the given page number"}, status=status.HTTP_404_NOT_FOUND)

    #         serialized_users = CustomUserSerializer(paginated_users, many=True, context={'request': request}).data
    #         len_of_data = paginator.count
    #         data_pagination = MyPagination(users, page_number, data_per_page, request)

    #         return Response({
    #             'result': {
    #                 'status': 'GET ALL with pagination',
    #                 'pagination': {
    #                     'current_page': data_pagination[1]['current_page'],
    #                     'number_of_pages': data_pagination[1]['number_of_pages'],
    #                     'next_url': data_pagination[1]['next_url'],
    #                     'previous_url': data_pagination[1]['previous_url'],
    #                     'has_next': data_pagination[1]['has_next'],
    #                     'has_previous': data_pagination[1]['has_previous'],
    #                     'has_other_pages': data_pagination[1]['has_other_pages'],
    #                     'len_of_data': len_of_data,
    #                 },
    #                 'data': serialized_users,
    #             },
    #         })

    #     else:
            
    #         if pk is None and not search_param:
    #             users = CustomUser.objects.filter(role_id__role_name="Partner").order_by('-id')
    #         elif pk is None:
    #             users = CustomUser.objects.filter(role_id__role_name="Partner").filter(
    #                 Q(first_name__icontains=search_param) |
    #                 Q(last_name__icontains=search_param) |
    #                 Q(email__icontains=search_param) |
    #                 Q(mobile_number__icontains=search_param)
    #             ).order_by('-id')
    #         else:
    #             try:
    #                 partner = CustomUser.objects.get(pk=pk, role_id__role_name="Partner")
    #                 serializer = CustomUserSerializer(partner, context={'request': request})
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
    #             except CustomUser.DoesNotExist:
    #                 return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

    #         serialized_users = CustomUserSerializer(users, many=True, context={'request': request}).data
    #         len_of_data = len(users)

    #         return Response({
    #             'result': {
    #                 'status': 'GET ALL without pagination',
    #                 'len_of_data': len_of_data,
    #                 'data': serialized_users,
    #             },
    #         })



    def post(self, request):

        data = request.data

        username = data.get('username')
        email = data.get('email')
        mobile_number = data.get('mobile_number')
        super_admin_id = data.get('Super_admin')

        if CustomUser.objects.filter(username=username).exists():
            return Response({"message": "Username must be unique"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "Email must be unique"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(mobile_number=mobile_number).exists():
            return Response({"message": "Mobilenumber must be unique"}, status=status.HTTP_400_BAD_REQUEST)

        default_category, created = CustomerCategory.objects.get_or_create(name="Organization")
        super_admin = get_object_or_404(CustomUser, id=super_admin_id)
        print(super_admin,"sssssssssss")


        serializer = CustomUserSerializer(data=request.data)
        print(serializer,"serializerrrrrrrrrrrrrrrrrrrrrrrrr")
        if serializer.is_valid():
            serializer.validated_data['category'] = default_category
            serializer.validated_data['created_by'] = super_admin
            username = serializer.validated_data.get("username")
            email = serializer.validated_data.get("email")
            print(email,"eeeeeeeeeeeeeeee")
            domain = 'https://amx-crm.thestorywallcafe.com/'
            title = 'AMX CRM Portal'

            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            serializer.validated_data['password'] = password

            user = serializer.save()

            subject = 'AMX CRM Credentials'
            message = f'Please note down your credentials.\nUsername: {username}\nPassword: {password}'
            message += f'\nLogin through the {title}: {domain}'
            from_email = 'amxdrone123@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({"message": "Partner created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        try:
            partner = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        required_fields = ['first_name', 'last_name', 'email', 'email_altr', 'mobile_number', 'address', 'pin_code',
                           'password', 'location']

        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response({"message": f"The following fields are required: {', '.join(missing_fields)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        allowed_fields = ["first_name", "last_name", "email", "email_altr", "mobile_number", "address", "pin_code",
                          "password", "location", "profile_pic"]
        data = {field: data.get(field) for field in allowed_fields if field in data}

        # if 'profile_pic' in data:
        #     profile_pic_base64 = data.pop('profile_pic')

        #     try:
        #         _, base64_data = profile_pic_base64.split(',')
        #         image_data = base64.b64decode(base64_data)
        #         file_path = f"/profile_pics/{partner.username}_profile_pic.png"

        #         partner.profile_pic.save(f"{partner.username}_profile_pic.png", ContentFile(image_data), save=True)
        #         partner.profile_pic.name = file_path

        #     except Exception as e:
        #         return Response({"message": f"Failed to process profile picture: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)     



        if 'profile_pic' in data:
            profile_pic_base64 = data.pop('profile_pic')

            
            try:
              
                _, base64_data = profile_pic_base64.split(',')

                
                image_data = base64.b64decode(base64_data)
                partner.profile_pic.save(f"{partner.username}_profile_pic.png", ContentFile(image_data), save=False)

            except Exception as e:
                return Response({"message": f"Failed to process profile picture: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


        for key, value in data.items():
            setattr(partner, key, value)

        partner.updated_date_time = timezone.now()

        try:
            partner.full_clean()
            partner.save()

         
            partner.refresh_from_db()
            response_data = {
                'message': 'Partner details updated successfully',
                'profile_image_path': partner.profile_pic.url if partner.profile_pic else None,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk):
    #     try:
    #         partner = CustomUser.objects.get(pk=pk)
    #     except CustomUser.DoesNotExist:
    #         return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

    #     data = request.data
    #     required_fields = ['first_name', 'last_name', 'email', 'email_altr', 'mobile_number', 'address', 'pin_code',
    #                        'password', 'location']

    #     missing_fields = [field for field in required_fields if field not in request.data]
    #     if missing_fields:
    #         return Response({"message": f"The following fields are required: {', '.join(missing_fields)}"},
    #                         status=status.HTTP_400_BAD_REQUEST)

    #     allowed_fields = ["first_name", "last_name", "email", "email_altr", "mobile_number", "address", "pin_code",
    #                       "password", "location", "profile_pic"]
    #     data = {field: data.get(field) for field in allowed_fields if field in data}

        
    #     if 'profile_pic' in data:
    #         profile_pic_base64 = data.pop('profile_pic')

            
    #         try:
              
    #             _, base64_data = profile_pic_base64.split(',')

                
    #             image_data = base64.b64decode(base64_data)
    #             partner.profile_pic.save(f"{partner.username}_profile_pic.png", ContentFile(image_data), save=False)

    #         except Exception as e:
    #             return Response({"message": f"Failed to process profile picture: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


    #     for key, value in data.items():
    #         setattr(partner, key, value)

    #     partner.updated_date_time = timezone.now()

    #     try:
    #         partner.full_clean()
    #         partner.save()

         
    #         partner.refresh_from_db()
    #         response_data = {
    #             'message': 'Partner details updated successfully',
    #             'profile_image_path': partner.profile_pic.url if partner.profile_pic else None,
    #         }
    #         return Response(response_data, status=status.HTTP_200_OK)
    #     except ValidationError as e:
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)




    def delete(self, request, pk=None):
        if pk is None:
            partner_ids_param = request.query_params.get('partner_ids', '')
            partner_ids = [int(partner_id) for partner_id in partner_ids_param.split(',') if partner_id]
            if not partner_ids:
                partners = CustomUser.objects.filter(role_id__role_name="Partner")
                partners.delete()
                return Response({"message": "All partners deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            try:
                partners = CustomUser.objects.filter(pk__in=partner_ids, role_id__role_name="Partner")
                partners.delete()
                return Response({"message": "Selected partners deleted successfully"},
                                status=status.HTTP_204_NO_CONTENT)
            except CustomUser.DoesNotExist:
                return Response({"message": "Partners not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                partner = CustomUser.objects.get(pk=pk, role_id__role_name="Partner").delete()
             
                return Response({"message": "Partner deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except CustomUser.DoesNotExist:
                return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)


class PartnerProfileUpdateForSuperAdminAPIView(APIView):
    def put(self, request, pk):
        try:
            partner = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

        super_admin_id = request.data.get("Super_admin")

        try:
            super_admin = CustomUser.objects.get(pk=super_admin_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Super Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        super_admin_role = Role.objects.filter(role_name="Super_admin").first()

        if not super_admin_role:
            return Response({"message": "Super Admin role not found"}, status=status.HTTP_404_NOT_FOUND)

        user_has_super_admin_role = super_admin.role_id == super_admin_role

        if not user_has_super_admin_role:
            return Response({"message": "User is not a Super Admin and cannot update partners."},
                            status=status.HTTP_403_FORBIDDEN)

        new_username = request.data.get("username")
        print('new_username',new_username)
        if new_username:
            existing_partner = CustomUser.objects.filter(username=new_username).exclude(pk=pk).first()
            if existing_partner:
                return Response({"message": "Username already exists. Choose a different one."},
                                status=status.HTTP_400_BAD_REQUEST)
            partner.username = new_username

        new_email = request.data.get("email")
        print('new_email',new_email)
        if new_email:
            existing_partner = CustomUser.objects.filter(email=new_email).exclude(pk=pk).first()
            if existing_partner:
                return Response({"message": "Email already exists. Choose a different one."},
                                status=status.HTTP_400_BAD_REQUEST)
            partner.email = new_email

        new_mobile_number = request.data.get("mobile_number")
        print('new_mobile_number',new_mobile_number)
        if new_mobile_number:
            existing_partner = CustomUser.objects.filter(mobile_number=new_mobile_number).exclude(pk=pk).first()
            if existing_partner:
                return Response({"message": "Mobile number already exists. Choose a different one."},
                                status=status.HTTP_400_BAD_REQUEST)
            partner.mobile_number = new_mobile_number

        if "first_name" in request.data:
            partner.first_name = request.data["first_name"]

        if "last_name" in request.data:
            partner.last_name = request.data["last_name"]

        if "email_altr" in request.data:
            partner.email_altr = request.data["email_altr"]

        if "address" in request.data:
            partner.address = request.data["address"]


        if "pin_code" in request.data:
            partner.pin_code = request.data["pin_code"]

        if "profile_pic" in request.data:
            profile_pic_data = request.data["profile_pic"]

            
            decoded_url = unquote(unquote(profile_pic_data))

           
            if decoded_url.startswith("http://") or decoded_url.startswith("https://"):
                partner.profile_pic = decoded_url
            else:
               
                converted_af_image = convertBase64(profile_pic_data, 'profilePic', partner.username, 'profile_pics')

                if converted_af_image:
                    converted_af_image = converted_af_image.strip('"')

                partner.profile_pic = converted_af_image

        if "password" in request.data:
            partner.password = request.data["password"]


        if "location" in request.data:
            partner.location = request.data["location"]

        partner.save()
        print('partnerrrrrrrrrrrr',partner)
        return Response({"message": "Partner profile details updated successfully"}, status=status.HTTP_200_OK)




class PartnerCompanyUpdateForSuperAdminAPIView(APIView):
    def put(self, request, pk):
        try:
            partner = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

        super_admin_id = request.data.get("Super_admin")
        print('super_admin_id',super_admin_id)

        try:
            super_admin = CustomUser.objects.get(pk=super_admin_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Super Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        super_admin_role = Role.objects.filter(role_name="Super_admin").first()
        print('super_admin_role',super_admin_role)

        if not super_admin_role:
            return Response({"message": "Super Admin role not found"}, status=status.HTTP_404_NOT_FOUND)

        user_has_super_admin_role = super_admin.role_id == super_admin_role
        print('user_has_super_admin_role',user_has_super_admin_role)

        if not user_has_super_admin_role:
            return Response({"message": "User is not a Super Admin and cannot update partners."},
                            status=status.HTTP_403_FORBIDDEN)

        if "pan_number" in request.data:
            partner.pan_number = request.data["pan_number"]

        if "company_name" in request.data:
            partner.company_name = request.data["company_name"]

        if "company_email" in request.data:
            partner.company_email = request.data["company_email"]

        if "shipping_address" in request.data:
            partner.shipping_address = request.data["shipping_address"]

        if "billing_address" in request.data:
            partner.billing_address = request.data["billing_address"]

        if "company_phn_number" in request.data:
            partner.company_phn_number = request.data["company_phn_number"]

        if "company_gst_num" in request.data:
            partner.company_gst_num = request.data["company_gst_num"]

        if "company_cin_num" in request.data:
            partner.company_cin_num = request.data["company_cin_num"]

        if "company_logo" in request.data:
            company_logo_base64 = request.data["company_logo"]
            converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username, 'company_logos')

            if converted_company_logo_base64:
                converted_company_logo_base64 = converted_company_logo_base64.strip('"')

            partner.company_logo = converted_company_logo_base64



        partner.save()
        print('partnesdsssssssssssssssssr',partner)
        return Response({"message": "Partner company details updated successfully"}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not (username and password):
            return Response({"message": "Missing required field"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(Q(username=username) & Q(password=password)).first()

        if user:
            user_name = user.username
            user_id = user.id
            role = user.role_id.role_name
            role_id = user.role_id.id
            email = user.email
            mobile_number = user.mobile_number
            firstname = user.first_name
            lastname = user.last_name

            auth_token = jwt.encode(
                {'user_id': user_id, 'name': user_name, 'exp': datetime.utcnow() + timedelta(days=5)},
                str(settings.JWT_SECRET_KEY), algorithm="HS256")

            authorization = "Bearer " + str(auth_token)

            if role == "Super_admin":
                message = 'Super_admin login successful'
            elif role == "Partner":
                message = 'Partner login successful'
            else:
                message = 'Login successful'

            response = {
                'result': {
                    'user_info': {
                        'username': user_name,
                        'user_id': user_id,
                        'token': authorization,
                        "user_role": role,
                        "user_role_id": role_id,
                        "user_email": email,
                        "mobile_number": mobile_number,
                        "firstname": firstname,
                        "lastname": lastname
                    },
                    'message': message
                }
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response({'result': {'error': 'Invalid credentials'}}, status=status.HTTP_401_UNAUTHORIZED)


class DroneCategoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        pk = kwargs.get('pk')  # Retrieve pk from URL parameters

        if id is not None:
            status = DroneCategory.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'category_name': status.category_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        elif pk is not None:
            status = DroneCategory.objects.filter(id=pk).first()  # Use pk instead of id
            if status:
                data = {'id': status.id, 'category_name': status.category_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        else:
            data = DroneCategory.objects.all().values()
            return Response(data)


    def post(self, request):
        data = request.data
        category_name = data.get('category_name')

        if DroneCategory.objects.filter(category_name=category_name).exists():
            return Response({'message': 'Drone category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_status = DroneCategory.objects.create(category_name=category_name)
            return Response({'result': 'Drone category is created successfully!'}, status=status.HTTP_201_CREATED)


    def put(self, request, pk):
        data = request.data
        category_name = data.get('category_name')

        try:
            status_instance = DroneCategory.objects.get(id=pk)

            if DroneCategory.objects.filter(category_name=category_name).exclude(id=pk).exists():
                return Response({'message': 'DroneCategory name already exists. Choose a different name.'},
                                status=status.HTTP_400_BAD_REQUEST)

            status_instance.category_name = category_name
            status_instance.updated_date_time = datetime.now()
            status_instance.save()

            return Response({'message': 'DroneCategory status updated successfully'})
        except DroneCategory.DoesNotExist:
            return Response({'message': 'DroneCategory status ID not found'}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        try:
            category = DroneCategory.objects.get(pk=pk)
            category.delete()
            return Response({"message": "Drone category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except DroneCategory.DoesNotExist:
            return Response({"message": "Drone category not found"}, status=status.HTTP_404_NOT_FOUND)

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
class DroneAPIView(APIView):
    def get(self, request, pk=None):
        # Retrieve query parameters
        page_number = request.query_params.get('page_number')
        data_per_page = request.query_params.get('data_per_page')
        search_param = request.query_params.get('search', '')
        drone_category_param = request.query_params.get('drone_category', '')
        drone_category = drone_category_param.split(',') if drone_category_param else []
        sales_status = request.query_params.get('sales_status', '')

        if page_number and data_per_page:
            
            # Paginated response
            drones = Drone.objects.all()

            if search_param:
                drones = drones.filter(
                    Q(drone_name__icontains=search_param) |
                    Q(drone_category_name__icontains=search_param) |
                    Q(market_price__icontains=search_param) |
                    Q(our_price__icontains=search_param) |
                    Q(drone_specification__icontains=search_param) |
                    Q(sales_status__icontains=search_param) |
                    Q(created_date_time__icontains=search_param) |
                    Q(updated_date_time__icontains=search_param)
                )
            if drone_category:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                drones = drones.filter(drone_category__id__in=drone_category_ids).order_by('-id')
            

            if sales_status:
                drones = drones.filter(sales_status=sales_status)

            if search_param and drone_category and sales_status:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                drones = drones.filter(
                    Q(sales_status=sales_status) &
                    Q(drone_name__icontains=search_param) &
                    Q(drone_category__id__in=drone_category_ids)
                )

            if search_param and drone_category:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                drones = drones.filter(
                    Q(drone_name__icontains=search_param) &
                    Q(drone_category__id__in=drone_category_ids)
                )

            if search_param and sales_status:
                drones = drones.filter(
                    Q(sales_status=sales_status) &
                    Q(drone_name__icontains=search_param)
                )

            if drone_category and sales_status:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                drones = drones.filter(
                    Q(sales_status=sales_status) &
                    Q(drone_category__id__in=drone_category_ids)
                )

            # Use Django Paginator for pagination
            paginator = Paginator(drones, data_per_page)
            try:
                paginated_drones = paginator.page(page_number)
            except PageNotAnInteger:
                paginated_drones = paginator.page(1)
            except EmptyPage:
                paginated_drones = paginator.page(paginator.num_pages)

            # Serialize the paginated data
            serializer = DroneSerializer(paginated_drones, many=True)  # Replace with your serializer
            serialized_data = serializer.data
            for drone_data in serialized_data:
                drone_data['thumbnail_image'] = drone_data['thumbnail_image'].replace('/media', '')
            len_of_data = paginator.count

            return Response({
                'result': {
                    'status': 'GET ALL with pagination',
                    'pagination': {
                        'current_page': paginated_drones.number,
                        'number_of_pages': paginator.num_pages,
                        'next_url': self.get_next_url(request, paginated_drones),
                        'previous_url': self.get_previous_url(request, paginated_drones),
                        'has_next': paginated_drones.has_next(),
                        'has_previous': paginated_drones.has_previous(),
                        'has_other_pages': paginated_drones.has_other_pages(),
                        'len_of_data': len_of_data,
                    },
                    'data': serialized_data,
                },
            })
        else:
            # Non-paginated response
            try:
                if pk:
                    # Get drone by ID
                    drone = Drone.objects.get(pk=pk)
                    serializer = DroneSerializer(drone)

                    # Modify the thumbnail_image field to remove the "/media" prefix
                    serialized_data = serializer.data
                    serialized_data['thumbnail_image'] = serialized_data['thumbnail_image'].replace('/media', '')

                    return Response({
                        'result': {
                            'status': 'GET by ID',
                            'data': [serialized_data],
                        },
                    })
                else:
                    # Get all drones without pagination
                    drones = Drone.objects.all()

                    if search_param:
                        drones = drones.filter(
                            Q(drone_name__icontains=search_param) |
                            Q(drone_category_name__icontains=search_param) |
                            Q(market_price__icontains=search_param) |
                            Q(our_price__icontains=search_param) |
                            Q(drone_specification__icontains=search_param) |
                            Q(sales_status__icontains=search_param) |
                            Q(created_date_time__icontains=search_param) |
                            Q(updated_date_time__icontains=search_param)
                        )

                    serialized_drones = DroneSerializer(drones, many=True).data
                    for drone_data in serialized_drones:
                        drone_data['thumbnail_image'] = drone_data['thumbnail_image'].replace('/media', '')
                    len_of_data = len(drones)

                    return Response({
                        'result': {
                            'status': 'GET ALL without pagination',
                            'len_of_data': len_of_data,
                            'data': serialized_drones,
                        },
                    })
            except ObjectDoesNotExist:
                return Response({"message": "Drone not found"}, status=404)

    def get_next_url(self, request, paginated_drones):
        if paginated_drones.has_next():
            return request.build_absolute_uri(
                f"?page_number={paginated_drones.next_page_number}&data_per_page={paginated_drones.paginator.per_page}")
        return None

    def get_previous_url(self, request, paginated_drones):
        if paginated_drones.has_previous():
            return request.build_absolute_uri(
                f"?page_number={paginated_drones.previous_page_number}&data_per_page={paginated_drones.paginator.per_page}")
        return None



    def paginate_response(self, data, page_number, data_per_page):
        if page_number is None and data_per_page is None:
            return Response({'result': {'data': data}})
        else:
            len_of_data = len(data)
            # Initialize MyPagination without passing data
            data_pagination = MyPagination()
            # Use paginate_queryset method to paginate the data
            paginated_data = data_pagination.paginate_queryset(data, self.request)
            # Convert the paginated data to a list
            paginated_data_list = list(paginated_data)
            return Response({
                'result': {
                    'status': 'GET ALL',
                    'pagination': {
                        'current_page': data_pagination.page.number,
                        'number_of_pages': data_pagination.page.paginator.num_pages,
                        'next_url': data_pagination.get_next_link(),
                        'previous_url': data_pagination.get_previous_link(),
                        'has_next': data_pagination.page.has_next(),
                        'has_previous': data_pagination.page.has_previous(),
                        'has_other_pages': data_pagination.page.has_other_pages(),
                        'len_of_data': len_of_data,
                    },
                    'data': paginated_data_list,
                },
            })


    def post(self, request):
        data = request.data
        drone_name = data.get('drone_name')
        drone_category_id = data.get('drone_category_id')
        drone_specification = data.get('drone_specification')
        market_price = data.get('market_price')
        our_price = data.get('our_price')
        thumbnail_image = data.get('thumbnail_image')
        drone_sub_images_base64 = data.get('drone_sub_images')
        sales_status = data.get('sales_status')
        quantity_available = data.get('quantity_available')
        username = data.get('username')
        hsn_number=data.get('hsn_number')
        igstvalue=data.get('igstvalue')
        sgstvalue=data.get('sgstvalue')
        cgstvalue=data.get('cgstvalue')
        units=data.get('units')
        
        units = get_object_or_404(UnitPriceList, units=units)


        if Drone.objects.filter(drone_name=drone_name).exists():
            return Response({"message": "Drone with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

        drone_category = DroneCategory.objects.get(id=drone_category_id)
        converted_thumbnail_image = convertBase64(thumbnail_image, 'drone_name', drone_name, 'thumbnail_images')

     
        drone = Drone.objects.create(
            drone_name=drone_name,
            drone_category=drone_category,
            drone_specification=drone_specification,
            market_price=market_price,
            our_price=our_price,
            thumbnail_image=converted_thumbnail_image,
            sales_status=sales_status,
            quantity_available=quantity_available,
            hsn_number=hsn_number,
            igstvalue= igstvalue,
            sgstvalue= sgstvalue,
            cgstvalue= cgstvalue,
            units=units,

        )

        
        sub_images_list = []
        for item in data.get('drone_sub_images', []):
            if isinstance(item, dict) and 'image' in item:
                image_name = 'image' + str(random.randint(0, 1000))
                sub_image_data = convertBase64(item['image'], image_name, username, "drone_sub_images")
                sub_images_list.append({'image': sub_image_data})

       
        drone.drone_sub_images = sub_images_list
        drone.save()

        return Response({"message": "Drone created successfully!"}, status=status.HTTP_201_CREATED)






    def put(self, request, pk):
        data = request.data
        username = data.get('username')

        try:
            drone = Drone.objects.get(id=pk)
        except Drone.DoesNotExist:
            return Response({"message": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)

        if 'drone_name' in data:
            new_drone_name = data['drone_name']
            if new_drone_name != drone.drone_name and Drone.objects.filter(drone_name=new_drone_name).exists():
                return Response({"message": "Drone with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
            drone.drone_name = new_drone_name

        if 'drone_category_id' in data:
            new_drone_category_id = data['drone_category_id']
            try:
                drone_category = DroneCategory.objects.get(id=new_drone_category_id)
                drone.drone_category = drone_category
            except DroneCategory.DoesNotExist:
                return Response({"message": "Drone category not found."}, status=status.HTTP_400_BAD_REQUEST)

        if 'drone_specification' in data:
            drone.drone_specification = data['drone_specification']

        if 'market_price' in data:
            drone.market_price = data['market_price']

        if 'our_price' in data:
            drone.our_price = data['our_price']

        if 'hsn_number' in data:
            drone.hsn_number=data['hsn_number']

        if 'igstvalue' in data:
            drone.igstvalue=data['igstvalue']

        if 'cgstvalue' in data:
            drone.cgstvalue=data['cgstvalue']

        if 'sgstvalue' in data:
            drone.sgstvalue=data['sgstvalue']
        
        #if 'units' in data:
            #drone.units=data['units']
        if 'units' in data:
            units = data['units']
            try:
                # Try to get the UnitPriceList instance based on the label_name
                units = UnitPriceList.objects.get(units=units)
                drone.units = units
            except UnitPriceList.DoesNotExist:
                return Response({"message": "UnitPriceList not found."}, status=status.HTTP_400_BAD_REQUEST)

        if 'thumbnail_image' in data:
            thumbnail_image_data = data.get('thumbnail_image')

            # Check if the thumbnail_image_data is a URL or base64-encoded data
            if thumbnail_image_data.startswith(('http:', 'https:')):
                thumbnail_image_url = thumbnail_image_data
                thumbnail_image_response = requests.get(thumbnail_image_url)
                if thumbnail_image_response.status_code == 200:
                    content_type = thumbnail_image_response.headers['content-type']
                    extension = content_type.split('/')[-1]
                    image_name = f"{new_drone_name}.{extension}"

                    save_path = os.path.join("thumbnail_images", new_drone_name, image_name)
                    drone.thumbnail_image.save(save_path, ContentFile(thumbnail_image_response.content), save=True)
                else:
                    return Response({"message": "Failed to fetch thumbnail image from the provided URL."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:  # Assume it's base64-encoded data
                image_name = f"{new_drone_name}.png"
                save_path = os.path.join("thumbnail_images", new_drone_name, image_name)
                thumbnail_image_data = base64.b64decode(thumbnail_image_data.split(';base64,')[1])
                drone.thumbnail_image.save(save_path, ContentFile(thumbnail_image_data), save=True)
        if 'sales_status' in data:
            drone.sales_status = data['sales_status']

        if 'quantity_available' in data:
            drone.quantity_available = data['quantity_available']

        drone_sub_images = data.get('drone_sub_images', [])

        sub_images_list = []

        for sub_image_data in drone_sub_images:
            image_data = sub_image_data.get('image', '')
            image_name = 'image' + str(random.randint(0, 1000))
            sub_image_path = self.save_image(drone, image_data, "drone_sub_images", image_name)
            sub_images_list.append({'image': sub_image_path})

        drone.drone_sub_images = sub_images_list

        # ... (rest of the code)
        
        drone.updated_date_time = timezone.now()

        drone.save()

        return Response({"message": "Drone updated successfully!"}, status=status.HTTP_200_OK)

    def save_image(self, drone, image_data, folder_name, image_name):
        if image_data.startswith(('http:', 'https:')):
            image_response = requests.get(image_data)
            if image_response.status_code == 200:
                content_type = image_response.headers['content-type']
                extension = content_type.split('/')[-1]
                image_filename = f"{image_name}.{extension}"
                image_path = os.path.join(folder_name, image_filename)
                save_path = os.path.join("amx-crm/site/public/media", image_path)
                with open(save_path, 'wb') as f:
                    f.write(image_response.content)
            else:
                raise ValueError(f"Failed to fetch {folder_name} image from the provided URL.")
        else:  # Assume it's base64-encoded data
            image_filename = f"{image_name}.png"
            image_path = os.path.join(folder_name, image_filename)
            save_path = os.path.join("amx-crm/site/public/media", image_path)
            image_data = base64.b64decode(image_data.split(';base64,')[1])
            with open(save_path, 'wb') as f:
                f.write(image_data)

        return f'/{image_path}'



    def delete(self, request, pk=None):
        if pk is None:
            drone_ids_param = request.query_params.get('drone_ids', '')
            drone_ids = [int(drone_ids) for drone_ids in drone_ids_param.split(',') if drone_ids]
            if not drone_ids:
                Drone.objects.all().delete()
                return Response({"message": "All drones deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            try:
                drones = Drone.objects.filter(id__in=drone_ids)
                drones.delete()
                return Response({"message": "Selected drones deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except Drone.DoesNotExist:
                return Response({"message": "Drones not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                drone = Drone.objects.get(pk=pk)
                drone.delete()
                return Response({"message": "Drone deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except Drone.DoesNotExist:
                return Response({"message": "Drone not found"}, status=status.HTTP_404_NOT_FOUND)


class SalesStatusAPIview(APIView):
    def put(self, request):
        sales_status = request.data.get("sales_status")
        drone_ids = request.data.get("drone_ids")

        if sales_status is None:
            return Response({"message": "Please provide a new sales status value."}, status=status.HTTP_400_BAD_REQUEST)

        if drone_ids:
            drones = Drone.objects.filter(id__in=drone_ids)
            drones.update(sales_status=sales_status)
            return Response({"message": "Selected drones' sales status updated successfully"},
                            status=status.HTTP_200_OK)
        else:
            
            Drone.objects.update(sales_status=sales_status)
            return Response({"message": "All drones' sales_status updated successfully"}, status=status.HTTP_200_OK)


class SendBulkEmail(APIView):
    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        selected_partner_ids = request.data.get('selected_partners', [])

        try:
            if selected_partner_ids:
                selected_partners = CustomUser.objects.filter(
                    role_id__role_name="Partner",
                    id__in=selected_partner_ids
                )
                selected_partner_emails = selected_partners.values_list('email', flat=True)

                if selected_partner_emails:
                    email = EmailMessage(subject, message, to=selected_partner_emails)
                    email.send()

                    return Response({"message": "Email sent to the selected partners"}, status=status.HTTP_200_OK)
            all_partners = CustomUser.objects.filter(role_id__role_name="Partner")
            partner_emails = all_partners.values_list('email', flat=True)

            if not partner_emails:
                return Response({"message": "No partner users found."}, status=status.HTTP_404_NOT_FOUND)

            if partner_emails:
                email = EmailMessage(subject, message, to=partner_emails)
                email.send()
                return Response({"message": "Email has been sent to all partners."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "Error sending bulk email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ForgotPasswordAPIView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')

        try:
            category = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user = CustomUser.objects.filter(username=username).first()
        


        if user:
            subject = 'Password Reset'
            uid = user.id  
            reset_link = f'https://amx-crm.thestorywallcafe.com/#/reset-password/{uid}/'

            message = f'To reset your password, please click on the following link: {reset_link}\nBest regards,\nAMX-CRM Team'
            sender_email = 'from@example.com'

            send_mail(
                subject,
                message,
                sender_email,
                [user.email],
                fail_silently=False,
            )

            return Response({
                'message': 'Password reset link sent to the user.',
            })
        else:
            return Response({'message': 'User does not exist.'})

class ResetpasswordAPI(APIView):

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = new_password
        user.save()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


class ChangePasswordAPI(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password=data.get('confirm_password')
        passwd = user.password
        if old_password != passwd:
            return Response({"message":"Old password is incorrect"},status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'message': 'New password and confirm password do not match'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.password=new_password
        user.password=confirm_password
        user.save()
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)






def setup_logger():
    logger = logging.getLogger("my_logger")  
    logger.setLevel(logging.DEBUG)  
    return logger



logger = setup_logger()

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import base64

class CompanydetailsAPIView(APIView):
    def get_state_code(self, state_name):
        # Define a dictionary mapping state names to their codes
        state_code_mapping = {
            "Andaman and Nicobar Islands": "35",
            "Andhra Pradesh": "28",
            "Arunachal Pradesh": "12",
            "Assam": "18",
            "Bihar": "10",
            "Chandigarh": "04",
            "Chhattisgarh": "22",
            "Dadra and Nagar Haveli and Daman and Diu": "26",
            "Delhi": "07",
            "Goa": "30",
            "Gujarat": "24",
            "Haryana": "06",
            "Himachal Pradesh": "02",
            "Jharkhand": "20",
            "Karnataka": "29",
            "Kerala": "32",
            "Lakshadweep": "31",
            "Madhya Pradesh": "23",
            "Maharashtra": "27",
            "Manipur": "14",
            "Meghalaya": "17",
            "Mizoram": "15",
            "Nagaland": "13",
            "Odisha": "21",
            "Puducherry": "34",
            "Punjab": "03",
            "Rajasthan": "08",
            "Sikkim": "11",
            "Tamil Nadu": "33",
            "Telangana": "36",
            "Tripura": "16",
            "Uttar Pradesh": "09",
            "Uttarakhand": "05",
            "West Bengal": "19",
            "Jammu and Kashmir": "01",
            "Ladakh": "02",
        }

        # Retrieve the state code from the dictionary
        return state_code_mapping.get(state_name, '')

    def get_location_details(self, pin_code):
        geolocator = Nominatim(user_agent="amxcrm")
        location = geolocator.geocode(pin_code)

        if location:
            raw_data = location.raw
            print(raw_data, "Raw Data")

            display_name = raw_data.get('display_name', '')
            print(display_name, "Display Name")

            # Extracting information from display_name
            parts = display_name.split(', ')
            state = parts[-2]
            city = parts[-3]
            country = parts[-1]

            # Retrieve state code using the predefined mapping
            state_code = self.get_state_code(state)
            print(state_code, "State Code")

            return {
                'state': state,
                'state_code': state_code,
                'city': city,
                'country': country
            }

        return None

    def post(self, request, pk):
        server_address = "https://amx-crm.thestorywallcafe.com"
        data = request.data
        media_url = settings.MEDIA_URL

        try:
            partner = CustomUser.objects.get(pk=pk)
            if partner.status is True:
                super_admin_role = Role.objects.filter(role_name="Super_admin").first()
                if super_admin_role:
                    super_admin = super_admin_role.customuser_set.first()
                    super_admin_email = super_admin.email if super_admin else None

                    if not super_admin_email:
                        return Response({"message": "Super admin email not found"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    requested_changes = {}
                    new_changes = {}
                    signature_name = ''  # Initialize the variable here

                    fields_to_check = ["company_name", "company_email", "shipping_address", "billing_address",
                                       "company_phn_number", "company_gst_num", "company_cin_num", "pan_number",
                                       "reason", "shipping_pincode", "billing_pincode", "user_signature"]

                    for field in fields_to_check:
                        old_value = getattr(partner, field)
                        new_value = data.get(field)

                        if old_value != new_value:
                            if field == "user_signature":
                                try:
                                    characters = string.ascii_letters + string.digits
                                    random_string = ''.join(random.choice(characters) for _ in range(10))
                                    format, imgstr = new_value.split(';base64,')
                                    ext = format.split('/')[-1]
                                    signature_name = f'signature_{random_string}.{ext}'
                                    data = ContentFile(base64.b64decode(imgstr), name=signature_name)
                                except Exception as e:
                                    print(f"Error saving signature image: {e}")

                                requested_changes[field] = {"old": server_address + media_url + str(old_value),
                                                            "new": server_address + media_url + signature_name}
                            else:
                                requested_changes[field] = {"old": old_value, "new": new_value}
                            new_changes[field] = new_value
                    print(new_changes,"nwwwwwwwwwwwwwwwwwwwwwwwwwww")


                    change = ChangeRequestCompanyDetails.objects.create(**new_changes, created_by=pk)
                    print(signature_name,"ccccccccccccccccccccccccccccc")
                    change.user_signature.save(signature_name, data, save=True)
                    approve_url = request.build_absolute_uri(reverse('approve_request', kwargs={'pk': change.id}))
                    reject_url = request.build_absolute_uri(reverse('reject_request', kwargs={'pk': change.id}))

                    logger.debug(f"Generated 'approve' URL: {approve_url}")
                    logger.debug(f"Generated 'reject' URL: {reject_url}")

                    email_content = render_to_string('email/partner_update_request_email.html', {
                        'requested_changes': requested_changes,
                        "user_signature": server_address + media_url + signature_name,  # Use signature_name directly
                        'approve_url': approve_url,
                        'reject_url': reject_url,
                        'user_id': change.id
                    })

                    send_mail(
                        'Partner Update Request',
                        strip_tags(email_content),
                        'amxdrone123@gmail.com',
                        [super_admin_email],
                        fail_silently=False,
                        html_message=email_content,
                    )

                    return Response({"message": "Update request sent to the super admin"},
                                    status=status.HTTP_200_OK)
            else:

                company_name = data.get('company_name')
                company_email = data.get('company_email')
                shipping_address = data.get('shipping_address')
                billing_address = data.get('billing_address')
                shipping_pincode = data.get('shipping_pincode')
                billing_pincode = data.get('billing_pincode')
                company_phn_number = data.get('company_phn_number')
                company_gst_num = data.get('company_gst_num')
                company_cin_num = data.get('company_cin_num')
                pan_number = data.get('pan_number')
                company_logo = request.FILES.get('company_logo')
                company_logo = data.get('company_logo')
                username = data.get('username')
                signature_data = data.get('user_signature')

                partner.company_name = company_name
                partner.company_email = company_email
                partner.shipping_address = shipping_address
                partner.billing_address = billing_address
                partner.shipping_pincode = shipping_pincode
                partner.billing_pincode = billing_pincode
                partner.company_phn_number = company_phn_number
                partner.company_gst_num = company_gst_num
                partner.company_cin_num = company_cin_num
                partner.pan_number = pan_number

                shipping_location_details = self.get_location_details(shipping_pincode)
                if shipping_location_details:
                    partner.shipping_state = shipping_location_details['state']
                    partner.shipping_state_city = shipping_location_details['city']
                    partner.shipping_state_country = shipping_location_details['country']
                    partner.shipping_state_code = shipping_location_details['state_code']

                # Fetch and update billing location details
                billing_location_details = self.get_location_details(billing_pincode)
                if billing_location_details:
                    partner.billing_state = billing_location_details['state']
                    partner.billing_state_city = billing_location_details['city']
                    partner.billing_state_country = billing_location_details['country']
                    partner.billing_state_code = billing_location_details['state_code']

                if "company_logo" in request.data:
                    company_logo_base64 = request.data["company_logo"]
                    converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username,
                                                                  'company_logos')

                    if converted_company_logo_base64:
                        converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                        file_path = f"/company_logos/{partner.username}companylogo.png"
                        partner.company_logo.save(f"{partner.username}companylogo.png",
                                                  ContentFile(converted_company_logo_base64), save=True)
                        partner.company_logo.name = file_path

                if signature_data:
                    try:
                        format, imgstr = signature_data.split(';base64,')
                        ext = format.split('/')[-1]
                        signature_name = f'signature_{uuid.uuid4()}.{ext}'
                        data = ContentFile(base64.b64decode(imgstr), name=signature_name)
                        partner.user_signature.save(signature_name, data, save=True)
                    except Exception as e:
                        print(f"Error saving signature image: {e}")

                partner.status = True
                partner.updated_date_time_company = timezone.now()
                partner.save()

                return Response({"message": "Company details updated successfully"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)


def get_state_code(state_name):
    # Define a dictionary mapping state names to their codes
    state_code_mapping = {
        "Andaman and Nicobar Islands": "35",
        "Andhra Pradesh": "28",
        "Arunachal Pradesh": "12",
        "Assam": "18",
        "Bihar": "10",
        "Chandigarh": "04",
        "Chhattisgarh": "22",
        "Dadra and Nagar Haveli and Daman and Diu": "26",
        "Delhi": "07",
        "Goa": "30",
        "Gujarat": "24",
        "Haryana": "06",
        "Himachal Pradesh": "02",
        "Jharkhand": "20",
        "Karnataka": "29",
        "Kerala": "32",
        "Lakshadweep": "31",
        "Madhya Pradesh": "23",
        "Maharashtra": "27",
        "Manipur": "14",
        "Meghalaya": "17",
        "Mizoram": "15",
        "Nagaland": "13",
        "Odisha": "21",
        "Puducherry": "34",
        "Punjab": "03",
        "Rajasthan": "08",
        "Sikkim": "11",
        "Tamil Nadu": "33",
        "Telangana": "36",
        "Tripura": "16",
        "Uttar Pradesh": "09",
        "Uttarakhand": "05",
        "West Bengal": "19",
        "Jammu and Kashmir": "01",
        "Ladakh": "02",
    }

    # Retrieve the state code from the dictionary
    return state_code_mapping.get(state_name, '')

def get_location_details(pin_code):
    geolocator = Nominatim(user_agent="amxcrm")
    location = geolocator.geocode(pin_code)

    if location:
        raw_data = location.raw
        display_name = raw_data.get('display_name', '')

        parts = display_name.split(', ')
        state = parts[-2]
        city = parts[-3]
        country = parts[-1]

        state_code = get_state_code(state)
        print(state_code, "State Code")

        return {
            'state': state,
            'state_code': state_code,
            'city': city,
            'country': country
        }

    return None

def approveRequest(request, id):
    partner = ChangeRequestCompanyDetails.objects.get(id=id)
    if not partner.status:
        profile = CustomUser.objects.get(pk=partner.created_by)
        fields_to_check = ["company_name", "company_email", "shipping_address", "billing_address", "company_logo",
                           "company_phn_number", "company_gst_num", "company_cin_num", "pan_number", "reason",
                           "shipping_pincode", "billing_pincode", "user_signature"]
        print(fields_to_check, 'fields_to_check')

        for field in fields_to_check:
            old_value = getattr(partner, field)
            print('old_value', old_value)

            if old_value:
                setattr(profile, field, old_value)

            if field == "user_signature" and partner.user_signature:
                # Use the same image name as used while saving the ChangeRequestCompanyDetails
                signature_name = partner.user_signature.name
                new_signature = ContentFile(partner.user_signature.read())
                profile.user_signature.save(signature_name, new_signature)
                print(f"User signature updated to {signature_name}")

            if field == "company_logo" and partner.company_logo:
                new_logo = ContentFile(partner.company_logo.read())
                profile.company_logo.save(partner.company_logo.name, new_logo)
                print(f"Company logo updated to {partner.company_logo.name}")

        shipping_pincode = profile.shipping_pincode
        shipping_location_details = get_location_details(shipping_pincode)
        if shipping_location_details:
            profile.shipping_state = shipping_location_details['state']
            profile.shipping_state_code = shipping_location_details['state_code']
            profile.shipping_state_city = shipping_location_details['city']
            profile.shipping_state_country = shipping_location_details['country']

        # Fetch and update billing location details
        billing_pincode = profile.billing_pincode
        billing_location_details = get_location_details(billing_pincode)
        if billing_location_details:
            profile.billing_state = billing_location_details['state']
            profile.billing_state_code = billing_location_details['state_code']
            profile.billing_state_city = billing_location_details['city']
            profile.billing_state_country = billing_location_details['country']

        profile.save()
        print('profile', profile)

        partner.approved = True
        partner.status = True
        partner.save()

        subject = "Your Update Request has been Approved"
        message = "Your update request has been approved by the admin."
        from_email = "amxdrone123@gmail.com"
        recipient_list = [profile.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return HttpResponse({'Status approved successfully'})
    else:
        return HttpResponse({'Already responded'})


# def approveRequest(request, id):
#     partner = ChangeRequestCompanyDetails.objects.get(id=id)
#     if not partner.status:
#         profile = CustomUser.objects.get(pk=partner.created_by)
#         fields_to_check = ["company_name", "company_email", "shipping_address", "billing_address", "company_logo",
#                            "company_phn_number", "company_gst_num", "company_cin_num", "pan_number", "reason",
#                            "shipping_pincode", "billing_pincode", "user_signature"]
#         print(fields_to_check, 'fields_to_check')

#         for field in fields_to_check:
#             old_value = getattr(partner, field)
#             print('old_value', old_value)

#             if old_value:
#                 setattr(profile, field, old_value)

#             if field == "user_signature" and partner.user_signature:
#                 # Use the same image name as used while saving the ChangeRequestCompanyDetails
#                 signature_name = partner.user_signature.name
#                 new_signature = ContentFile(partner.user_signature.read())
#                 profile.user_signature.save(signature_name, new_signature)
#                 print(f"User signature updated to {signature_name}")

#             if field == "company_logo" and partner.company_logo:
#                 new_logo = ContentFile(partner.company_logo.read())
#                 profile.company_logo.save(partner.company_logo.name, new_logo)
#                 print(f"Company logo updated to {partner.company_logo.name}")

#         shipping_pincode = profile.shipping_pincode
#         shipping_location_details = get_location_details(shipping_pincode)
#         if shipping_location_details:
#             profile.shipping_state = shipping_location_details['state']
#             profile.shipping_state_code = shipping_location_details['state_code']
#             profile.shipping_state_city = shipping_location_details['city']
#             profile.shipping_state_country = shipping_location_details['country']

#         # Fetch and update billing location details
#         billing_pincode = profile.billing_pincode
#         billing_location_details = get_location_details(billing_pincode)
#         if billing_location_details:
#             profile.billing_state = billing_location_details['state']
#             profile.billing_state_code = billing_location_details['state_code']
#             profile.billing_state_city = billing_location_details['city']
#             profile.billing_state_country = billing_location_details['country']

#         profile.save()
#         print('profile', profile)

#         partner.approved = True
#         partner.status = True
#         partner.save()

#         subject = "Your Update Request has been Approved"
#         message = "Your update request has been approved by the admin."
#         from_email = "amxdrone123@gmail.com"
#         recipient_list = [profile.email]

#         send_mail(subject, message, from_email, recipient_list, fail_silently=False)

#         return HttpResponse({'Status approved successfully'})
#     else:
#         return HttpResponse({'Already responded'})


def RejectRequest(request, id):
    partner = ChangeRequestCompanyDetails.objects.get(id=id)
    profile = CustomUser.objects.get(pk=partner.created_by)

    if not partner.status:
        partner.status = True
        partner.save()
        subject = "Your Update Request has been Rejected"
        message = "Your update request has been rejected by the admin."
        from_email = "amxdrone123@gmail.com"
        recipient_list = [profile.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponse({'Status rejected successfully'})
    else:
        return HttpResponse({'Already responded'})

from datetime import datetime
class DroneSalesPaymentAPI(APIView):
    def post(self, request):
        data = request.data
        payment_gateway_price = data.get('payment_gateway_price')
        description = data.get('description')

        existing_payment_gateway = Payment_gateways.objects.first()

        if existing_payment_gateway:
            return Response({'message': 'Data is already present.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Payment_gateways.objects.create(
                payment_gateway_price=payment_gateway_price,
                description=description
            )
            return Response({'message': 'Item added to cart successfully!'}, status=status.HTTP_201_CREATED)


    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        pk = kwargs.get('pk')  # Retrieve pk from URL parameters

        if id is not None:
            status = Payment_gateways.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'payment_gateway_price': status.payment_gateway_price,'description':status.description,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        elif pk is not None:
            status = Payment_gateways.objects.filter(id=pk).first()  # Use pk instead of id
            if status:
                data = {'id': status.id, 'payment_gateway_price': status.payment_gateway_price,'description':status.description,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        else:
            data = Payment_gateways.objects.all().values()
            return Response(data)

    def put(self, request, pk):
        data = request.data
        payment_gateway_price = data.get('payment_gateway_price')
        description = data.get('description')
        created_date_time_str = data.get('created_date_time')
        updated_date_time_str = data.get('updated_date_time')

        try:
            payment_gateway_instance = Payment_gateways.objects.get(id=pk)

            payment_gateway_instance.payment_gateway_price = payment_gateway_price
            payment_gateway_instance.description = description
            payment_gateway_instance.updated_date_time = datetime.now()
            payment_gateway_instance.save()

            return Response({'message': 'Payment gateway updated successfully'})
        except Payment_gateways.DoesNotExist:
            return Response({'message': 'Payment gateway ID not found'}, status=status.HTTP_404_NOT_FOUND)



class Partner_slotAPI(APIView):
    def post(self, request):
        data = request.data
        slot_price = data.get('slot_price')
        description = data.get('description')

        existing_slot = Partner_slot.objects.first()

        if existing_slot:

            return Response({'message': 'Data is already present.'}, status=status.HTTP_400_BAD_REQUEST)
        else:

            Partner_slot.objects.create(
                slot_price=slot_price,
                description=description
            )
            return Response({'message': 'Partner slot price added!!'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        id = request.query_params.get('id')

        if id:
            slot = Partner_slot.objects.filter(id=id).first()
            if slot:
                return Response({
                    'id': slot.id,
                    'slot_price': slot.slot_price,
                    'description': slot.description
                })
            else:
                return Response({'message': 'Slot not found.'}, status=404)
        else:
            slots = Partner_slot.objects.all()
            slot_list = [
                {
                    'id': s.id,
                    'slot_price': s.slot_price,
                    'description': s.description
                }
                for s in slots
            ]
            return Response(slot_list)

    def put(self, request, pk):
        data = request.data
        slot_price = data.get('slot_price')
        description = data.get('description')

        if Partner_slot.objects.filter(id=pk).exists():
            Partner_slot.objects.filter(id=pk).update(
                slot_price=slot_price, description=description)
            return Response({'message': 'Slot price updated successfully!'})
        else:
            return Response({'message': 'ID not found!'})


class PaymentLinksAPI(APIView):
    def post(self, request):
        data = request.data
        payment_link_price = data.get('payment_link_price')
        description = data.get('description')

        existing_payment_link = PaymentLinks.objects.first()

        if existing_payment_link:

            return Response({'message': 'Data is already present.'}, status=status.HTTP_400_BAD_REQUEST)
        else:

            PaymentLinks.objects.create(
                payment_link_price=payment_link_price,
                description=description
            )
            return Response({'message': 'Paymentlink price added successfully!'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        id = request.query_params.get('id')

        if id:
            payment_link = PaymentLinks.objects.filter(id=id).first()
            if payment_link:
                return Response({
                    'id': payment_link.id,
                    'payment_link_price': payment_link.payment_link_price,
                    'description': payment_link.description
                })
            else:
                return Response({'message': 'Payment link not found.'}, status=404)
        else:
            payment_links = PaymentLinks.objects.all()
            payment_link_list = [
                {
                    'id': pl.id,
                    'payment_link_price': pl.payment_link_price,
                    'description': pl.description
                }
                for pl in payment_links
            ]
            return Response(payment_link_list)

    def put(self, request, pk):
        data = request.data
        payment_link_price = data.get('payment_link_price')
        description = data.get('description')

        if PaymentLinks.objects.filter(id=pk).exists():
            PaymentLinks.objects.filter(id=pk).update(
                payment_link_price=payment_link_price, description=description)
            return Response({'message': 'Payment link price updated successfully!'})
        else:
            return Response({'message': 'ID not found!'})


class Slot_batch_rangeAPI(APIView):
    def post(self, request):
        data = request.data
        minimum_slot_size = data.get('minimum_slot_size')
        maximum_slot_size = data.get('maximum_slot_size')
        description = data.get('description')

        existing_slot = Slot_batch_range.objects.first()

        if existing_slot:

            return Response({'message': 'Data is already present.'}, status=status.HTTP_400_BAD_REQUEST)
        else:

            Slot_batch_range.objects.create(
                minimum_slot_size=minimum_slot_size,
                maximum_slot_size=maximum_slot_size,
                description=description
            )
            return Response({'message': 'Slot batch range added successfully!'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        id = request.query_params.get('id')

        if id:
            slot = Slot_batch_range.objects.filter(id=id).first()
            if slot:
                return Response({
                    'id': slot.id,
                    'minimum_slot_size': slot.minimum_slot_size,
                    'maximum_slot_size': slot.maximum_slot_size,
                    'description': slot.description
                })
            else:
                return Response({'message': 'Slot not found.'}, status=404)
        else:
            slots = Slot_batch_range.objects.all()
            slot_list = [
                {
                    'id': s.id,
                    'minimum_slot_size': s.minimum_slot_size,
                    'maximum_slot_size': s.maximum_slot_size,
                    'description': s.description
                }
                for s in slots
            ]
            return Response(slot_list)

    def put(self, request, pk):
        data = request.data
        minimum_slot_size = data.get('minimum_slot_size')
        maximum_slot_size = data.get('maximum_slot_size')
        description = data.get('description')

        if Slot_batch_range.objects.filter(id=pk).exists():
            slot_batch = Slot_batch_range.objects.get(id=pk)
            slot_batch.minimum_slot_size = minimum_slot_size
            slot_batch.maximum_slot_size = maximum_slot_size
            slot_batch.description = description
            slot_batch.save()
            return Response({'message': 'Slot batch range updated successfully!'})
        else:
            return Response({'message': 'ID not found!'})


class AddToCart(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        drone_id = data.get('drone_id')
        role_id = data.get('role_id')
        quantity = data.get('quantity')

        ids_param = request.query_params.get('id', '')
        ids = [int(id_) for id_ in ids_param.split(',') if id_.isdigit()]

        if ids:
            
            drone_sales = DroneSales.objects.filter(id__in=ids)
            deleted_count, _ = drone_sales.delete()

            if deleted_count > 0:
                return Response({'message': f'{deleted_count} Items deleted from cart'})
            else:
                return Response({'message': 'No matching IDs found for deletion'}, status=status.HTTP_404_NOT_FOUND)

        
        if not (user_id and drone_id and role_id and quantity):
            return Response({"message": "Required fields are missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
            drone = Drone.objects.get(id=drone_id)
            role = Role.objects.get(id=role_id)
        except (CustomUser.DoesNotExist, Drone.DoesNotExist, Role.DoesNotExist):
            return Response({"message": "User, Drone, or Role not found."}, status=status.HTTP_404_NOT_FOUND)

        if quantity < 1:
            return Response({"message": "Invalid quantity requested."}, status=status.HTTP_400_BAD_REQUEST)

    
        existing_drone_sales = DroneSales.objects.filter(user=user, drone_id=drone, role=role).first()

        if existing_drone_sales:
            return Response({"message": "Duplicate entry attempted."}, status=status.HTTP_409_CONFLICT)
        else:
            custom_amounts = CustomizablePrice.objects.all()

            custom_price_instance = custom_amounts.first()
            print(custom_price_instance)

            drone_sales = DroneSales.objects.create(
                user=user,
                drone_id=drone,
                role=role,
                quantity=quantity,
                custom_price = custom_price_instance

            )
            return Response({"message": "Dronesales created successfully!"}, status=status.HTTP_201_CREATED)


    def get(self, request):
        user_id = request.query_params.get('user_id')
        custom_amounts = CustomizablePrice.objects.all()

        if user_id is not None:
            try:
                drone_sales = DroneSales.objects.filter(user_id=user_id)
                data = []

                for sale in drone_sales:
                    user_id = sale.user.id if sale.user else None
                    drone_id = sale.drone_id.id if sale.drone_id else None
                    role_id = sale.role.id if sale.role else None
                    quantity = sale.quantity
                    checked=sale.checked
                    custom_price_amount = sale.custom_price.custom_amount if sale.custom_price else None
                    # print(custom_price_amount, "cccccccccccnnnnnnnnnn")

                    drone_details = {}
                    if sale.drone_id:
                        thumbnail_image = sale.drone_id.thumbnail_image.url if sale.drone_id.thumbnail_image else None
                        thumbnail_image = thumbnail_image.replace("/media", "") if thumbnail_image else None
                        drone_details = {
                            'drone_name': sale.drone_id.drone_name,
                            'drone_category': sale.drone_id.drone_category.category_name if sale.drone_id.drone_category else None,
                            'drone_specification': sale.drone_id.drone_specification,
                            'market_price': sale.drone_id.market_price,
                            'our_price': sale.drone_id.our_price,
                            'thumbnail_image': thumbnail_image,
                            'drone_sub_images': sale.drone_id.drone_sub_images,
                            'sales_status': sale.drone_id.sales_status,
                            'created_date_time': sale.drone_id.created_date_time,
                            'updated_date_time': sale.drone_id.updated_date_time,
                            'quantity_available': sale.drone_id.quantity_available,
                        }

                    data.append({
                        'id': sale.id,
                        'user_id': user_id,
                        'drone_id': drone_id,
                        'role_id': role_id,
                        'quantity': quantity,
                        'checked':checked,
                        # 'custom_price': custom_price_amount,
                        'drone_details': drone_details,
                    })
            except DroneSales.DoesNotExist:
                return Response({"message": "DroneSales not found for the specified user_id"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Missing user_id parameter"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'cart_items': data, 'custom_price': custom_amounts[0].custom_amount if custom_amounts else None}, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        data = request.data
        drone_id = data.get('drone_id')
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        quantity = data.get('quantity')
        checked = data.get('checked')
        ids = data.get('ids', [])

        # If 'ids' parameter is present, update 'checked' status for multiple instances
        if ids:
            if not all(isinstance(i, int) for i in ids):
                return Response({'message': 'Invalid IDs provided for update.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update 'checked' status for multiple instances
            DroneSales.objects.filter(id__in=ids).update(checked=checked)

            return Response({'message': 'Updated checked status for multiple instances successfully.'})

        # If 'pk' parameter is present, update a single instance
        elif pk and DroneSales.objects.filter(id=pk).exists():
            DroneSales.objects.filter(id=pk).update(
                drone_id=drone_id,
                user_id=user_id,
                role_id=role_id,
                quantity=quantity,
                checked=checked
            )

            return Response({'message': 'Updated checked status for a single instance successfully.'})

        else:
            return Response({'message': 'Invalid request. Provide either "ids" or a valid "pk".'}, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request):
        ids_param = request.query_params.get('id', '')

        ids = [int(id_) for id_ in ids_param.split(',') if id_.isdigit()]


        if not ids:
            return Response({'message': 'No valid IDs provided for deletion'}, status=status.HTTP_400_BAD_REQUEST)

        drone_sales = DroneSales.objects.filter(id__in=ids)
        deleted_count, _ = drone_sales.delete()

        if deleted_count > 0:
            return Response({'message': f'{deleted_count} Items deleted from cart'})
        else:
            return Response({'message': 'No matching IDs found for deletion'}, status=status.HTTP_404_NOT_FOUND)



class DroneCountAPI(APIView):
    def put(self,request,pk):
        data=request.data
        drone_id=data.get('drone_id')
        user_id=data.get('user_id')
        quantity_available=data.get('quantity_available')
        id = data.get('id')
        if Drone.objects.filter(id=pk).exists():
            drone=Drone.objects.get(id=pk)
            drone.drone_id=drone_id
            drone.user_id=user_id
            drone.quantity_available=quantity_available
            drone.save()
            return Response({'message':'Drone count updated!!'})
        else:
            return Response({'error':'id not found'})


class StatusAPI(APIView):
    def get(self, request):
        id = request.query_params.get('id')

        if id is not None:
            status = Status.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'status_name': status.status_name}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        else:
            data = Status.objects.all().values()
            return Response({'Result': data})

    def post(self, request):
        data = request.data
        status_name = data.get('status_name')

        if Status.objects.filter(status_name=status_name).exists():
            return Response({'message': 'order status name is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_status = Status.objects.create(status_name=status_name)
            return Response({'result': 'order status is created successfully!'}, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        data = request.data
        status_name = data.get('status_name')

        try:
            status_instance = Status.objects.get(id=pk)

            if Status.objects.filter(status_name=status_name).exclude(id=pk).exists():
                return Response({'message': 'Status name already exists. Choose a different name.'},
                                status=status.HTTP_400_BAD_REQUEST)

            status_instance.status_name = status_name
            status_instance.updated_date_time = datetime.now()
            status_instance.save()

            return Response({'message': 'Order status updated successfully'})
        except Status.DoesNotExist:
            return Response({'message': 'Order status ID not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,pk):
        data=request.data
        status_name=data.get('status_name')

        if Status.objects.filter(id=pk).exists():
            data=Status.objects.filter(id=pk).delete(status_name=status_name)
            return Response({'message':'Status deleted!!'})
        else:
            return Response({'result':'status Id not found!!'})

class PaymentStatusAPI(APIView):
    def get(self, request):
        id = request.query_params.get('id')

        if id is not None:
            status = PaymentStatus.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'name': status.name}
                return Response(data)
            else:
                return Response({'message': 'Status not found for the specified id'}, status=404)
        else:
            data = PaymentStatus.objects.all().values()
            return Response({'Result': data})

    def post(self, request):
        data = request.data
        name = data.get('name')

        if PaymentStatus.objects.filter(name=name).exists():
            return Response({'message': 'Status_name is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_status = PaymentStatus.objects.create(name=name)
            return Response({'result': 'Status is created successfully!'}, status=status.HTTP_201_CREATED)

    def put(self,request,pk):
        data=request.data
        name=data.get('name')

        if PaymentStatus.objects.filter(id=pk).exists():
            data=PaymentStatus.objects.filter(id=pk).update(name=name)
            return Response({'message':'Status Updated!!'})
        else:
            return Response({'message':'Status id not found!!'})

    def delete(self,request,pk):
        data=request.data
        name=data.get('name')

        if PaymentStatus.objects.filter(id=pk).exists():
            data=PaymentStatus.objects.filter(id=pk).delete(name=name)
            return Response({'message':'Status deleted!!'})
        else:
            return Response({'result':'status id not found!!'})

class CreateOrderAPI(APIView):
    def post(self, request, *args, **kwargs):
        drone_id = request.data.get('drone_id')
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        try:
            drone_instance = Drone.objects.get(id=drone_id)
            user_instance = CustomUser.objects.get(id=user_id)
        except Drone.DoesNotExist:
            return Response({"message": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({'amount':'5000', 'currency': 'INR', 'payment_capture': '1'})

        order = Order.objects.create(drone_id=drone_instance, user_id=user_instance, amount=amount)
        order.order_id = razorpay_order['id']
        order.save()

        response_data = {
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class MydronesAPI(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        id_param = request.query_params.get('id')
        page_number = request.query_params.get('page_number')
        data_per_page = request.query_params.get('data_per_page')
        pagination = request.query_params.get('pagination')
        search_param = request.query_params.get('search', '')
        drone_category_param = request.query_params.get('drone_category', '')
        drone_category = drone_category_param.split(',') if drone_category_param else []
        order_status = request.query_params.get('order_status', '')

        orders = Order.objects.all()
        #orders = Order.objects.exclude(order_status__isnull=True).order_by('-id')
        print(orders,"oooooooooo")

        if search_param:
            orders = orders.filter(
                Q(drone_id__drone_name__icontains=search_param) |
                Q(order_id__icontains=search_param) |
                Q(quantity__icontains=search_param) |
                Q(order_status__status_name__icontains=search_param) |
                Q(drone_id__drone_category__category_name__icontains=search_param) |
                Q(drone_id__market_price__icontains=search_param) |
                Q(drone_id__our_price__icontains=search_param) |
                Q(drone_id__drone_specification__icontains=search_param) |
                Q(drone_id__sales_status__icontains=search_param) |
                Q(created_date_time__icontains=search_param) |
                Q(updated_date_time__icontains=search_param)
            )
        if drone_category:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(drone_id__drone_category__id__in=drone_category_ids).order_by('-id')

        if order_status:
            orders = orders.filter(order_status__status_name=order_status)

        if user_id:
            orders=orders.filter(user_id__id=user_id)

        if search_param and drone_category and order_status and user_id:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(drone_id__drone_name__icontains=search_param) &
                Q(user_id__id=user_id) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )
        if search_param and drone_category and order_status :
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(drone_id__drone_name__icontains=search_param) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )
        if search_param and drone_category:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(drone_id__drone_name__icontains=search_param) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )

        if search_param and drone_category and user_id:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(drone_id__drone_name__icontains=search_param) &
                Q(user_id__id=user_id) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )

        if search_param and order_status:
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(drone_id__drone_name__icontains=search_param)
            )

        if search_param and order_status and user_id:
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(user_id__id=user_id) &
                Q(drone_id__drone_name__icontains=search_param)
            )

        if drone_category and order_status and user_id:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(user_id__id=user_id) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )

        if drone_category and order_status:
            drone_category_ids = [int(category_id) for category_id in drone_category]
            orders = orders.filter(
                Q(order_status__status_name=order_status) &
                Q(drone_id__drone_category__id__in=drone_category_ids)
            )
        return self.paginate_response(request, orders, page_number, data_per_page)
      
    def paginate_response(self, request, queryset, page_number, data_per_page):
        paginator = Paginator(queryset, data_per_page)

        try:
            paginated_data = paginator.page(page_number)
        except EmptyPage:
            return Response({"message": "No results found for the given page number"}, status=404)

        serialized_data = OrderSerializer(paginated_data, many=True).data
        len_of_data = paginator.count
        

        return Response({
            'result': {
                'status': 'GET ALL with pagination',
                'pagination': {
                    'current_page': paginated_data.number,
                    'number_of_pages': paginator.num_pages,
                    'next_url': self.get_next_url(request, paginated_data),
                    'previous_url': self.get_previous_url(request, paginated_data),
                    'has_next': paginated_data.has_next(),
                    'has_previous': paginated_data.has_previous(),
                    'has_other_pages': paginated_data.has_other_pages(),
                    'len_of_data': len_of_data,
                },
                'data': serialized_data,
            },
            
        })

    def get_next_url(self, request, paginated_data):
        if paginated_data.has_next():
            return request.build_absolute_uri(
                f"?page_number={paginated_data.next_page_number}&data_per_page={paginated_data.paginator.per_page}")
        return None

    def get_previous_url(self, request, paginated_data):
        if paginated_data.has_previous():
            return request.build_absolute_uri(
                f"?page_number={paginated_data.previous_page_number}&data_per_page={paginated_data.paginator.per_page}")
        return None

class CustomizablePriceAPIView(APIView):
    def put(self, request, *args, **kwargs):
        
        customizable_price = CustomizablePrice.objects.first()

        if not customizable_price:
            return Response({'error': 'CustomizablePrice does not exist.'}, status=status.HTTP_404_NOT_FOUND)

      
        custom_amount = request.data.get('custom_amount', None)

        if custom_amount is not None:
            customizable_price.custom_amount = custom_amount
            customizable_price.save()

            return Response({'message': 'CustomizablePrice updated successfully.'})

        return Response({'message': 'No data provided for update.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def razorpay_payment(request):
    if request.method == 'POST':
        drone_id = request.data.get('drone_id')
        partner_id = request.data.get('partner_id')
        quantity = request.data.get('quantity')

        try:
            drone = Drone.objects.get(id=drone_id)
        except Drone.DoesNotExist:
            return Response({"message": "Drone not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            partner = CustomUser.objects.get(id=partner_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        customizable_price = CustomizablePrice.objects.first()

        if customizable_price:
            amount_in_paise = int(float(customizable_price.custom_amount))

           
            razorpay_order = client.order.create({'amount': amount_in_paise, 'currency': 'INR'})
            razorpay_order_id = razorpay_order.get('id')

            response_data = {
                'order_id': razorpay_order_id,
                'total_amount': amount_in_paise,
                'currency': 'INR',
                'quantity': quantity
            }
            drone_instance = Drone.objects.get(id=drone_id)
            drone_our_price = float(drone_instance.our_price)

            user_instance = CustomUser.objects.get(id=partner_id)

            
            order = Order.objects.create(
                drone_id=drone_instance,
                user_id=user_instance,
                order_id=razorpay_order_id,
                updated_date_time=datetime.today(), quantity=quantity, amount=drone_our_price
            )


            return JsonResponse(response_data)

        return JsonResponse({'message': 'CustomizablePrice is not available.'}, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({'message': 'Invalid request method'}, status=status.HTTP_404_NOT_FOUND)




@csrf_exempt
def checkout(request):

    if request.method == 'POST':

        partner_id = request.GET.get('partner_id')

        cart_ids_param = request.GET.get('cart_ids')
        #cart_ids = [int(cart_id) for cart_id in cart_ids_param.strip('[]').split(',')]
        cart_ids = [int(cart_id) if cart_id else 0 for cart_id in cart_ids_param.strip('[]').split(',')]
        selected_items = DroneSales.objects.filter(user_id=partner_id, id__in=cart_ids)
        print(selected_items,"sssssssssssssssss")


        selected_cart_ids_param = request.GET.get('selected_cart_ids')

        cart_items = DroneSales.objects.filter(user_id=partner_id)

        if cart_ids_param:
            print("if cartttttttt")
            try:
                cart_ids = [int(cart_id) for cart_id in cart_ids_param.strip('[]').split(',')]
                cart_items = cart_items.filter(id__in=cart_ids)
                # selected_items = DroneSales.objects.filter(user_id=partner_id, id__in=cart_ids)
                print(selected_items)
            except ValueError:
                return JsonResponse({'message': 'Invalid cart_ids parameter'}, status=400)

        # selected_items = DroneSales.objects.filter(user_id=partner_id,id__in=cart_ids_param)

        if selected_cart_ids_param:
            try:
                selected_cart_ids = [int(cart_id) for cart_id in selected_cart_ids_param.strip('[]').split(',')]
                selected_items = selected_items.filter(id__in=selected_cart_ids)
            except ValueError:
                return JsonResponse({'message': 'Invalid selected_cart_ids parameter'}, status=400)

        # all_items = cart_items.union(selected_items)


        total_amount = sum(
            (float(item.drone_id.our_price) if item.drone_id.our_price else 0)
            * item.quantity
            for item in selected_items
        )

        customizable_price = CustomizablePrice.objects.first()
        if customizable_price:
            paid_amount = float(customizable_price.custom_amount)
        else:
            return JsonResponse({'message': 'CustomizablePrice is not available.'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({'amount': int(paid_amount * 100), 'currency': 'INR'})

        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['total_amount'] = paid_amount


        for item in selected_items:
            user_instance = CustomUser.objects.get(id=partner_id)
            drone_sales_entry = DroneSales.objects.get(id=item.id)
            quantity = drone_sales_entry.quantity

            Order.objects.create(
                amount=(
                    float(item.drone_id.our_price) if item.drone_id.our_price else 0
                ),
                # order_status=None,
                order_status=Status.objects.get(status_name='Failure'), order_id=razorpay_order['id'],
                drone_id=item.drone_id,
                user_id=user_instance,
                created_date_time=datetime.now(),
                updated_date_time=datetime.now(),
                quantity=quantity,                
            )

        response_data = {
            'order_id': razorpay_order['id'],
            'partner_id': partner_id,
            'total_amount': paid_amount,
            'our_price': float(total_amount),
        }
        print(response_data,"respoooooooooooooooooooo")

        return JsonResponse(response_data)

    return JsonResponse({'message': 'Invalid request method'}, status=405)
@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            json_data = json.loads(request.body.decode('utf-8'))

            payment_id = json_data.get('razorpay_payment_id')
            razorpay_order_id = json_data.get('razorpay_order_id')
            signature = json_data.get('razorpay_signature')
            print(signature,"signatureeeeeeeeeeeeeeeeeeeeeeeee")
            

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print(params_dict,"paramssssssssssssssssssssssssssssssssssssssssss")

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print("resultttttttttttttttttttttttttttttttttttttttttt")

            # Handle the result as needed.
            if result:
                try:
                    # Get all orders with the specified razorpay_order_id
                    order_instances = Order.objects.filter(order_id=razorpay_order_id)
                    print(order_instances,"ooooooooooooooooo")

                    if order_instances.exists():
                        # Iterate through each order and update status, payment details, and delete from cart
                        for order_instance in order_instances:
                            order_instance.order_status = Status.objects.get(status_name='Pending')
                            order_instance.payment_id = payment_id
                            order_instance.razorpay_signature = signature

                            # Fetch quantity from DroneSales
                            drone_sales_entries = DroneSales.objects.filter(
                                drone_id=order_instance.drone_id, user=order_instance.user_id
                            )

                            # Update quantity in the Order table
                            if drone_sales_entries.exists():
                                order_instance.quantity = drone_sales_entries[0].quantity

                            order_instance.save()

                            # Delete the entry from Dronesales table
                            cart = DroneSales.objects.filter(drone_id=order_instance.drone_id, user_id=order_instance.user_id)
                            cart.delete()
                    else:
                        return JsonResponse({"message": "Orders not found"}, status=404)

                    return JsonResponse({"message": "Payment completed successfully"}, status=200)

                except Order.DoesNotExist:
                    return JsonResponse({"message": "Orders not found"}, status=404)

            else:
                # If signature verification fails.
                raise SignatureVerificationError("Razorpay Signature Verification Failed")

        except SignatureVerificationError as e:
            return JsonResponse({"message": f"Signature Verification Error: {str(e)}"}, status=400)

        except ValidationError as e:
            return JsonResponse({"message": f"Validation Error: {str(e)}"}, status=400)

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    else:
        return JsonResponse({"message": "Invalid request method. Only POST requests are allowed."}, status=405)


@csrf_exempt
def track_order(request):
    if request.method == 'GET':
       
        order_id = request.GET.get('order_id')
        if not order_id:
            return JsonResponse({'error': 'Missing order_id parameter'}, status=400)

        try:
            order = razorpay_client.order.fetch(order_id)
            status = order.get('status')
            amount_paid = order.get('amount_paid')
            amount_due = order.get('amount_due')

            
            notes = order.get('notes', [])

           
            partner_id = None
            for note in notes:
                if 'partner_id' in note:
                    partner_id = note['partner_id']
                    break

            response_data = {
                'order_id': order_id,
                'status': status,
                'amount_paid': amount_paid,
                'amount_due': amount_due,
                'partner_id': partner_id,
            }

            return JsonResponse(response_data)

        except razorpay.errors.BadRequestError:
            return JsonResponse({'error': 'Order not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



class MyPagination(PageNumberPagination):
    page_size_query_param = 'data_per_page'

@method_decorator(csrf_exempt, name='dispatch')
class OrderStatusView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')
            id_param = request.query_params.get('id')
            page_number = request.query_params.get('page_number')
            data_per_page = request.query_params.get('data_per_page')
            pagination = request.query_params.get('pagination')
            search_param = request.query_params.get('search', '')
            drone_category = request.query_params.get('drone_category')
            drone_category = drone_category.split(',') if drone_category else []
            order_status = request.query_params.get('order_status')
            order_status = order_status.split(',') if order_status else []

            #orders = Order.objects.all().order_by('-id')
            orders = Order.objects.exclude(order_status__isnull=True).order_by('-id')

            if search_param:
                orders = orders.filter(
                    Q(drone_id__drone_name__icontains=search_param) |
                    Q(order_id__icontains=search_param) |
                    Q(user_id__username__icontains=search_param) |
                    Q(order_status__id__icontains=search_param) |
                    Q(quantity__icontains=search_param) |
                    Q(order_status__status_name__icontains=search_param) |
                    Q(drone_id__drone_category__id__icontains=search_param) |
                    Q(drone_id__drone_category__category_name__icontains=search_param) |
                    Q(drone_id__market_price__icontains=search_param) |
                    Q(drone_id__our_price__icontains=search_param) |
                    Q(drone_id__drone_specification__icontains=search_param) |
                    Q(drone_id__sales_status__icontains=search_param) |
                    Q(created_date_time__icontains=search_param) |
                    Q(updated_date_time__icontains=search_param)
                )
            if drone_category:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                orders = orders.filter(drone_id__drone_category__id__in=drone_category_ids).order_by('-id')

            if order_status:
                order_status_ids = [int(status_id) for status_id in order_status]
                orders = orders.filter(order_status__id__in=order_status).order_by('-id')

            if search_param and drone_category and order_status:
                order_status_ids = [int(status_id) for status_id in order_status if status_id.isdigit()]
                drone_category_ids = [int(category_id) for category_id in drone_category if category_id.isdigit()]

                if not all(order_status_ids) or not all(drone_category_ids):
                    return Response({'message': {'error': 'Invalid order_status or drone_category IDs'}})

                orders = orders.filter(
                    Q(order_status__id__in=order_status_ids) &
                    (Q(user_id__username__icontains=search_param) | Q(drone_id__drone_name__icontains=search_param))&
                    Q(drone_id__drone_category__id__in=drone_category_ids)
                ).order_by('-id')


            if search_param and drone_category:
                drone_category_ids = [int(category_id) for category_id in drone_category]
                orders = orders.filter(
                    (Q(user_id__username__icontains=search_param) | Q(drone_id__drone_name__icontains=search_param))&
                   
                    Q(drone_id__drone_category__id__in=drone_category)
                ).order_by('-id')

            if search_param and order_status:
                order_status_ids = [int(status_id) for status_id in order_status]
                orders = orders.filter(
                    (Q(user_id__username__icontains=search_param) | Q(drone_id__drone_name__icontains=search_param))&
                    Q(order_status__id__in=order_status)
                    
                ).order_by('-id')

            if drone_category and order_status:
                order_status_ids = [int(status_id) for status_id in order_status]
                drone_category_ids = [int(category_id) for category_id in drone_category]
                orders = orders.filter(
                    Q(order_status__id__in=order_status) &
                    Q(drone_id__drone_category__id__in=drone_category)
                ).order_by('-id')

            return self.paginate_response(request, orders, page_number, data_per_page)

        except Exception as e:
            return Response({"message": f"Error: {str(e)}"}, status=400)

    def paginate_response(self, request, queryset, page_number, data_per_page):
        paginator = Paginator(queryset, data_per_page)

        try:
            paginated_data = paginator.page(page_number)
        except EmptyPage:
            return Response({"message": "No results found for the given page number"}, status=404)

        serialized_data = OrderSerializer(paginated_data, many=True).data
        len_of_data = paginator.count

        return Response({
            'result': {
                'status': 'GET ALL with pagination',
                'pagination': {
                    'current_page': paginated_data.number,
                    'number_of_pages': paginator.num_pages,
                    'next_url': self.get_next_url(request, paginated_data),
                    'previous_url': self.get_previous_url(request, paginated_data),
                    'has_next': paginated_data.has_next(),
                    'has_previous': paginated_data.has_previous(),
                    'has_other_pages': paginated_data.has_other_pages(),
                    'len_of_data': len_of_data,
                },
                'data': serialized_data,
            },
        })

    def get_next_url(self, request, paginated_data):
        if paginated_data.has_next():
            return request.build_absolute_uri(
                f"?page_number={paginated_data.next_page_number}&data_per_page={paginated_data.paginator.per_page}")
        return None

    def get_previous_url(self, request, paginated_data):
        if paginated_data.has_previous():
            return request.build_absolute_uri(
                f"?page_number={paginated_data.previous_page_number}&data_per_page={paginated_data.paginator.per_page}")
        return None




    def put(self, request, super_admin_id):
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            single_order_id = data.get('order_id')
            status_id = data.get('status_id')

            if not status_id:
                return JsonResponse({"message": "status_id is required in the request body"}, status=400)

            new_status = get_object_or_404(Status, id=status_id)

            super_admin = CustomUser.objects.get(id=super_admin_id)
            is_super_admin = super_admin.role_id.role_name == "Super_admin"
            processed_order_ids = set()

            try:
                with transaction.atomic():
                    if is_super_admin:
                        if single_order_id:
                            orders = Order.objects.filter(order_id=single_order_id)
                            for order in orders:
                                order.order_status = new_status
                                order.updated_date_time = datetime.now()
                                order.save()

                                if order.user_id:
                                    if new_status.status_name == "Shipped":
                                        order.user_id.inventory_count = F('inventory_count') + order.quantity
                                        order.user_id.save()

                                    """neww"""
                                    try:
                                        drone_ownership = DroneOwnership.objects.get(
                                            user=order.user_id,
                                            drone=order.drone_id,
                                        )
                                        drone_ownership.quantity += order.quantity
                                        drone_ownership.save()
                                    except DroneOwnership.DoesNotExist:
                                        # If DroneOwnership doesn't exist, create a new one
                                        DroneOwnership.objects.create(
                                            user=order.user_id,
                                            drone=order.drone_id,
                                            quantity=order.quantity,
                                        )

                                """newww"""

                                # Increment inventory_count for the Super_admin
                            if new_status.status_name == "Shipped":
                                # super_admin.inventory_count = F('inventory_count') + orders.count()
                                super_admin.inventory_count = F('inventory_count') + sum(
                                    order.quantity for order in orders)
                                super_admin.save()
                            return JsonResponse({"message": "Order status updated successfully"}, status=200)

                        # else:
                        #     return JsonResponse({"message": f"Order with order_id {single_order_id} not found"},
                        #                             status=404)

                        elif order_ids:
                            orders = Order.objects.filter(order_id__in=order_ids)
                            for order in orders:
                                order.order_status = new_status
                                order.updated_date_time = datetime.now()
                                order.save()

                                # Increment inventory_count for the associated user
                                if order.user_id:
                                    if new_status.status_name == "Shipped":
                                        order.user_id.inventory_count = F('inventory_count') + order.quantity
                                        order.user_id.save()

                                    """neww"""
                                    try:
                                        drone_ownership = DroneOwnership.objects.get(
                                            user=order.user_id,
                                            drone=order.drone_id,
                                        )
                                        drone_ownership.quantity += order.quantity
                                        drone_ownership.save()
                                    except DroneOwnership.DoesNotExist:
                                        # If DroneOwnership doesn't exist, create a new one
                                        DroneOwnership.objects.create(
                                            user=order.user_id,
                                            drone=order.drone_id,
                                            quantity=order.quantity,
                                        )

                                    """new"""

                            # Increment inventory_count for the Super_admin
                            if new_status.status_name == "Shipped":
                                # super_admin.inventory_count = F('inventory_count') + len(orders)
                                super_admin.inventory_count = F('inventory_count') + sum(
                                    order.quantity for order in orders)
                                super_admin.save()

                            return JsonResponse({"message": "Order status updated successfully"}, status=200)

                    else:
                        return JsonResponse({"message": "Permission denied"}, status=403)

            except IntegrityError:
                return JsonResponse({"message": "IntegrityError: Duplicate key for Super_admin"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON in the request body"}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)



class GetdashbordAPI(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        drone_model = request.query_params.get('drone_model')
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')
        inventory_count = CustomUser.objects.filter(id=user_id).values_list('inventory_count', flat=True).first()

        if user_id and start_time_str and end_time_str and drone_model:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if user.role_id.role_name == 'Partner':
               
                start_time = timezone.datetime.strptime(start_time_str, '%d-%m-%Y')
                end_time = timezone.datetime.strptime(end_time_str, '%d-%m-%Y')

               
                date_range = [start_time.date() + timezone.timedelta(days=x) for x in range((end_time - start_time).days + 1)]

                # drone_model_ids = [int(model_id) for model_id in drone_model.split(',')]
                drone_model_ids = [int(model_id) for model_id in drone_model.split(',') if model_id]
                
                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    user_id=user_id,
                    created_date_time__date__in=date_range
                ).values(
                    'created_date_time__date',
                    'drone_id__drone_category__category_name'
                ).annotate(count=Count('id'))

                result = {
                    'result': {
                        'data': {
                        	'inventory_count':inventory_count,
                            'purchased_drones_Graph': []
                        }
                    }
                }

              
                for drone_model_id in drone_model_ids:
                  
                    purchased_drones_entry = {
                        'drone_model': None,
                        'drone_model_id': None,
                        # 'purchased_drones_Graph': [],
                    }


                    data = queryset.filter(drone_id__drone_category__id=drone_model_id).values(
                        'created_date_time__date'
                    ).annotate(count=Count('id'))

                    if data:
                        drone_model_name = DroneCategory.objects.get(id=drone_model_id).category_name

                        purchased_drones_entry['drone_model'] = drone_model_name
                        purchased_drones_entry['drone_model_id'] = drone_model_id


                        purchased_drones_entry['purchased_drones'] = [{'date': date_entry['created_date_time__date'].strftime('%d-%m-%Y'), 'count': date_entry['count']} for date_entry in data]

                        date_set = set(date_entry['created_date_time__date'] for date_entry in data)
                        missing_dates = date_set.symmetric_difference(date_range)
                        purchased_drones_entry['purchased_drones'].extend(
                            {'date': date.strftime('%d-%m-%Y'), 'count': 0} for date in missing_dates
                        )

                    else:
                       
                        default_model = DroneCategory.objects.filter(id=drone_model_id).first()

                        if default_model:
                            purchased_drones_entry['drone_model'] = default_model.category_name
                            purchased_drones_entry['drone_model_id'] = drone_model_id

                            
                            purchased_drones_entry['purchased_drones'] = [
                                {'date': date.strftime('%d-%m-%Y'), 'count': 0} for date in date_range
                            ]
                    purchased_drones_entry['purchased_drones'] = sorted(purchased_drones_entry['purchased_drones'], key=lambda x: x['date'])
                  
                    result['result']['data']['purchased_drones_Graph'].append(purchased_drones_entry)

                return Response(result)
            else:
                
                date_range = [timezone.datetime.strptime(start_time_str, '%d-%m-%Y').date() + timezone.timedelta(days=x) for x in range((timezone.datetime.strptime(end_time_str, '%d-%m-%Y') - timezone.datetime.strptime(start_time_str, '%d-%m-%Y')).days + 1)]

               
                drone_model_ids = [int(model_id) for model_id in drone_model.split(',') if model_id]
               
                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    created_date_time__date__in=date_range
                ).values(
                    'created_date_time__date',
                    'drone_id__drone_category__category_name'
                ).annotate(count=Count('id'))

                
                result = {
                    'result': {
                        'data': {
                        	'inventory_count':inventory_count,
                            'drone_sales': []
                        }
                    }
                }

              
                for drone_model_id in drone_model_ids:
                  
                    purchased_drones_entry = {
                        'drone_model': None,
                        'drone_model_id': None,
                        'Sales_drones': [],
                    }

                    data = queryset.filter(drone_id__drone_category__id=drone_model_id).values(
                        'created_date_time__date'
                    ).annotate(count=Count('id'))

                    if data:
                        drone_model_name = DroneCategory.objects.get(id=drone_model_id).category_name

                        purchased_drones_entry['drone_model'] = drone_model_name
                        purchased_drones_entry['drone_model_id'] = drone_model_id

                        purchased_drones_entry['Sales_drones'] = [{'date': date_entry['created_date_time__date'].strftime('%d-%m-%Y'), 'count': date_entry['count']} for date_entry in data]

                        date_set = set(date_entry['created_date_time__date'] for date_entry in data)
                        missing_dates = date_set.symmetric_difference(date_range)
                        purchased_drones_entry['Sales_drones'].extend(
                            {'date': date.strftime('%d-%m-%Y'), 'count': 0} for date in missing_dates
                        )

                    else:
                        
                        default_model = DroneCategory.objects.filter(id=drone_model_id).first()

                        if default_model:
                            purchased_drones_entry['drone_model'] = default_model.category_name
                            purchased_drones_entry['drone_model_id'] = drone_model_id

                           
                            purchased_drones_entry['Sales_drones'] = [
                                {'date': date.strftime('%d-%m-%Y'), 'count': 0} for date in date_range
                            ]
                    purchased_drones_entry['Sales_drones'] = sorted(purchased_drones_entry['Sales_drones'], key=lambda x: x['date'])
                    
                    result['result']['data']['drone_sales'].append(purchased_drones_entry)

                return Response(result)

        if user_id and start_time_str and end_time_str:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if user.role_id.role_name == 'Partner':
               
                start_time = timezone.datetime.strptime(start_time_str, '%d-%m-%Y')
                end_time = timezone.datetime.strptime(end_time_str, '%d-%m-%Y')

                
                date_range = [start_time.date() + timezone.timedelta(days=x) for x in range((end_time - start_time).days + 1)]

                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    user_id=user_id,
                    created_date_time__date__in=date_range
                ).values(
                    'created_date_time__date',
                    'drone_id__drone_category__category_name'
                ).annotate(count=Count('id'))

                result = {
                    'result': {
                        'data': {
                        	'inventory_count':inventory_count,
                            'purchased_drones_Graph': [],
                        }
                    }
                }

                dates_data = {date: {'count': 0, 'drone_category_name': []} for date in date_range}
                drone_models = set()

                for entry in queryset:
                    date_entry = entry['created_date_time__date']
                    if date_entry is not None:
                        
                        dates_data[date_entry]['count'] += entry['count']
                        dates_data[date_entry]['drone_category_name'].append(entry['drone_id__drone_category__category_name'])

                       
                        drone_models.add(entry['drone_id__drone_category__category_name'])

                drone_sales_data = []

                for date_entry, date_data in dates_data.items():
                    formatted_date = date_entry.strftime('%d-%m-%Y')  
                    drone_sales_data.append({
                        'date': formatted_date,
                        'count': date_data['count'],
                    })

                drone_entry = {
                    'Purchased_drones': [
                        {
                            'label': 'Purchased Drones',
                            'data': drone_sales_data,
                        }
                    ],
                    'drone_model': [
                        {
                            'drone_category_name': list(drone_models),
                        }
                    ],
                }

                result['result']['data']['purchased_drones_Graph'].append(drone_entry)

                return Response(result)
            else:
                start_time = timezone.datetime.strptime(start_time_str, '%d-%m-%Y')
                end_time = timezone.datetime.strptime(end_time_str, '%d-%m-%Y')

                date_range = [start_time.date() + timezone.timedelta(days=x) for x in range((end_time - start_time).days + 1)]

                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    created_date_time__date__range=[str(start_time.date()), str(end_time.date())]
                ).values(
                    'created_date_time__date',
                    'drone_id__drone_category__category_name'
                ).annotate(count=Count('id'))

                result = {
                    'result': {
                        'data': {
                        	'inventory_count':inventory_count,
                            'drone_sales': [],
                        }
                    }
                }

                dates_data = {date: {'count': 0, 'drone_category_name': []} for date in date_range}
                drone_models = set()

                for entry in queryset:
                    date_entry = entry['created_date_time__date']
                    if date_entry is not None:
                        dates_data[date_entry]['count'] += entry['count']
                        dates_data[date_entry]['drone_category_name'].append(entry['drone_id__drone_category__category_name'])
                        drone_models.add(entry['drone_id__drone_category__category_name'])

                drone_sales_data = []

                for date_entry, date_data in dates_data.items():
                    formatted_date = date_entry.strftime('%d-%m-%Y')
                    drone_sales_data.append({
                        'date': formatted_date,
                        'count': date_data['count'],
                    })

                drone_entry = {
                    'Sales_drones': [
                        {
                            'label': 'Sales_drones ',
                            'data': drone_sales_data,
                        }
                    ],
                    'drone_model': [
                        {
                            'drone_category_name': list(drone_models),
                        }
                    ],
                }

                result['result']['data']['drone_sales'].append(drone_entry)

                return Response(result)

                # start_time = timezone.datetime.strptime(start_time_str, '%d-%m-%Y')
                # end_time = timezone.datetime.strptime(end_time_str, '%d-%m-%Y')

                # date_range = [start_time.date() + timezone.timedelta(days=x) for x in range((end_time - start_time).days + 1)]

                # queryset = Order.objects.filter(
                #     order_status__status_name='Shipped',
                #     created_date_time__date__range=[str(start_time.date()), str(end_time.date())]
                # ).values(
                #     'created_date_time__date',
                #     'drone_id__drone_category__category_name'
                # ).annotate(count=Count('id'))

                # result = {
                #     'result': {
                #         'data': {
                #             'drone_sales': [],
                #         }
                #     }
                # }

                # dates_data = {date: {'count': 0, 'drone_category_name': []} for date in date_range}
                # drone_models = set()

                # for entry in queryset:
                #     date_entry = entry['created_date_time__date']
                #     if date_entry is not None:
                #         dates_data[date_entry]['count'] += entry['count']
                #         dates_data[date_entry]['drone_category_name'].append(entry['drone_id__drone_category__category_name'])
                #         drone_models.add(entry['drone_id__drone_category__category_name'])

                # drone_sales_data = []

                # for date_entry, date_data in dates_data.items():
                #     formatted_date = date_entry.strftime('%d-%m-%Y')
                #     drone_sales_data.append({
                #         'date': formatted_date,
                #         'count': date_data['count'],
                #     })

                # drone_entry = {
                #     'purchased_drones_Graph': [
                #         {
                #             'label': 'Purchased Drones',
                #             'data': drone_sales_data,
                #         }
                #     ],
                #     'drone_model': [
                #         {
                #             'drone_category_name': list(drone_models),
                #         }
                #     ],
                # }

                # result['result']['data']['drone_sales'].append(drone_entry)

        if user_id and not drone_model:
            
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if user.role_id.role_name == 'Partner': 
                
                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    user_id=user_id
                )

                data = queryset.values(
                    'created_date_time__month',
                    'drone_id__drone_category__category_name',
                    'drone_id__drone_category__id'
                ).annotate(count=Count('id'))

                result = {
                    'data': {
                    	'inventory_count':inventory_count,
                        'purchased_drones_Graph': [],
                    }
                }

                overall_count_dict = {}
                months_data = {month: {'count': 0, 'drone_category_name': []} for month in range(1, 13)}

                drone_models = set()
                drone_models_id = set()
                for entry in data:
                    month_number = entry['created_date_time__month']
                    if month_number is not None:
                        month_name_loop = timezone.datetime(2022, month_number, 1).strftime('%B')

                        if month_name_loop not in overall_count_dict:
                            overall_count_dict[month_name_loop] = entry['count']
                        else:
                            overall_count_dict[month_name_loop] += entry['count']

                        
                        months_data[month_number]['count'] = overall_count_dict[month_name_loop]
                        months_data[month_number]['drone_category_name'].append(entry['drone_id__drone_category__category_name'])

                        
                        drone_models.add(entry['drone_id__drone_category__category_name'])
                        drone_models_id.add(entry['drone_id__drone_category__id'])

                drone_sales_data = []

                for month_number, month_data in months_data.items():
                    month_name = timezone.datetime(2022, month_number, 1).strftime('%B')
                    drone_sales_data.append({
                        'month': month_name,
                        'count': month_data['count'],
                    })

                drone_entry = {
                    'Purchased_drones': [
                        {
                            'label': 'Purchased Drones ',
                            'data': drone_sales_data,
                        }
                    ],
                    'drone_model': [
                        {
                            'drone_category_name': list(drone_models),
                            'drone_model_id': list(drone_models_id),
                        }
                    ],
                }

                result['data']['purchased_drones_Graph'].append(drone_entry)

                return Response({'result': result})

            else:
               
                queryset = Order.objects.filter(order_status__status_name='Shipped')

                data = queryset.values(
                    'created_date_time__month',
                    'drone_id__drone_category__category_name'
                ).annotate(count=Count('id'))

                result = {
                    'data': {
                    	'inventory_count':inventory_count,
                        'drone_sales': [],
                    }
                }

                overall_count_dict = {}
                months_data = {month: {'count': 0, 'drone_category_name': []} for month in range(1, 13)}

                drone_models = set()

                for entry in data:
                    month_number = entry['created_date_time__month']
                    if month_number is not None:
                        month_name_loop = timezone.datetime(2022, month_number, 1).strftime('%B')

                        if month_name_loop not in overall_count_dict:
                            overall_count_dict[month_name_loop] = entry['count']
                        else:
                            overall_count_dict[month_name_loop] += entry['count']

                        
                        months_data[month_number]['count'] = overall_count_dict[month_name_loop]
                        months_data[month_number]['drone_category_name'].append(entry['drone_id__drone_category__category_name'])

                       
                        drone_models.add(entry['drone_id__drone_category__category_name'])

                drone_sales_data = []

                for month_number, month_data in months_data.items():
                    month_name = timezone.datetime(2022, month_number, 1).strftime('%B')
                    drone_sales_data.append({
                        'month': month_name,
                        'count': month_data['count'],
                    })

                drone_entry = {
                    'Sales_drones': [
                        {
                            'label': 'Sales Drones',
                            'data': drone_sales_data,
                        }
                    ],
                    'drone_model': [
                        {
                            'drone_category_name': list(drone_models),
                        }
                    ],
                }

                result['data']['drone_sales'].append(drone_entry)

                return Response({'result': result})


        if user_id and drone_model:
            
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if user.role_id.role_name == 'Partner': 
                drone_model_ids = [int(model_id) for model_id in drone_model.split(',')]

                
                queryset = Order.objects.filter(
                    user_id=user_id,
                    order_status__status_name='Shipped',
                    drone_id__drone_category__id__in=drone_model_ids
                ).order_by('id')

                data = queryset.values(
                    'drone_id__drone_category__category_name',
                    'drone_id__drone_category__id',
                    'created_date_time__month'
                ).annotate(count=Count('id'))

                all_months = [timezone.datetime(2022, month, 1).strftime('%B') for month in range(1, 13)]

                result = {
                    'result': {
                        'data': {
                        'inventory_count':inventory_count,
                            'purchased_drones_Graph': []
                        }
                    }
                }

                counts_by_model = {}
                for drone_model_id in drone_model_ids:
                    counts_by_model[drone_model_id] = {}
                    for entry in data.filter(drone_id__drone_category__id=drone_model_id):
                        counts_by_model[drone_model_id][entry['created_date_time__month']] = counts_by_model[drone_model_id].get(entry['created_date_time__month'], 0) + entry['count']

              
                for drone_model_id in drone_model_ids:
                    
                    purchased_drones_entry = {
                        'drone_model': None,
                        'drone_model_id': None,
                        # 'purchased_drones_Graph': [],
                    }

                   
                    model_data = data.filter(drone_id__drone_category__id=drone_model_id).first()

                    if model_data:
                        drone_model_name = model_data['drone_id__drone_category__category_name']

                        purchased_drones_entry['drone_model'] = drone_model_name
                        purchased_drones_entry['drone_model_id'] = drone_model_id
                    else:
                       
                        default_model = DroneCategory.objects.filter(id=drone_model_id).first()

                        if default_model:
                            purchased_drones_entry['drone_model'] = default_model.category_name
                            purchased_drones_entry['drone_model_id'] = drone_model_id
                        else:
                            purchased_drones_entry['drone_model'] = 'Unknown'
                            purchased_drones_entry['drone_model_id'] = 'Unknown'

                   
                    purchased_drones_entry['purchased_drones'] = [{'month': timezone.datetime(2022, month_number, 1).strftime('%B'), 'count': counts_by_model[drone_model_id].get(month_number, 0)} for month_number in range(1, 13)]
                   
                    result['result']['data']['purchased_drones_Graph'].append(purchased_drones_entry)

                return Response(result)
            else:
               
                drone_model_ids = [int(model_id) for model_id in drone_model.split(',')]

                
                queryset = Order.objects.filter(
                    order_status__status_name='Shipped',
                    drone_id__drone_category__id__in=drone_model_ids
                ).order_by('id')

                data = queryset.values(
                    'drone_id__drone_category__category_name',
                    'drone_id__drone_category__id',
                    'created_date_time__month'
                ).annotate(count=Count('id'))

                all_months = [timezone.datetime(2022, month, 1).strftime('%B') for month in range(1, 13)]

                result = {
                    'result': {
                        'data': {
                        	'inventory_count':inventory_count,
                            'drone_sales': []
                        }
                    }
                }

                counts_by_model = {}
                for drone_model_id in drone_model_ids:
                    counts_by_model[drone_model_id] = {}
                    for entry in data.filter(drone_id__drone_category__id=drone_model_id):
                        counts_by_model[drone_model_id][entry['created_date_time__month']] = counts_by_model[drone_model_id].get(entry['created_date_time__month'], 0) + entry['count']

                
                for drone_model_id in drone_model_ids:
                    
                    purchased_drones_entry = {
                        'drone_model': None,
                        'drone_model_id': None,
                        'Sales_drones': [],
                    }

                   
                    model_data = data.filter(drone_id__drone_category__id=drone_model_id).first()

                    if model_data:
                        drone_model_name = model_data['drone_id__drone_category__category_name']

                        purchased_drones_entry['drone_model'] = drone_model_name
                        purchased_drones_entry['drone_model_id'] = drone_model_id
                    else:
                       
                        default_model = DroneCategory.objects.filter(id=drone_model_id).first()

                        if default_model:
                            purchased_drones_entry['drone_model'] = default_model.category_name
                            purchased_drones_entry['drone_model_id'] = drone_model_id
                        else:
                            purchased_drones_entry['drone_model'] = 'Unknown'
                            purchased_drones_entry['drone_model_id'] = 'Unknown'

                  
                    purchased_drones_entry['Sales_drones'] = [{'month': timezone.datetime(2022, month_number, 1).strftime('%B'), 'count': counts_by_model[drone_model_id].get(month_number, 0)} for month_number in range(1, 13)]
                   
                    result['result']['data']['drone_sales'].append(purchased_drones_entry)

                return Response(result)
        else:
            return Response({'error': 'Invalid parameters'})


class GetCompanyDetailAPI(APIView):
    def get(self, request, *args, **kwargs):
        gst_number = request.query_params.get('gst_number')

        if not gst_number:
            return Response({"message": "GST number is required"}, status=status.HTTP_400_BAD_REQUEST)

        api_url = 'https://einv-apisandbox.nic.in/eivital/v1.04/auth'
        api_key = 'D1NX96M3kLIH8XrqBsLriAx+YAi7+aLSaEZPuo9VFq4='

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }

        data = {
            'gst_number': gst_number,
        }

        try:
            response = requests.post(api_url, headers=headers, json=data)

            if response.status_code == 200:
                company_details = response.json()
                return Response(company_details, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Failed to retrieve company details"}, status=response.status_code)

        except requests.RequestException as e:
            return Response({"message": f"Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # gst_number = request.query_params.get('gst_number')
        # api_url = 'https://einv-apisandbox.nic.in/eivital/v1.04/auth'  # Use the correct API endpoint

        # if not gst_number:
        #     return Response({"message": "GST number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # client_id = 'AAGCE29TXPDW932'
        # client_secret = '76KkYyE3SGguAaOocIWw'
        # gstin = '29AAGCE4783K1Z1'
        # user_name = 'ekfrazotech'
        # app_key = 'D1NX96M3kLIH8XrqBsLriAx+YAi7+aLSaEZPuo9VFq4='

        # headers = {
        #     'Content-Type': 'application/json',
        # }

        # params = {
        #     'client_id': client_id,
        #     'client_secret': client_secret,
        #     'gstin': gstin,
        #     'user_name': user_name,
        #     'App-key': app_key,
        # }

        # try:
        #     response = requests.get(api_url, headers=headers, params=params)

        #     if response.status_code == 200:
        #         company_details = response.json()
        #         return Response({
        #             "message": "Company details fetched successfully",
        #             "data": company_details
        #         }, status=status.HTTP_200_OK)
        #     else:
        #         print(response.text)  # Add this line to print the response content
        #         return Response({"message": "Failed to retrieve company details"}, status=response.status_code)

        # except requests.RequestException as e:
        #     return Response({"message": f"Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanyAndPartnerDetailsAPIView(APIView):
    def get_state_code(self, state_name):
        # Define a dictionary mapping state names to their codes
        state_code_mapping = {
            "Andaman and Nicobar Islands": "35",
            "Andhra Pradesh": "28",
            "Arunachal Pradesh": "12",
            "Assam": "18",
            "Bihar": "10",
            "Chandigarh": "04",
            "Chhattisgarh": "22",
            "Dadra and Nagar Haveli and Daman and Diu": "26",
            "Delhi": "07",
            "Goa": "30",
            "Gujarat": "24",
            "Haryana": "06",
            "Himachal Pradesh": "02",
            "Jharkhand": "20",
            "Karnataka": "29",
            "Kerala": "32",
            "Lakshadweep": "31",
            "Madhya Pradesh": "23",
            "Maharashtra": "27",
            "Manipur": "14",
            "Meghalaya": "17",
            "Mizoram": "15",
            "Nagaland": "13",
            "Odisha": "21",
            "Puducherry": "34",
            "Punjab": "03",
            "Rajasthan": "08",
            "Sikkim": "11",
            "Tamil Nadu": "33",
            "Telangana": "36",
            "Tripura": "16",
            "Uttar Pradesh": "09",
            "Uttarakhand": "05",
            "West Bengal": "19",
            "Jammu and Kashmir": "01",
            "Ladakh": "02",
        }

        # Retrieve the state code from the dictionary
        return state_code_mapping.get(state_name, '')

    def get_location_details(self, pin_code):
        geolocator = Nominatim(user_agent="amxcrm")
        location = geolocator.geocode(pin_code)

        if location:
            raw_data = location.raw
            print(raw_data, "Raw Data")

            display_name = raw_data.get('display_name', '')
            print(display_name, "Display Name")

            # Extracting information from display_name
            parts = display_name.split(', ')
            state = parts[-2]
            city = parts[-3]
            country = parts[-1]

            # Retrieve state code using the predefined mapping
            state_code = self.get_state_code(state)
            print(state_code, "State Code")

            return {
                'state': state,
                'state_code': state_code,
                'city': city,
                'country': country
            }

        return None

    def put(self, request, pk):
        server_address = "https://amx-crm.thestorywallcafe.com/"
        data = request.data
        try:
            partner = CustomUser.objects.get(pk=pk)
            if partner.status is True:
                super_admin_role = Role.objects.filter(role_name="Super_admin").first()
                if super_admin_role:
                    super_admin = super_admin_role.customuser_set.first()
                    super_admin_email = super_admin.email if super_admin else None

                    if not super_admin_email:
                        return Response({"message": "Super admin email not found"},
                                        status=status.HTTP_400_BAD_REQUEST)



                    requested_changes = {}

                    fields_to_check = ["company_name", "company_email", "shipping_address", "billing_address","profile_pic"
                                       "company_phn_number", "company_gst_num", "company_cin_num", "pan_number","email_altr","address","pin_code",
                                       "reason","shipping_pincode","billing_pincode"]

                    new_changes = {}

                    for field in fields_to_check:
                        old_value = getattr(partner, field)
                        new_value = data.get(field)

                        if old_value != new_value:
                            requested_changes[field] = {"old": old_value, "new": new_value}
                            new_changes[field] = new_value

                            if field =="user_signature":
                                try:
                                    characters = string.ascii_letters + string.digits
                                    random_string = ''.join(random.choice(characters) for _ in range(10))
                                    format, imgstr = new_value.split(';base64,')
                                    ext = format.split('/')[-1]
                                    signature_name = f'signature_{random_string}.{ext}'
                                    data = ContentFile(base64.b64decode(imgstr), name=signature_name)
                                except Exception as e:
                                    print(f"Error saving signature image: {e}")
                                requested_changes[field] = {"old": server_address+MEDIA_URL+str(old_value), "new": new_value}
                            else:
                                requested_changes[field] = {"old": old_value, "new": new_value}
                            new_changes[field] = new_value                                                       



                    change = ChangeRequestCompanyDetails.objects.create(**new_changes, created_by=pk)

                    approve_url = request.build_absolute_uri(reverse('approve_request', kwargs={'pk': change.id}))
                    reject_url = request.build_absolute_uri(reverse('reject_request', kwargs={'pk': change.id}))

                    logger.debug(f"Generated 'approve' URL: {approve_url}")
                    logger.debug(f"Generated 'reject' URL: {reject_url}")

                    email_content = render_to_string('email/partner_update_request_email.html', {
                        'requested_changes': requested_changes,
                        'approve_url': approve_url,
                        'reject_url': reject_url,
                        'user_id': change.id
                    })

                    
                    send_mail(
                        'Partner Update Request',
                        strip_tags(email_content),
                        'amxdrone123@gmail.com',
                        [super_admin_email],
                        fail_silently=False,
                        html_message=email_content,
                    )

                    return Response({"message": "Update request sent to the super admin"},
                                    status=status.HTTP_200_OK)
            else:

                company_name = data.get('company_name')
                company_email = data.get('company_email')
                shipping_address = data.get('shipping_address')
                billing_address = data.get('billing_address')
                company_phn_number = data.get('company_phn_number')
                company_gst_num = data.get('company_gst_num')
                company_cin_num = data.get('company_cin_num')
                shipping_pincode = data.get('shipping_pincode')
                billing_pincode = data.get('billing_pincode')
                pan_number = data.get('pan_number')
                company_logo = request.FILES.get('company_logo')
                company_logo = data.get('company_logo')
                email_altr = data.get('email_altr')
                username = data.get('username')
                pin_code = data.get('pin_code')
                address = data.get('address')
                signature_data = data.get('user_signature')
                profile_pic= data.get('profile_pic')

                partner.company_name = company_name
                partner.company_email = company_email
                partner.shipping_address = shipping_address
                partner.billing_address = billing_address
                partner.shipping_pincode = shipping_pincode
                partner.billing_pincode = billing_pincode
                partner.company_phn_number = company_phn_number
                partner.company_gst_num = company_gst_num
                partner.company_cin_num = company_cin_num
                partner.pin_code = pin_code
                partner.email_altr = email_altr
                partner.address = address
                partner.pan_number = pan_number

                shipping_location_details = self.get_location_details(shipping_pincode)
                if shipping_location_details:
                    partner.shipping_state = shipping_location_details['state']
                    partner.shipping_state_city = shipping_location_details['city']
                    partner.shipping_state_country = shipping_location_details['country']
                    partner.shipping_state_code = shipping_location_details['state_code']


                # Fetch and update billing location details
                billing_location_details = self.get_location_details(billing_pincode)
                if billing_location_details:
                    partner.billing_state = billing_location_details['state']
                    partner.billing_state_city = billing_location_details['city']
                    partner.billing_state_country = billing_location_details['country']
                    partner.billing_state_code = billing_location_details['state_code']


                if "company_logo" in request.data:
                    print('00000000000000000-----------------------0000000000000000000')
                    company_logo_base64 = request.data["company_logo"]
                    converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username, 'company_logos')
                    print('--------------------------------------------',converted_company_logo_base64)

                    if converted_company_logo_base64:
                       
                        converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                        
                        file_path = f"/company_logos/{partner.username}companylogo.png"
                        partner.company_logo.save(f"{partner.username}companylogo.png", ContentFile(converted_company_logo_base64), save=True)
                        partner.company_logo.name = file_path

                if 'profile_pic' in data:
                    profile_pic_base64 = data.pop('profile_pic')
                    
                    _, base64_data = profile_pic_base64.split(',')
                    image_data = base64.b64decode(base64_data)
                    partner.profile_pic.save(f"{partner.username}_profile_pic.png", ContentFile(image_data), save=False)

                if signature_data:
                    try:
                        format, imgstr = signature_data.split(';base64,')
                        ext = format.split('/')[-1]
                        signature_name = f'signature_{uuid.uuid4()}.{ext}'
                        data = ContentFile(base64.b64decode(imgstr), name=signature_name)
                        partner.user_signature.save(signature_name, data, save=True)
                    except Exception as e:
                        print(f"Error saving signature image: {e}")


                partner.status = True
                partner.partner_initial_update = True
                partner.updated_date_time_company = timezone.now()
                partner.save()

                return Response({"message": "Company details updated successfully"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)
    # def get_state_code(self, state_name):
    #     # Define a dictionary mapping state names to their codes
    #     state_code_mapping = {
    #         "Andaman and Nicobar Islands": "35",
    #         "Andhra Pradesh": "28",
    #         "Arunachal Pradesh": "12",
    #         "Assam": "18",
    #         "Bihar": "10",
    #         "Chandigarh": "04",
    #         "Chhattisgarh": "22",
    #         "Dadra and Nagar Haveli and Daman and Diu": "26",
    #         "Delhi": "07",
    #         "Goa": "30",
    #         "Gujarat": "24",
    #         "Haryana": "06",
    #         "Himachal Pradesh": "02",
    #         "Jharkhand": "20",
    #         "Karnataka": "29",
    #         "Kerala": "32",
    #         "Lakshadweep": "31",
    #         "Madhya Pradesh": "23",
    #         "Maharashtra": "27",
    #         "Manipur": "14",
    #         "Meghalaya": "17",
    #         "Mizoram": "15",
    #         "Nagaland": "13",
    #         "Odisha": "21",
    #         "Puducherry": "34",
    #         "Punjab": "03",
    #         "Rajasthan": "08",
    #         "Sikkim": "11",
    #         "Tamil Nadu": "33",
    #         "Telangana": "36",
    #         "Tripura": "16",
    #         "Uttar Pradesh": "09",
    #         "Uttarakhand": "05",
    #         "West Bengal": "19",
    #         "Jammu and Kashmir": "01",
    #         "Ladakh": "02",
    #     }

    #     # Retrieve the state code from the dictionary
    #     return state_code_mapping.get(state_name, '')

    # def get_location_details(self, pin_code):
    #     geolocator = Nominatim(user_agent="amxcrm")
    #     print('geolocator-------------------->>>>>>>>>>geolocator',geolocator)
    #     location = geolocator.geocode(pin_code)
    #     print('location----------------',location)

    #     if location:
    #         raw_data = location.raw
    #         print(raw_data, "Raw Data")

    #         display_name = raw_data.get('display_name', '')
    #         print(display_name, "Display Name>>>>>>>>>>>>>>>>>>>>>>>>")

    #         # Extracting information from display_name
    #         parts = display_name.split(', ')
    #         state = parts[-2]
    #         city = parts[-3]
    #         country = parts[-1]

    #         # Check if the country is India
    #         if country != 'India':
    #             return None

    #         # Retrieve state code using the predefined mapping
    #         state_code = self.get_state_code(state)
    #         print(state_code, "State Code-------------------------->>>>>>>")

    #         return {
    #             'state': state,
    #             'state_code': state_code,
    #             'city': city,
    #             'country': country
    #         }

    #     return None
    # def put(self, request, pk=None):
    #     # Update partner details
    #     partner = get_object_or_404(CustomUser, pk=pk)

    #     data = request.data
    #     required_fields = ['first_name', 'last_name', 'email', 'email_altr', 'mobile_number', 'address', 'pin_code',"shipping_pincode","billing_pincode",
    #                        'password', 'location', 'profile_pic', 'company_logo','user_signature']

    #     missing_fields = [field for field in required_fields if field not in request.data]
    #     if missing_fields:
    #         return Response({"message": f"The following fields are required: {', '.join(missing_fields)}"},
    #                         status=status.HTTP_400_BAD_REQUEST)

    #     allowed_fields = ["first_name", "last_name", "email", "email_altr", "mobile_number", "address", "pin_code",
    #                       "password", "location", "profile_pic", "company_logo","shipping_pincode","billing_pincode",
    #                       "company_name", "company_email", "shipping_address", "billing_address",
    #                       "company_phn_number", "company_gst_num", "company_cin_num", "pan_number",'user_signature']
    #     data = {field: data.get(field) for field in allowed_fields if field in data}

    #     if 'pin_code' in data:
    #         partner.pin_code = data.pop('pin_code')

    #     if 'address' in data:
    #         partner.address = data.pop('address')

    #     if 'shipping_pincode' in data:
    #         partner.shipping_pincode = data.pop('shipping_pincode')

    #     if 'billing_pincode' in data:
    #         partner.billing_pincode = data.pop('billing_pincode')

        # if 'profile_pic' in data:
        #     profile_pic_base64 = data.pop('profile_pic')
            
        #     _, base64_data = profile_pic_base64.split(',')
        #     image_data = base64.b64decode(base64_data)
        #     partner.profile_pic.save(f"{partner.username}_profile_pic.png", ContentFile(image_data), save=False)
    #     # # Handle company logo
    #     if "company_logo" in request.data:
    #         company_logo_base64 = request.data["company_logo"]
    #         converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username, 'company_logos')

    #         if converted_company_logo_base64:
                
    #             converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                
    #             file_path = f"/company_logos/{partner.username}companylogo.png"
    #             partner.company_logo.save(f"{partner.username}companylogo.png", ContentFile(converted_company_logo_base64), save=True)
    #             partner.company_logo.name = file_path

    #     # # Update other fields
    #     for key, value in data.items():
    #         setattr(partner, key, value)

    #     if 'pin_code' in data:
    #         partner.pin_code = data.pop('pin_code')

    #     if 'address' in data:
    #         partner.address = data.pop('address')

    #     if 'shipping_pincode' in data:
    #         partner.shipping_pincode = data.pop('shipping_pincode')

    #     if 'billing_pincode' in data:
    #         partner.shipping_pincode = data.pop('billing_pincode')

    #     partner = CustomUser.objects.get(pk=pk)

    #     if partner.status is True:
    #         super_admin_role = Role.objects.filter(role_name="Super_admin").first()

    #         if super_admin_role:
    #             super_admin = super_admin_role.customuser_set.first()
    #             super_admin_email = super_admin.email if super_admin else None

    #             if not super_admin_email:
    #                 return Response({"message": "Super admin email not found"}, status=status.HTTP_400_BAD_REQUEST)

    #             requested_changes = {}
    #             fields_to_check = ["company_name", "company_email", "shipping_address", "billing_address","shipping_pincode","billing_pincode","pin_code","address",
    #                                "company_phn_number", "company_gst_num", "company_cin_num", "pan_number", "reason"]

    #             new_changes = {}

    #             for field in fields_to_check:
    #                 old_value = getattr(partner, field)
    #                 new_value = data.get(field)

    #                 if old_value != new_value:
    #                     requested_changes[field] = {"old": old_value, "new": new_value}
    #                     new_changes[field] = new_value

    #             change = ChangeRequestCompanyDetails.objects.create(**new_changes, created_by=pk)

    #             approve_url = request.build_absolute_uri(reverse('approve_request', kwargs={'pk': change.id}))
    #             reject_url = request.build_absolute_uri(reverse('reject_request', kwargs={'pk': change.id}))

    #             email_content = render_to_string('email/partner_update_request_email.html', {
    #                 'requested_changes': requested_changes,
    #                 'approve_url': approve_url,
    #                 'reject_url': reject_url,
    #                 'user_id': change.id
    #             })

    #             send_mail(
    #                 'Partner Update Request',
    #                 strip_tags(email_content),
    #                 'amxdrone123@gmail.com',
    #                 [super_admin_email],
    #                 fail_silently=False,
    #                 html_message=email_content,
    #             )

    #             return Response({"message": "Update request sent to the super admin"}, status=status.HTTP_200_OK)
                
    #     else:
            # company_name = data.get('company_name')
            # company_email = data.get('company_email')
            # shipping_address = data.get('shipping_address')
            # billing_address = data.get('billing_address')
            # company_phn_number = data.get('company_phn_number')
            # company_gst_num = data.get('company_gst_num')
            # company_cin_num = data.get('company_cin_num')
            # shipping_pincode = data.get('shipping_pincode')
            # billing_pincode = data.get('billing_pincode')
            # pan_number = data.get('pan_number')
            # company_logo = request.FILES.get('company_logo')
            # company_logo = data.get('company_logo')
            # email_altr = data.get('email_altr')
            # username = data.get('username')
            # pin_code = data.get('pin_code')
            # address = data.get('address')
            # signature_data = data.get('user_signature')


    #         partner.company_name = company_name
    #         partner.company_email = company_email
    #         partner.shipping_address = shipping_address
    #         partner.billing_address = billing_address
    #         partner.company_phn_number = company_phn_number
    #         partner.company_gst_num = company_gst_num
    #         partner.company_cin_num = company_cin_num
    #         partner.pan_number = pan_number

    #         shipping_location_details = self.get_location_details(shipping_pincode)
    #         if shipping_location_details:
    #             partner.shipping_state = shipping_location_details['state']
    #             partner.shipping_state_city = shipping_location_details['city']
    #             partner.shipping_state_country = shipping_location_details['country']
    #             partner.shipping_state_code = shipping_location_details['state_code']

    #         # Fetch and update billing location details
    #         billing_location_details = self.get_location_details(billing_pincode)
    #         if billing_location_details:
    #             partner.billing_state = billing_location_details['state']
    #             partner.billing_state_city = billing_location_details['city']
    #             partner.billing_state_country = billing_location_details['country']
    #             partner.billing_state_code = billing_location_details['state_code']
                        
    #         if 'pin_code' in data:
    #             partner.pin_code = data.pop('pin_code')

    #         if 'address' in data:
    #             partner.address = data.pop('address')

    #         if 'shipping_pincode' in data:
    #             partner.shipping_pincode = data.pop('shipping_pincode')
                
    #         if 'billing_pincode' in data:
    #             partner.billing_pincode = data.pop('billing_pincode')

    #         if 'profile_pic' in data:
    #             profile_pic_base64 = data.pop('profile_pic')

    #         if "company_logo" in request.data:
    #             company_logo_base64 = request.data["company_logo"]
    #             converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username, 'company_logos')

    #             if converted_company_logo_base64:
                    
    #                 converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                    
    #                 file_path = f"/company_logos/{partner.username}companylogo.png"
    #                 partner.company_logo.save(f"{partner.username}companylogo.png", ContentFile(converted_company_logo_base64), save=True)
    #                 partner.company_logo.name = file_path

    #         # if "user_signature" in request.data:
    #         #     company_logo_base64 = request.data["company_logo"]
    #         #     converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username, 'company_logos')

    #         #     if converted_company_logo_base64:
                    
    #         #         converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                    
    #         #         file_path = f"/company_logos/{partner.username}companylogo.png"
    #         #         partner.company_logo.save(f"{partner.username}companylogo.png", ContentFile(converted_company_logo_base64), save=True)
    #         #         partner.company_logo.name = file_path
                

    #         if "user_signature" in request.data:
    #             print('---------------------------------------------------------')
    #             user_sigantures_base64 = request.data["user_signature"]
    #             print("user_sigantures_base64-----------------------:", user_sigantures_base64)
                
    #             converted_user_sigantures_base64 = convertBase64(user_sigantures_base64, 'user_signature', partner.username, 'user_signatures')
    #             print("converted_user_sigantures_base64--------->>>>>>>>>>>>>>>>>>>>:", converted_user_sigantures_base64)

    #             if converted_user_sigantures_base64:
    #                 converted_user_sigantures_base64 = converted_user_sigantures_base64.strip('"')
    #                 print("converted_user_sigantures_base64___________________ (stripped):", converted_user_sigantures_base64)

    #                 file_path = f"/user_signatures/{partner.username}user_signature.png"
    #                 print("file_path:", file_path)
                    
    #                 partner.user_signature.save(f"{partner.username}user_signature.png", ContentFile(converted_user_sigantures_base64), save=True)
    #                 print("Saved partner.user_signature.")
                    
    #                 partner.user_signature.name = file_path
    #                 print("Assigned file_path to partner.user_signature.name.")
    #         # if signature_data:
    #         #     try:
    #         #         format, imgstr = signature_data.split(';base64,')
    #         #         ext = format.split('/')[-1]
    #         #         signature_name = f'signature_{uuid.uuid4()}.{ext}'
    #         #         data = ContentFile(base64.b64decode(imgstr), name=signature_name)
    #         #         partner.user_signature.save(signature_name, data, save=True)
    #         #     except Exception as e:
    #         #         print(f"Error saving signature image: {e}")

    #         partner.status = True
    #         partner.partner_initial_update = True 
    #         partner.updated_date_time_company = timezone.now()
    #         partner.save()

    #         return Response({"message": "Company details updated successfully"}, status=status.HTTP_200_OK)


class InvoiceTypeAPI(APIView):
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        pk = kwargs.get('pk')  # Retrieve pk from URL parameters

        if id is not None:
            status = InvoiceType.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'invoice_type_name': status.invoice_type_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Invoice type not found for the specified id'}, status=404)
        elif pk is not None:
            status = InvoiceType.objects.filter(id=pk).first()  # Use pk instead of id
            if status:
                data = {'id': status.id, 'invoice_type_name': status.invoice_type_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Invoice type not found for the specified id'}, status=404)
        else:
            data = InvoiceType.objects.all().values()
            return Response({'Result':data})

    def post(self, request):
        data = request.data
        invoice_type_name = data.get('invoice_type_name')

        if InvoiceType.objects.filter(invoice_type_name=invoice_type_name).exists():
            return Response({'message': 'invoice_type_name is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_status = InvoiceType.objects.create(invoice_type_name=invoice_type_name)
            return Response({'result': 'invoice_type_name is created successfully!'}, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        data = request.data
        invoice_type_name = data.get('invoice_type_name')

        try:
            status_instance = InvoiceType.objects.get(id=pk)

            if InvoiceType.objects.filter(invoice_type_name=invoice_type_name).exclude(id=pk).exists():
                return Response({'message': 'DroneCategory name already exists. Choose a different name.'},
                                status=status.HTTP_400_BAD_REQUEST)

            status_instance.invoice_type_name = invoice_type_name
            status_instance.updated_date_time = datetime.now()
            status_instance.save()

            return Response({'message': 'invoice_type_name Updated!!'})
        except InvoiceType.DoesNotExist:
            return Response({'message': 'invoice_type_name id not found!!'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,pk):
        data=request.data
        invoice_type_name=data.get('invoice_type_name')

        if InvoiceType.objects.filter(id=pk).exists():
            data=InvoiceType.objects.filter(id=pk).delete()
            return Response({'message':'invoice_type_name deleted!!'})
        else:
            return Response({'result':'invoice_type_name id not found!!'})
class CustomerCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        date_of_birth = data.get('date_of_birth')
        gst = data.get('gst')
        pan = data.get('pan')
        cin = data.get('cin')
        shipping_address = data.get('shipping_address')
        billing_address = data.get('billing_address')
        pin_code=data.get('pin_code')
        address=data.get('address')
        shipping_pincode=data.get('shipping_pincode')
        billing_pincode=data.get('billing_pincode')
        gender = data.get('gender')
        created_by_id = data.get('created_by')
        category_id = data.get('category_id')
        invoice = data.get('invoice_id')
        role_id = data.get('role_id')

        # Validate if created_by_id is provided
        if created_by_id is None:
            return Response({"message": "created_by is required"}, status=status.HTTP_400_BAD_REQUEST)

        if invoice is None:
            return Response({"message": "invoice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if role_id is None:
            return Response({"message": "role_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the CustomUser instance for created_by
        try:
            created_by = CustomUser.objects.get(id=created_by_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with ID {} does not exist.".format(created_by_id)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = InvoiceType.objects.get(id=invoice)
        except InvoiceType.DoesNotExist:
            return Response({"message": "InvoiceType with ID {} does not exist.".format(invoice)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            role_id = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"message": "Role with ID {} does not exist.".format(role_id)},
                            status=status.HTTP_400_BAD_REQUEST)

        new_user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=phone,
            date_of_birth=date_of_birth,
            gst_number=data.get('gst'), 
            company_gst_num=data.get('gst'),
            pan_number=pan,
            company_cin_num=cin,
            shipping_address=shipping_address,
            billing_address=billing_address,
            gender=gender,
            pin_code= pin_code,
            address= address,
            shipping_pincode= shipping_pincode,
            billing_pincode= billing_pincode,
            category_id=category_id,
            created_by=created_by,
            invoice = invoice,
            role_id =role_id
        )

        try:
            new_user.save()
            return Response({"message": "Customer created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        partner_id = self.kwargs.get('partner_id')
        customer_id = self.request.query_params.get('customer_id')
        invoice_id = self.request.query_params.get('invoice_type_id')
        category_id = self.request.query_params.get('customer_type_id')

        if partner_id is None:
            customers = CustomUser.objects.filter(role_id__role_name="Customer")
        else:
            customers = CustomUser.objects.filter(created_by=partner_id)

        if customer_id:
            customers = customers.filter(id=customer_id)

        if invoice_id:
            customers = customers.filter(invoice__id=invoice_id)

        if category_id:
            customers = customers.filter(category__id=category_id)

        serializer = CustomUserSerializer(customers, many=True)
        serialized_data = serializer.data

        return Response(serialized_data, status=status.HTTP_200_OK)
class CustomerCategoryAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = CustomerCategorySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully", "category_id": serializer.data['id']}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, category_id, *args, **kwargs):
        category = self.get_object(category_id)
        data = request.data
        serializer = CustomerCategorySerializer(category, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, category_id=None, *args, **kwargs):
        if category_id is not None:
            # Retrieve a specific category by ID
            try:
                category = CustomerCategory.objects.get(id=category_id)
                serializer = CustomerCategorySerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomerCategory.DoesNotExist:
                return Response({"message": "Category with ID {} does not exist.".format(category_id)}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all categories
            categories = CustomerCategory.objects.all()
            serializer = CustomerCategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, category_id):
        try:
            return CustomerCategory.objects.get(id=category_id)
        except CustomerCategory.DoesNotExist:
            return Response({"message": "Category with ID {} does not exist.".format(category_id)}, status=status.HTTP_404_NOT_FOUND)




class GetPartnerDronesAPI(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if user_id:
            data = Order.objects.filter(user_id=user_id, order_status__status_name='Shipped').values('drone_id__drone_category__id', 'drone_id__drone_category__category_name').annotate(total_quantity=Sum('quantity')).distinct().values('drone_id__drone_category__id', 'drone_id__drone_category__category_name', 'total_quantity','drone_id__market_price','drone_id__our_price','drone_id','drone_id__drone_name')
            return Response({'data': data})
        else:
            return Response({'message':'user_id not found!!'})



from django.middleware.csrf import get_token

# Your decryption function remains the same as provided
def decrypt_by_symmetric_key(encrypted_text, key):
    # Paste your decryption logic here
    try:
        data_to_decrypt = base64.b64decode(encrypted_text)
        key_bytes = base64.b64decode(key)
        
        # Use AES decryption
        cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data_to_decrypt) + decryptor.finalize()
        
        # Remove PKCS7 padding
        decrypted_result = remove_padding(decrypted_data)
        return decrypted_result
    except Exception as ex:
        raise ex
    
def remove_padding(data):
    # Remove PKCS7 padding
    pad_length = data[-1]
    return data[:-pad_length]


@method_decorator(csrf_exempt, name='dispatch')
class AuthAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        csrf_token = get_token(request)
        url = "https://einv-apisandbox.nic.in/eivital/v1.04/auth/"
        headers = {
            "client_id": "AAGCE29TXPDW932",
            "client_secret": "76KkYyE3SGguAaOocIWw",
            "Gstin": "29AAGCE4783K1Z1",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
        }

        data = {
            "Data": "mT7Hse8LOO3fUl0DhDaJF4sffYqNT4ReWP752IuwjJR6XN6vqvL7TZ9rgHoVi86i+GSBXwBLuwLrENsu0RHUjWlegouTtEY/PQdzAIvdZz11IseJGHVbTT/zN5n4p7+hy1XbOmtOdZofJ53scISzOevHr/LGxodp0UarYooLV9R/J2Ao9FypePXSKN4WrcAfWklm26/FJmSTJyezluUMfMajSyfjLZigrg9aw/0mSK///cFzrJg2Ucm9npSxfA4K0iofO/GYCRDwS4YWKFa1jzpZ5R6p3nbYlZQqWx7CjwEoBSZULV1FAc7m14hxJI4rsU3TfkwpCHR95I2aNJrdFA=="
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            ewbres = response.json()
            data = ewbres.get("Data", {})
            
            existing_record = AuthToken.objects.first()
            
            if existing_record:
                provided_key = "bwqMewBhiNquDylcx67N1iXgBIvPF3PFKstOEsWZ7LI="  # app key
                encrypted_sek = data.get("Sek")
                decrypted_sek = decrypt_by_symmetric_key(encrypted_sek, provided_key)
                base64_decrypted_sek = base64.b64encode(decrypted_sek).decode('utf-8')
                
                existing_record.client_id = data.get("ClientId")
                existing_record.user_name = data.get("UserName")
                existing_record.auth_token = data.get("AuthToken")
                existing_record.sek = base64_decrypted_sek
                existing_record.token_expiry = data.get("TokenExpiry")
                existing_record.save()
            else:
                provided_key = "bwqMewBhiNquDylcx67N1iXgBIvPF3PFKstOEsWZ7LI="  # app key
                encrypted_sek = data.get("Sek")
                decrypted_sek = decrypt_by_symmetric_key(encrypted_sek, provided_key)
                base64_decrypted_sek = base64.b64encode(decrypted_sek).decode('utf-8')
                
                auth_token_instance = AuthToken.objects.create(
                    client_id=data.get("ClientId"),
                    user_name=data.get("UserName"),
                    auth_token=data.get("AuthToken"),
                    sek=base64_decrypted_sek,
                    token_expiry=data.get("TokenExpiry"),
                )
                auth_token_instance.save()

            return Response({"message":"Auth Token and necessary things generated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": f"Failed to retrieve data. Status code: {response.status_code}"},
                status=response.status_code,
            )

def decrypt_aes_256_ecb(data, key):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    return decrypted_data

class GetCompanyDetailsAPIView(generics.RetrieveAPIView):
    def clean_string(self, input_string):
        # Remove non-printable ASCII characters and control characters
        printable_chars = set(string.printable)
        cleaned_string = ''.join(filter(lambda x: x in printable_chars, input_string))
        return cleaned_string

    def extract_pan_number(self, gstin):
        # Assuming GSTIN is of 15 characters, remove the first 2 and last 3 characters to get the PAN number
        return gstin[2:-3]

    def get(self, request, *args, **kwargs):
        try:
            auth_token = AuthToken.objects.first()
            if auth_token:
                sek = base64.b64decode(auth_token.sek)  # Assuming 'sek' is stored in base64

                params = self.kwargs.get('params')  # Get the parameter from the URL

                # Construct the URL with the received params
                url = f"https://einv-apisandbox.nic.in/eivital/v1.03/Master/gstin/{params}/"

                headers = {
                    "client-id": auth_token.client_id,
                    "client-secret": "76KkYyE3SGguAaOocIWw",
                    "gstin": "29AAGCE4783K1Z1",
                    "user_name": auth_token.user_name,
                    "authtoken": auth_token.auth_token,
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    ewbres = response.json()
                    encrypted_data = base64.b64decode(ewbres["Data"])
                    decrypted_data = decrypt_aes_256_ecb(encrypted_data, sek)
                    decrypted_string = decrypted_data.decode("utf-8")

                    # Clean the decrypted string
                    cleaned_decrypted_string = self.clean_string(decrypted_string)

                    # Extract PAN number from the GSTIN
                    pan_number = self.extract_pan_number(params)

                    # Include PAN number inside 'companydetails' key
                    company_details = {'pan_number': pan_number, **json.loads(cleaned_decrypted_string)}

                    return Response({'companydetails': company_details}, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": f"Failed to retrieve data. Status code: {response.status_code}"},
                        status=response.status_code,
                    )
            else:
                return Response({"error": "No AuthToken found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CompanyDetailsAPIView(generics.RetrieveAPIView):
#     def clean_string(self, input_string):
#         # Remove non-printable ASCII characters and control characters
#         printable_chars = set(string.printable)
#         cleaned_string = ''.join(filter(lambda x: x in printable_chars, input_string))
#         return cleaned_string

#     def get(self, request, *args, **kwargs):
#         try:
#             auth_token = AuthToken.objects.first()
#             if auth_token:
#                 sek = base64.b64decode(auth_token.sek)  # Assuming 'sek' is stored in base64
                
#                 params = self.kwargs.get('params')  # Get the parameter from the URL
                
#                 # Construct the URL with the received params
#                 url = f"https://einv-apisandbox.nic.in/eivital/v1.03/Master/gstin/{params}/"
                
#                 headers = {
#                     "client-id": auth_token.client_id,
#                     "client-secret": "76KkYyE3SGguAaOocIWw",
#                     "gstin": "29AAGCE4783K1Z1",
#                     "user_name": auth_token.user_name,
#                     "authtoken": auth_token.auth_token,
#                 }

#                 response = requests.get(url, headers=headers)

#                 if response.status_code == 200:
#                     ewbres = response.json()
#                     encrypted_data = base64.b64decode(ewbres["Data"])
#                     decrypted_data = decrypt_aes_256_ecb(encrypted_data, sek)
#                     decrypted_string = decrypted_data.decode("utf-8")
                    
#                     # Clean the decrypted string
#                     cleaned_decrypted_string = self.clean_string(decrypted_string)
                    
#                     return Response({'companydetails': json.loads(cleaned_decrypted_string)}, status=status.HTTP_200_OK)
#                 else:
#                     return Response(
#                         {"error": f"Failed to retrieve data. Status code: {response.status_code}"},
#                         status=response.status_code,
#                     )
#             else:
#                 return Response({"error": "No AuthToken found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import hashlib
import random
import time
import json
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction



from django.shortcuts import get_object_or_404

class AddItemAPI(APIView):
    def generate_serial_numbers(self, quantity):
        # Generate a list of unique serial numbers
        serial_numbers = []
        for _ in range(quantity):
            # Create a unique identifier based on timestamp and random value
            timestamp = str(int(time.time()))
            random_value = str(random.randint(1000, 9999))  # Change the range if needed
            unique_string = f"{timestamp}-{random_value}"

            # Hash the unique string using MD5 and take the first 6 characters
            hashed_value = hashlib.md5(unique_string.encode()).hexdigest()[:6]
            serial_numbers.append(hashed_value)

        return serial_numbers

    def create_invoice_number(self):
        try:
            while True:
                # Generate a unique UUID
                unique_uuid = uuid.uuid4()

                # Convert UUID to a 4-digit string and prepend "IAMX"
                invoice_number = f"IAMX-{int(unique_uuid.int % 1e4):04d}"

                # Check if the generated invoice_number is unique in the AddItem table
                if not AddItem.objects.filter(invoice_number=invoice_number).exists() and \
                        not CustomInvoice.objects.filter(invoice_number=invoice_number).exists():
                    return invoice_number
        except Exception as e:
            # Handle any exceptions that may occur during invoice_number generation
            raise RuntimeError(f"Error generating invoice_number: {str(e)}")



    def get(self, request, item_id=None):
        if item_id:
            # Retrieve a specific record by ID
            add_item_instance = get_object_or_404(AddItem, id=item_id)

            invoice_status = add_item_instance.invoice_status
            invoice_status_name = invoice_status.invoice_status_name if invoice_status else None
            invoice_status_id = invoice_status.id if invoice_status else None

            customer_instance = add_item_instance.customer_id
            partner_instance = add_item_instance.owner_id


            # Fetching customer_type_id from AddItem instance
            customer_type_id = add_item_instance.customer_type_id.id if add_item_instance.customer_type_id else None
            customer_type_name = add_item_instance.customer_type_id.name if add_item_instance.customer_type_id else None

            customer_details = {
                'id': customer_instance.id,
                'username': customer_instance.username,
                'email': customer_instance.email,
                'first_name': customer_instance.first_name,
                'full_name': customer_instance.get_full_name(),
                'mobile_number': customer_instance.mobile_number,
                'address': customer_instance.address,
                'pin_code': customer_instance.pin_code,
                'pan_number': customer_instance.pan_number,
                'profile_pic': customer_instance.profile_pic.url if customer_instance.profile_pic else None,
                'company_name': customer_instance.company_name,
                'company_email': customer_instance.company_email,
                'company_address': customer_instance.company_address,
                'shipping_address': customer_instance.shipping_address,
                'billing_address': customer_instance.billing_address,
                'company_phn_number': customer_instance.company_phn_number,
                'company_gst_num': customer_instance.company_gst_num,
                'company_cin_num': customer_instance.company_cin_num,
                'company_logo': customer_instance.company_logo.url if customer_instance.company_logo else None,
                'role_id': customer_instance.role_id.id,
                'created_date_time': customer_instance.created_date_time,
                'updated_date_time': customer_instance.updated_date_time,
                'status': customer_instance.status,
                'location': customer_instance.location,
                'reason': customer_instance.reason,
                'partner_initial_update': customer_instance.partner_initial_update,
                'gst_number': customer_instance.gst_number,
                'category': customer_instance.category.id if customer_instance.category else None,
                'date_of_birth': customer_instance.date_of_birth,
                'gender': customer_instance.gender,
                'created_by': customer_instance.created_by.id if customer_instance.created_by else None,
                'invoice': customer_instance.invoice.id if customer_instance.invoice else None,
                'shipping_pincode': customer_instance.shipping_pincode,
                'billing_pincode': customer_instance.billing_pincode,
                # 'state_name': customer_instance.state_name,
                # 'state_code': customer_instance.state_code,
                'shipping_state': customer_instance.shipping_state,
                'shipping_state_code': customer_instance.shipping_state_code,
                'shipping_state_city': customer_instance.shipping_state_city,
                'shipping_state_country': customer_instance.shipping_state_country,
                'billing_state': customer_instance.billing_state,
                'billing_state_code': customer_instance.billing_state_code,
                'billing_state_city': customer_instance.billing_state_city,
                'billing_state_country': customer_instance.billing_state_country,
                'category_id':customer_type_id,
                'category_name':customer_type_name,
                

            }

            partner_details = {
                'id': partner_instance.id,
                'username': partner_instance.username,
                'email': partner_instance.email,
                'first_name': partner_instance.first_name,
                'full_name': partner_instance.get_full_name(),
                'mobile_number': partner_instance.mobile_number,
                'address': partner_instance.address,
                'pin_code': partner_instance.pin_code,
                'pan_number': partner_instance.pan_number,
                'profile_pic': partner_instance.profile_pic.url if partner_instance.profile_pic else None,
                'company_name': partner_instance.company_name,
                'company_email': partner_instance.company_email,
                'company_address': partner_instance.company_address,
                'shipping_address': partner_instance.shipping_address,
                'billing_address': partner_instance.billing_address,
                'company_phn_number': partner_instance.company_phn_number,
                'company_gst_num': partner_instance.company_gst_num,
                'company_cin_num': partner_instance.company_cin_num,
                'company_logo': partner_instance.company_logo.url if partner_instance.company_logo else None,
                'role_id': partner_instance.role_id.id,
                'created_date_time': partner_instance.created_date_time,
                'updated_date_time': partner_instance.updated_date_time,
                'status': partner_instance.status,
                'location': partner_instance.location,
                'reason': partner_instance.reason,
                'partner_initial_update': partner_instance.partner_initial_update,
                'gst_number': partner_instance.gst_number,
                'category': partner_instance.category.id if partner_instance.category else None,
                'date_of_birth': partner_instance.date_of_birth,
                'gender': partner_instance.gender,
                'created_by': partner_instance.created_by.id if partner_instance.created_by else None,
                'invoice': partner_instance.invoice.id if partner_instance.invoice else None,
                'shipping_pincode': partner_instance.shipping_pincode,
                'billing_pincode': partner_instance.billing_pincode,
                # 'state_name': partner_instance.state_name,
                # 'state_code': partner_instance.state_code,
                'shipping_state': partner_instance.shipping_state,
                'shipping_state_code': partner_instance.shipping_state_code,
                'shipping_state_city': partner_instance.shipping_state_city,
                'shipping_state_country': partner_instance.shipping_state_country,
                'billing_state': partner_instance.billing_state,
                'billing_state_code': partner_instance.billing_state_code,
                'billing_state_city': partner_instance.billing_state_city,
                'billing_state_country': partner_instance.billing_state_country,

            }

            invoice_type_details = {
                'id': add_item_instance.invoice_type_id.id,
                'name': add_item_instance.invoice_type_id.invoice_type_name,
            }
            customer_category = {
                "category_id": add_item_instance.customer_id.category.id if add_item_instance.customer_id and 		add_item_instance.customer_id.category else None,
                "category_name": add_item_instance.customer_id.category.name if add_item_instance.customer_id and add_item_instance.customer_id.category else None,
            }
            

            dronedetails = add_item_instance.dronedetails or []

            drone_info_list = []

            if dronedetails:
                for drone_detail in dronedetails:
                    drone_id = drone_detail["drone_id"]
                    quantity = drone_detail["quantity"]
                    price = drone_detail["price"]
                    units = drone_detail.get("units")
                    serial_numbers = drone_detail.get("serial_numbers", [])
                    hsn_number = drone_detail["hsn_number"]
                    item_total_price = drone_detail.get("item_total_price", 0)
                    discount = drone_detail.get("discount", 0)
                    igst = drone_detail.get("igst", 0)
                    cgst = drone_detail.get("cgst", 0)
                    sgst = drone_detail.get("sgst", 0)
                    discount_amount = drone_detail.get("discount_amount", 0)
                    price_after_discount = drone_detail.get("price_after_discount", 0)
                    igst_percentage = drone_detail.get("igst_percentage", 0)
                    cgst_percentage = drone_detail.get("cgst_percentage", 0)
                    sgst_percentage = drone_detail.get("sgst_percentage", 0)
                    total = drone_detail.get("total", 0)
                    created_datetime = drone_detail.get("created_datetime", 0)
                    updated_datetime = drone_detail.get("updated_datetime", 0)




                    try:
                        drone = Drone.objects.get(id=drone_id)
                        drone_ownership = DroneOwnership.objects.filter(user=partner_instance, drone=drone_id).first()
                        remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                        drone_info = {
                            "drone_id": drone.id,
                            "drone_name": drone.drone_name,
                            "drone_category": drone.drone_category.category_name if drone.drone_category else None,
                            "quantity": quantity,
                            "price": price,
                            "serial_numbers": serial_numbers,
                            "hsn_number": hsn_number,
                            "item_total_price": item_total_price,
                            "remaining_quantity": remaining_quantity,
                            "discount" :discount,
                            "igst" : igst,
                            "cgst" : cgst,
                            "sgst" : sgst,
                            "units":units,
                            "discount_amount" : discount_amount,
                            "price_after_discount" : price_after_discount,
                            "igst_percentage" : igst_percentage,
                            "cgst_percentage" : cgst_percentage,
                            "sgst_percentage" : sgst_percentage,
                            "total" :total,
                            "created_datetime":created_datetime,
                            "updated_datetime":updated_datetime,

                        }
                        drone_info_list.append(drone_info)
                    except Drone.DoesNotExist:
                        pass

            response_data = {
                'id': add_item_instance.id,
                'created_date_time': add_item_instance.created_date_time,
                'updated_date_time': add_item_instance.updated_date_time,
                'customer_details': customer_details,
                'owner_details': partner_details,
                'invoice_type_details': invoice_type_details,
                'customer_category':customer_category,
                'dronedetails': drone_info_list,
                "invoice_number": add_item_instance.invoice_number,
                'signature_url': add_item_instance.signature.url if add_item_instance.signature else None,
                'invoice_status': invoice_status_name,
                'invoice_status_id': invoice_status_id,
                'amount_to_pay' : add_item_instance.amount_to_pay,
                'sum_of_item_total_price' : add_item_instance.sum_of_item_total_price,
                'sum_of_igst_percentage' : add_item_instance.sum_of_igst_percentage,
                'sum_of_cgst_percentage' : add_item_instance.sum_of_cgst_percentage,
                'sum_of_sgst_percentage' : add_item_instance.sum_of_sgst_percentage,
                'sum_of_discount_amount' : add_item_instance.sum_of_discount_amount,
                'sum_of_price_after_discount': add_item_instance.sum_of_price_after_discount,


            }

        else:
            # Retrieve all records
            all_add_items = AddItem.objects.all()
            records_list = []

            for add_item_instance in all_add_items:
                customer_instance = add_item_instance.customer_id
                partner_instance = add_item_instance.owner_id

                invoice_status = add_item_instance.invoice_status
                invoice_status_name = invoice_status.invoice_status_name if invoice_status else None
                invoice_status_id = invoice_status.id if invoice_status else None

                customer_details = {
                    'id': customer_instance.id,
                    'username': customer_instance.username,
                    'email': customer_instance.email,
                    'first_name': customer_instance.first_name,
                    'full_name': customer_instance.get_full_name(),
                    'mobile_number': customer_instance.mobile_number,
                    'address': customer_instance.address,
                    'pin_code': customer_instance.pin_code,
                    'pan_number': customer_instance.pan_number,
                    'profile_pic': customer_instance.profile_pic.url if customer_instance.profile_pic else None,
                    'company_name': customer_instance.company_name,
                    'company_email': customer_instance.company_email,
                    'company_address': customer_instance.company_address,
                    'shipping_address': customer_instance.shipping_address,
                    'billing_address': customer_instance.billing_address,
                    'company_phn_number': customer_instance.company_phn_number,
                    'company_gst_num': customer_instance.company_gst_num,
                    'company_cin_num': customer_instance.company_cin_num,
                    'company_logo': customer_instance.company_logo.url if customer_instance.company_logo else None,
                    'role_id': customer_instance.role_id.id,
                    'created_date_time': customer_instance.created_date_time,
                    'updated_date_time': customer_instance.updated_date_time,
                    'status': customer_instance.status,
                    'location': customer_instance.location,
                    'reason': customer_instance.reason,
                    'partner_initial_update': customer_instance.partner_initial_update,
                    'gst_number': customer_instance.gst_number,
                    'category': customer_instance.category.id if customer_instance.category else None,
                    'date_of_birth': customer_instance.date_of_birth,
                    'gender': customer_instance.gender,
                    'created_by': customer_instance.created_by.id if customer_instance.created_by else None,
                    'invoice': customer_instance.invoice.id if customer_instance.invoice else None,
                    'shipping_pincode': customer_instance.shipping_pincode,
                    'billing_pincode': customer_instance.billing_pincode,
                    # 'state_name': customer_instance.state_name,
                    # 'state_code': customer_instance.state_code,
                    'shipping_state': customer_instance.shipping_state,
                    'shipping_state_code': customer_instance.shipping_state_code,
                    'shipping_state_city': customer_instance.shipping_state_city,
                    'shipping_state_country': customer_instance.shipping_state_country,
                    'billing_state': customer_instance.billing_state,
                    'billing_state_code': customer_instance.billing_state_code,
                    'billing_state_city': customer_instance.billing_state_city,
                    'billing_state_country': customer_instance.billing_state_country,
                }

                partner_details = {
                    'id': partner_instance.id,
                    'username': partner_instance.username,
                    'email': partner_instance.email,
                    'first_name': partner_instance.first_name,
                    'full_name': partner_instance.get_full_name(),
                    'mobile_number': partner_instance.mobile_number,
                    'address': partner_instance.address,
                    'pin_code': partner_instance.pin_code,
                    'pan_number': partner_instance.pan_number,
                    'profile_pic': partner_instance.profile_pic.url if partner_instance.profile_pic else None,
                    'company_name': partner_instance.company_name,
                    'company_email': partner_instance.company_email,
                    'company_address': partner_instance.company_address,
                    'shipping_address': partner_instance.shipping_address,
                    'billing_address': partner_instance.billing_address,
                    'company_phn_number': partner_instance.company_phn_number,
                    'company_gst_num': partner_instance.company_gst_num,
                    'company_cin_num': partner_instance.company_cin_num,
                    'company_logo': partner_instance.company_logo.url if partner_instance.company_logo else None,
                    'role_id': partner_instance.role_id.id,
                    'created_date_time': partner_instance.created_date_time,
                    'updated_date_time': partner_instance.updated_date_time,
                    'status': partner_instance.status,
                    'location': partner_instance.location,
                    'reason': partner_instance.reason,
                    'partner_initial_update': partner_instance.partner_initial_update,
                    'gst_number': partner_instance.gst_number,
                    'category': partner_instance.category.id if partner_instance.category else None,
                    'date_of_birth': partner_instance.date_of_birth,
                    'gender': partner_instance.gender,
                    'created_by': partner_instance.created_by.id if partner_instance.created_by else None,
                    'invoice': partner_instance.invoice.id if partner_instance.invoice else None,
                    'shipping_pincode': partner_instance.shipping_pincode,
                    'billing_pincode': partner_instance.billing_pincode,
                    # 'state_name': partner_instance.state_name,
                    # 'state_code': partner_instance.state_code,
                    'shipping_state': partner_instance.shipping_state,
                    'shipping_state_code': partner_instance.shipping_state_code,
                    'shipping_state_city': partner_instance.shipping_state_city,
                    'shipping_state_country': partner_instance.shipping_state_country,
                    'billing_state': partner_instance.billing_state,
                    'billing_state_code': partner_instance.billing_state_code,
                    'billing_state_city': partner_instance.billing_state_city,
                    'billing_state_country': partner_instance.billing_state_country,
                }

                invoice_type_details = {
                    'id': add_item_instance.invoice_type_id.id,
                    'name': add_item_instance.invoice_type_id.invoice_type_name,
                }
                
                customer_category = {
                "category_id": add_item_instance.customer_id.category.id if add_item_instance.customer_id and add_item_instance.customer_id.category else None,
                "category_name": add_item_instance.customer_id.category.name if add_item_instance.customer_id and add_item_instance.customer_id.category else None,
            }

                dronedetails = add_item_instance.dronedetails or []

                drone_info_list = []

                if dronedetails:
                    for drone_detail in dronedetails:
                        drone_id = drone_detail["drone_id"]
                        quantity = drone_detail["quantity"]
                        price = drone_detail["price"]
                        units = drone_detail.get("units")
                        serial_numbers = drone_detail.get("serial_numbers", [])
                        hsn_number = drone_detail["hsn_number"]
                        item_total_price = drone_detail.get("item_total_price", 0)
                        discount = drone_detail.get("discount", 0)
                        igst = drone_detail.get("igst", 0)
                        cgst = drone_detail.get("cgst", 0)
                        sgst = drone_detail.get("sgst", 0)
                        discount_amount = drone_detail.get("discount_amount", 0)
                        price_after_discount = drone_detail.get("price_after_discount", 0)
                        igst_percentage = drone_detail.get("igst_percentage", 0)
                        cgst_percentage = drone_detail.get("cgst_percentage", 0)
                        sgst_percentage = drone_detail.get("sgst_percentage", 0)
                        created_datetime = drone_detail.get("created_datetime", 0)
                        updated_datetime = drone_detail.get("updated_datetime", 0)
                        total = drone_detail.get("total", 0)

                        try:
                            drone = Drone.objects.get(id=drone_id)
                            drone_ownership = DroneOwnership.objects.filter(user=partner_instance,
                                                                            drone=drone_id).first()
                            remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                            drone_info = {
                                "drone_id": drone.id,
                                "drone_name": drone.drone_name,
                                "drone_category": drone.drone_category.category_name if drone.drone_category else None,
                                "quantity": quantity,
                                "price": price,
                                "units":units,
                                "serial_numbers": serial_numbers,
                                "hsn_number": hsn_number,
                                "item_total_price": item_total_price,
                                "remaining_quantity": remaining_quantity,
                                "discount": discount,
                                "igst": igst,
                                "cgst": cgst,
                                "sgst": sgst,
                                "discount_amount": discount_amount,
                                "price_after_discount": price_after_discount,
                                "igst_percentage": igst_percentage,
                                "cgst_percentage": cgst_percentage,
                                "sgst_percentage": sgst_percentage,
                                "created_datetime":created_datetime,
                                "updated_datetime":updated_datetime,
                                "total": total,
                            }
                            drone_info_list.append(drone_info)
                        except Drone.DoesNotExist:
                            pass

                record_details = {
                    'id': add_item_instance.id,
                    'created_date_time': add_item_instance.created_date_time,
                    'updated_date_time': add_item_instance.updated_date_time,
                    'customer_details': customer_details,
                    'owner_details': partner_details,
                    'invoice_type_details': invoice_type_details,
                    'customer_category':customer_category,
                    'dronedetails': drone_info_list,
                    'signature_url': add_item_instance.signature.url if add_item_instance.signature else None,
                    'invoice_status': invoice_status_name,
                    'invoice_status_id': invoice_status_id,
                    'amount_to_pay': add_item_instance.amount_to_pay,
                    'sum_of_item_total_price': add_item_instance.sum_of_item_total_price,
                    'sum_of_igst_percentage': add_item_instance.sum_of_igst_percentage,
                    'sum_of_cgst_percentage': add_item_instance.sum_of_cgst_percentage,
                    'sum_of_sgst_percentage': add_item_instance.sum_of_sgst_percentage,
                    'sum_of_discount_amount': add_item_instance.sum_of_discount_amount,
                    'sum_of_price_after_discount': add_item_instance.sum_of_price_after_discount,

                }

                records_list.append(record_details)

            response_data = records_list

        return Response(response_data, status=status.HTTP_200_OK)


    def post(self, request):
        data = request.data
        items = data.get('items', [])
        owner_id = data.get('owner_id')
        customer_type_id = data.get('customer_type_id')
        customer_id = data.get('customer_id')
        invoice_type_id = data.get('invoice_type_id')
        partner_instance = get_object_or_404(CustomUser, id=owner_id)
        all_serialnumbers = []

        dronedetails_lists = AddItem.objects.values_list('dronedetails', flat=True)

        for dronedetails_list in dronedetails_lists:
            if dronedetails_list:
                serial_numbers = [serial_number for entry in dronedetails_list for serial_number in
                                  entry.get('serial_numbers', [])]
                all_serialnumbers.extend(serial_numbers)

        items_data = []
        dronedetails = []
        total_price = Decimal('0.00')
        total_price_with_additional_percentages = Decimal('0.00')
        all_serial_numbers = set()

        is_super_admin = partner_instance.role_id.role_name == 'Super_admin'

        with transaction.atomic():
            entered_serial_numbers = []
            for item_data in items:
                drone_id = item_data.get('drone_id')
                quantity = item_data.get('quantity')
                discount = item_data.get('discount')[0] if isinstance(item_data.get('discount'),
                                                                      tuple) else item_data.get('discount')
                igst = item_data.get('igst')[0] if isinstance(item_data.get('igst'), tuple) else item_data.get('igst')
                cgst = item_data.get('cgst')[0] if isinstance(item_data.get('cgst'), tuple) else item_data.get('cgst')
                sgst = item_data.get('sgst')[0] if isinstance(item_data.get('sgst'), tuple) else item_data.get('sgst')
                item_total_price = round((quantity) * (item_data.get('price')), 2)
                discount_amount = round((discount / 100) * item_total_price, 2)
                user_id = get_object_or_404(CustomUser, id=customer_id)

                serial_numbers = item_data.get('serial_numbers', [])
                entered_serial_numbers.extend(serial_numbers)

                if quantity != len(serial_numbers):
                    return Response(
                        {'message': f"Quantity and the number of serial numbers must be equal in each drone entry"},
                        status=status.HTTP_400_BAD_REQUEST)

                if len(set(serial_numbers)) != len(serial_numbers):
                    return Response({'message': f"Serial numbers must be unique within each drone entry"},
                                    status=status.HTTP_400_BAD_REQUEST)

                if any(serial_number in all_serial_numbers for serial_number in serial_numbers):
                    return Response({'message': f"Serial numbers must be unique across all drone entries"},
                                    status=status.HTTP_400_BAD_REQUEST)

                all_serial_numbers.update(serial_numbers)
                price_after_discount = round(item_total_price - discount_amount, 2)
                igst_percentage = round((igst / 100) * (item_total_price - discount_amount), 2)
                cgst_percentage = round((cgst / 100) * (item_total_price - discount_amount), 2)
                sgst_percentage = round((sgst / 100) * (item_total_price - discount_amount), 2)
                total = round(
                    (item_total_price - discount_amount) + igst_percentage + cgst_percentage + sgst_percentage, 2)

                dronedetails.append({
                    'drone_id': drone_id,
                    'quantity': quantity,
                    'price': item_data.get('price'),
                    'serial_numbers': serial_numbers,
                    'hsn_number': item_data.get('hsn_number'),
                    'units': item_data.get('units'),
                    'item_total_price': item_total_price,
                    'discount': discount,
                    'igst': igst,
                    'cgst': cgst,
                    'sgst': sgst,
                    'created_datetime': [timezone.now().isoformat()],
                    'updated_datetime': [timezone.now().isoformat()],
                    'discount_amount': discount_amount,
                    'price_after_discount': price_after_discount,
                    'igst_percentage': igst_percentage,
                    'cgst_percentage': cgst_percentage,
                    'sgst_percentage': sgst_percentage,
                    'total': total,
                })

                items_data.append({
                    'drone_id': drone_id,
                    'price': item_data.get('price'),
                    'serial_numbers': serial_numbers,
                    'hsn_number': item_data.get('hsn_number'),
                    'units': item_data.get('units'),
                    'item_total_price': item_total_price,
                    'discount': discount,
                    'igst': igst,
                    'cgst': cgst,
                    'sgst': sgst,
                    'created_datetime': [timezone.now().isoformat()],
                    'updated_datetime': [timezone.now().isoformat()],
                    'discount_amount': discount_amount,
                    'price_after_discount': price_after_discount,
                    'igst_percentage': igst_percentage,
                    'cgst_percentage': cgst_percentage,
                    'sgst_percentage': sgst_percentage,
                    'total': total,
                })

                total_price += Decimal(item_data.get('price')) * quantity
                total_price_with_additional_percentages += Decimal(item_data.get('price')) * quantity

            duplicate_serial_numbers = []
            for entered_serial in entered_serial_numbers:
                if entered_serial in all_serialnumbers:
                    duplicate_serial_numbers.append(entered_serial)

            if duplicate_serial_numbers:
                return Response({
                    'message': f"Serial numbers {', '.join(map(str, duplicate_serial_numbers))} already exist in the table"},
                    status=status.HTTP_400_BAD_REQUEST)

            if len(dronedetails) == 0:
                return Response({'message': 'Dronedetails cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

            for item_data in items:
                drone_id = item_data.get('drone_id')
                quantity = item_data.get('quantity')
                user_id = get_object_or_404(CustomUser, id=customer_id)

                if not is_super_admin:
                    drone_ownership = DroneOwnership.objects.filter(user=owner_id, drone=drone_id).first()
                    if not drone_ownership or drone_ownership.quantity < quantity:
                        return Response({'message': f"Not enough quantity available for drone_id {drone_id}"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    drone_ownership.quantity = F('quantity') - quantity
                    drone_ownership.save()

                    if drone_ownership.quantity == 0:
                        return Response({'message': f"Drone_id {drone_id} is out of stock"},
                                        status=status.HTTP_400_BAD_REQUEST)
                                        
                        """inventory count for partner"""
                    if partner_instance.role_id.role_name == 'Partner':
                        # Update the inventory count for the specific user
                        partner_instance.inventory_count = F('inventory_count') - quantity
                        partner_instance.save()
                        """end of inventory count"""                                        

            else:
                try:
                    draft_status = InvoiceStatus.objects.get(invoice_status_name='Inprogress')
                except InvoiceStatus.DoesNotExist:
                    draft_status = InvoiceStatus.objects.create(invoice_status_name='Inprogress')
                new_item = AddItem.objects.create(
                    customer_type_id=get_object_or_404(CustomerCategory, id=customer_type_id),
                    customer_id=get_object_or_404(CustomUser, id=customer_id),
                    owner_id=partner_instance,
                    invoice_type_id=get_object_or_404(InvoiceType, id=invoice_type_id),
                    invoice_status=draft_status,
                )

                new_item.invoice_number = self.create_invoice_number()
                new_item.save()

                new_item.dronedetails = dronedetails
                new_item.total_price = total_price
                new_item.total_price_with_additional_percentages = total_price_with_additional_percentages
                amount_to_pay = round(sum(item['total'] for item in dronedetails), 2)
                sum_of_item_total_price = round(sum(item['item_total_price'] for item in dronedetails), 2)
                sum_of_igst_percentage = round(sum(item['igst_percentage'] for item in dronedetails), 2)
                sum_of_cgst_percentage = round(sum(item['cgst_percentage'] for item in dronedetails), 2)
                sum_of_sgst_percentage = round(sum(item['sgst_percentage'] for item in dronedetails), 2)
                sum_of_discount_amount = round(sum(item['discount_amount'] for item in dronedetails), 2)
                sum_of_price_after_discount = round(sum(item['price_after_discount'] for item in dronedetails), 2)

                new_item.amount_to_pay = amount_to_pay
                new_item.sum_of_item_total_price = sum_of_item_total_price
                new_item.sum_of_igst_percentage = sum_of_igst_percentage
                new_item.sum_of_cgst_percentage = sum_of_cgst_percentage
                new_item.sum_of_sgst_percentage = sum_of_sgst_percentage
                new_item.sum_of_discount_amount = sum_of_discount_amount
                new_item.sum_of_price_after_discount = sum_of_price_after_discount

                new_item.save()

                response_data = {
                    'message': 'Items are created successfully!',
                    'item_id': new_item.id,
                    'items_data': [
                        {
                            'drone_id': item_data['drone_id'],
                            'price': item_data['price'],
                            'serial_numbers': item_data['serial_numbers'],
                            'hsn_number': item_data['hsn_number'],
                            'item_total_price': round(item_data['item_total_price'], 2),
                            'discount': round(item_data['discount'], 2),
                            'igst': round(item_data['igst'], 2),
                            'cgst': round(item_data['cgst'], 2),
                            'sgst': round(item_data['sgst'], 2),
                            'remaining_quantity': None if is_super_admin else DroneOwnership.objects.filter(
                                user=owner_id, drone=item_data['drone_id']
                            ).first().quantity
                        } for item_data in items_data
                    ],
                    'Amount_to_pay': amount_to_pay,
                    "sum_of_item_total_price": sum_of_item_total_price,
                    "sum_of_igst_percentage": sum_of_igst_percentage,
                    "sum_of_cgst_percentage": sum_of_cgst_percentage,
                    "sum_of_sgst_percentage": sum_of_sgst_percentage,
                    "sum_of_discount_amount": sum_of_discount_amount,
                    "sum_of_price_after_discount": sum_of_price_after_discount
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
                
                
                
    def calculate_item_total_price(self, price, quantity):
        return str(round(Decimal(price) * Decimal(quantity), 2))

    def put(self, request, item_id):
        def check_unique_serial_numbers(new_items):
            serial_numbers_set = set()

            for entry in new_items:
                for serial_number in entry['serial_numbers']:
                    if serial_number in serial_numbers_set:
                        return False  # Duplicate serial number found
                    else:
                        serial_numbers_set.add(serial_number)

            return True

        item = get_object_or_404(AddItem, id=item_id)
        inventory_partner = item.owner_id        
        dic_item = item.dronedetails
        data = request.data
        new_items = data.get('items', [])
        update_list = []
        add_list = []
        total_price_with_additional_percentages = Decimal('0.00')

        all_serial = []

        all_items_except_given_id = AddItem.objects.exclude(id=item_id).values('id', 'dronedetails')
        for item_data in all_items_except_given_id:
            for drone_detail in item_data['dronedetails']:
                serial_numbers = drone_detail.get('serial_numbers', [])
                all_serial.extend(serial_numbers)

        print("All Serial Numbers:", all_serial)

        if not check_unique_serial_numbers(new_items):
            return Response({'message': f"Serial numbers must be unique with all drone entry"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            pass

        with transaction.atomic():
            duplicate_serial = []
            for j in new_items:
                for serial_number in j.get('serial_numbers', []):
                    if serial_number in all_serial:
                        duplicate_serial.append(serial_number)
                        # Return a response with an error message
                        # return Response({'message': f"Serial number '{serial_number}' already exists in other items."},
                        #                 status=status.HTTP_400_BAD_REQUEST)
                if duplicate_serial:
                    error_message = f"Serial numbers {', '.join(map(repr, duplicate_serial))} already exist in other items."
                    return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

                drone_exists = any(drone['drone_id'] == j['drone_id'] for drone in item.dronedetails)
                drone_id = j.get('drone_id')
                drone_name = Drone.objects.filter(id=drone_id).first().drone_name if drone_id else 'Unknown Drone'

                if not drone_exists:
                    # Drone not in dronedetails, check in DroneOwnership
                    if item.owner_id.role_id.role_name == 'Super_admin':
                        # If owner is Super_admin, just add the new drone to dronedetails
                        new_drone = {
                            'drone_id': j['drone_id'],
                            'quantity': j['quantity'],
                            'price': j['price'],
                            'serial_numbers': j['serial_numbers'],
                            'hsn_number': j['hsn_number'],
                            'units': j['units'],
                            'discount': j.get('discount', 0),
                            'igst': j.get('igst', 0),
                            'cgst': j.get('cgst', 0),
                            'sgst': j.get('sgst', 0),
                            'updated_datetime': timezone.now().isoformat(),
                        }
                        # Calculate additional fields for the new drone
                        new_drone["item_total_price"] = self.calculate_item_total_price(new_drone["price"],
                                                                                        new_drone["quantity"])
                        new_drone["discount_amount"] = round((new_drone["discount"] / 100) * (
                            new_drone["quantity"]) * (new_drone["price"]), 2)
                        new_drone["price_after_discount"] = round((new_drone["quantity"]) * (new_drone["price"]) - (
                                new_drone["discount"] / 100) * (
                                                                      new_drone["quantity"]) * (
                                                                      new_drone["price"]), 2)
                        new_drone["igst_percentage"] = round((new_drone["igst"] / 100) * (
                                (new_drone["quantity"]) * (new_drone["price"]) - (
                                new_drone["discount"] / 100) * (
                                    new_drone["quantity"]) * (new_drone["price"])), 2)
                        new_drone["cgst_percentage"] = round((new_drone["cgst"] / 100) * (
                                (new_drone["quantity"]) * (new_drone["price"]) - (
                                new_drone["discount"] / 100) * (
                                    new_drone["quantity"]) * (new_drone["price"])), 2)
                        new_drone["sgst_percentage"] = round((new_drone["sgst"] / 100) * (
                                (new_drone["quantity"]) * (new_drone["price"]) - (
                                new_drone["discount"] / 100) * (
                                    new_drone["quantity"]) * (new_drone["price"])), 2)
                        new_drone["total"] = round(((new_drone["quantity"]) * (new_drone["price"]) - (
                                new_drone["discount"] / 100) * (
                                                        new_drone["quantity"]) * (
                                                        new_drone["price"])) + new_drone[
                                                       "igst_percentage"] + new_drone["cgst_percentage"] + new_drone[
                                                       "sgst_percentage"], 2)
                        item.dronedetails.append(new_drone)
                    else:
                        # Drone not in dronedetails, check in DroneOwnership
                        try:
                            owner = DroneOwnership.objects.get(user=item.owner_id, drone=j['drone_id'])
                            new_drone = {
                                'drone_id': j['drone_id'],
                                'quantity': j['quantity'],
                                'units': j['units'],
                                'price': j['price'],
                                'serial_numbers': j['serial_numbers'],
                                'hsn_number': j['hsn_number'],
                                'discount': j.get('discount', 0),
                                'igst': j.get('igst', 0),
                                'cgst': j.get('cgst', 0),
                                'sgst': j.get('sgst', 0),
                                'updated_datetime': timezone.now().isoformat(),

                            }
                            # Calculate additional fields for the new drone
                            new_drone["item_total_price"] = self.calculate_item_total_price(new_drone["price"],
                                                                                            new_drone["quantity"])
                            new_drone["discount_amount"] = round((new_drone["discount"] / 100) * (
                                new_drone["quantity"]) * (new_drone["price"]), 2)
                            new_drone["price_after_discount"] = round((new_drone["quantity"]) * (
                                new_drone["price"]) - (
                                                                              new_drone["discount"] / 100) * (
                                                                          new_drone["quantity"]) * (
                                                                          new_drone["price"]), 2)
                            new_drone["igst_percentage"] = round((new_drone["igst"] / 100) * (
                                    (new_drone["quantity"]) * (new_drone["price"]) - (
                                    new_drone["discount"] / 100) * (
                                        new_drone["quantity"]) * (new_drone["price"])), 2)
                            new_drone["cgst_percentage"] = round((new_drone["cgst"] / 100) * (
                                    (new_drone["quantity"]) * (new_drone["price"]) - (
                                    new_drone["discount"] / 100) * (
                                        new_drone["quantity"]) * (new_drone["price"])), 2)
                            new_drone["sgst_percentage"] = round((new_drone["sgst"] / 100) * (
                                    (new_drone["quantity"]) * (new_drone["price"]) - (
                                    new_drone["discount"] / 100) * (
                                        new_drone["quantity"]) * (new_drone["price"])), 2)
                            new_drone["total"] = round(((new_drone["quantity"]) * (
                                new_drone["price"]) - (
                                                                new_drone["discount"] / 100) * (
                                                            new_drone["quantity"]) * (
                                                            new_drone["price"])) + new_drone[
                                                           "igst_percentage"] + new_drone["cgst_percentage"] +
                                                       new_drone[
                                                           "sgst_percentage"], 2)

                            # Add new drone to the dronedetails list
                            item.dronedetails.append(new_drone)

                            # Only (q) or fewer quantities allowed for d1
                            if owner.quantity >= j['quantity']:
                                # Subtract new drone quantity from DroneOwnership
                                owner.quantity -= j['quantity']
                                owner.save()

                                # Add new drone quantity to dronedetails
                                add_list.append({
                                    'drone_id': j['drone_id'],
                                    'quantity': j['quantity'],
                                    'units': j['units'],
                                    'price': j['price'],
                                    'serial_numbers': j['serial_numbers'],
                                    'hsn_number': j['hsn_number'],
                                    'discount': j.get('discount', 0),
                                    'igst': j.get('igst', 0),
                                    'cgst': j.get('cgst', 0),
                                    'sgst': j.get('sgst', 0),
                                    'updated_datetime': timezone.now().isoformat(),
                                })
                            else:
                                return Response(
                                    {'message': f"Only {owner.quantity} or fewer quantities allowed for {drone_name}"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        except DroneOwnership.DoesNotExist:
                            return Response(
                                {'message': f"Only {j['quantity']} or fewer quantities allowed for {drone_name}"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                else:
                    # Drone already in dronedetails, update quantity and serial numbers
                    for i in item.dronedetails:
                        serial_numbers = j['serial_numbers']
                        if len(set(serial_numbers)) != len(serial_numbers):
                            return Response({'message': f"Serial numbers must be unique within each drone entry"},
                                            status=status.HTTP_400_BAD_REQUEST)

                        if j["drone_id"] == i["drone_id"]:
                            # Check if the provided serial numbers match the quantity
                            if len(j['serial_numbers']) != j['quantity']:
                                return Response(
                                    {
                                        'message': f"The number of serial numbers must be equal to the quantity for {drone_name}"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                            difference = i["quantity"] - j["quantity"]
                            update_list.append({"drone_id": j["drone_id"], "difference": difference})

                            if item.owner_id.role_id.role_name != 'Super_admin':
                                # Update quantity in DroneOwnership
                                owner = DroneOwnership.objects.get(user=item.owner_id, drone=j["drone_id"])
                                new_quantity = owner.quantity + difference

                                # Check if new quantity is non-negative
                                if new_quantity < 0:
                                    return Response(
                                        {
                                            'message': f"Only {owner.quantity} or fewer quantities allowed for {drone_name}"},
                                        status=status.HTTP_400_BAD_REQUEST
                                    )

                                owner.quantity = new_quantity
                                owner.save()

                            # Update quantity and serial numbers in dronedetails
                            i["quantity"] = j["quantity"]
                            i["serial_numbers"] = j["serial_numbers"]
                            i["item_total_price"] = self.calculate_item_total_price(j["price"], j["quantity"])
                            i["hsn_number"] = j["hsn_number"]
                            i["units"] = j["units"]
                            i["discount"] = j.get('discount', 0)
                            i["igst"] = j.get('igst', 0)
                            i["cgst"] = j.get('cgst', 0)
                            i["sgst"] = j.get('sgst', 0)

                            # Add default values for missing keys
                            i.setdefault("discount_amount", 0)
                            i.setdefault("price_after_discount", 0)
                            i.setdefault("igst_percentage", 0)
                            i.setdefault("cgst_percentage", 0)
                            i.setdefault("sgst_percentage", 0)
                            i.setdefault("total", 0)

                            # Recalculate the additional fields
                            i["discount_amount"] = round((i["discount"] / 100) * (i["quantity"]) * (i["price"]), 2)
                            i["price_after_discount"] = round((i["quantity"]) * (i["price"]) - (
                                    i["discount"] / 100) * (
                                                                  i["quantity"]) * (
                                                                  i["price"]), 2)
                            i["igst_percentage"] = round((i["igst"] / 100) * (
                                    (i["quantity"]) * (i["price"]) - (
                                    i["discount"] / 100) * (
                                        i["quantity"]) * (i["price"])), 2)
                            i["cgst_percentage"] = round((i["cgst"] / 100) * (
                                    (i["quantity"]) * (i["price"]) - (
                                    i["discount"] / 100) * (
                                        i["quantity"]) * (i["price"])), 2)
                            i["sgst_percentage"] = round((i["sgst"] / 100) * (
                                    (i["quantity"]) * (i["price"]) - (
                                    i["discount"] / 100) * (
                                        i["quantity"]) * (i["price"])), 2)
                            i["total"] = round(((i["quantity"]) * (
                                i["price"]) - (
                                                        i["discount"] / 100) * (
                                                    i["quantity"]) * (
                                                    i["price"])) + i["igst_percentage"] + i[
                                                   "cgst_percentage"] + i["sgst_percentage"], 2)

            item.amount_to_pay = round(sum(i.get("total", 0) for i in item.dronedetails), 2)
            item.sum_of_item_total_price = round(sum(Decimal(i.get("item_total_price", 0)) for i in item.dronedetails), 2)
            item.sum_of_igst_percentage = round(sum(float(i.get("igst_percentage", 0)) for i in item.dronedetails), 2)
            item.sum_of_cgst_percentage = round(sum(float(i.get("cgst_percentage", 0)) for i in item.dronedetails), 2)
            item.sum_of_sgst_percentage = round(sum(float(i.get("sgst_percentage", 0)) for i in item.dronedetails), 2)
            item.sum_of_discount_amount = round(sum(float(i.get("discount_amount", 0)) for i in item.dronedetails), 2)
            item.sum_of_price_after_discount = round(
                sum(float(i.get("price_after_discount", 0)) for i in item.dronedetails), 2)
                
            updated_datetime = timezone.now().isoformat()
            for i in item.dronedetails:
                i["updated_datetime"] = [updated_datetime]                

            item.save()
            
            if inventory_partner.role_id.role_name == 'Partner':

                drone_ownerships = DroneOwnership.objects.filter(user= inventory_partner)
                print(drone_ownerships,"aaaaaaaaaaaaaaaaaaaaaa")
                inventory_count = drone_ownerships.aggregate(Sum('quantity'))['quantity__sum']
                print(inventory_count,"innnnnnnnnn")

                inventory_partner.inventory_count = inventory_count
                inventory_partner.save()           

            response_data = {
                'message': 'Items are updated successfully!',
                'item_id': item.id,
                'items_data': new_items
            }
            return Response(response_data, status=status.HTTP_200_OK)


    def delete(self, request, item_id):
        item = get_object_or_404(AddItem, id=item_id)
        data = request.data
        drones_to_delete_param = request.query_params.get('drones_to_delete', '')
        drones_to_delete = [int(drone_id) for drone_id in drones_to_delete_param.split(',') if drone_id]
        user_role = item.owner_id.role_id if item.owner_id else None

        # Fetch the current discount and tax details
        discount = Decimal(item.discount)

        # Fetch the current drone details
        dronedetails = item.dronedetails or []

        # Prepare lists to store updated dronedetails and DroneOwnership instances
        updated_dronedetails = []

        # Calculate the current total price before deletion
        total_price_before_deletion = sum(Decimal(drone['price']) * Decimal(drone['quantity']) for drone in dronedetails)

        # Calculate the discount amount before deletion
        discount_amount_before_deletion = (discount / Decimal(100)) * total_price_before_deletion

        # Calculate the new total price after deletion
        total_price_after_deletion = Decimal(0)

        # Calculate the new discount amount after deletion
        discount_amount_after_deletion = Decimal(0)

        # Check if all drones are being deleted
        if all(drone_id in drones_to_delete for drone_id in
               [drone_detail.get('drone_id') for drone_detail in dronedetails]):
            # If all drones are being deleted, set tax values to zero
            igst_percentage = Decimal(0.0)
            sgst_percentage = Decimal(0.0)
            cgst_percentage = Decimal(0.0)
            utgst_percentage = Decimal(0.0)
        else:
            # If not all drones are being deleted, fetch the current tax details
            igst_percentage = Decimal(item.igst)
            sgst_percentage = Decimal(item.sgst)
            cgst_percentage = Decimal(item.cgst)
            utgst_percentage = Decimal(item.utgst)

        # Iterate through the existing dronedetails
        for drone_detail in dronedetails:
            drone_id = drone_detail.get('drone_id')

            # Check if the drone_id is in the list of drones to be deleted
            if drone_id in drones_to_delete:
                if user_role != "Super_admin":
                    drone_ownership = DroneOwnership.objects.filter(user=item.owner_id, drone=drone_id).first()
                    if drone_ownership:
                        drone_ownership.quantity = F('quantity') + drone_detail['quantity']
                        drone_ownership.save()

                # Skip deleted drones
                continue

            # Add non-deleted drones to the updated_dronedetails list
            updated_dronedetails.append(drone_detail)

            # Update total price and discount amount
            total_price_after_deletion += Decimal(drone_detail['price']) * Decimal(drone_detail['quantity'])

        # Calculate the new discount amount after deletion
        discount_amount_after_deletion = (discount / Decimal(100)) * total_price_after_deletion

        # Update item with new discount and tax details
        item.discount_amount = discount_amount_after_deletion
        item.total_price = total_price_after_deletion

        # Update dronedetails in the item
        item.dronedetails = updated_dronedetails

        # Update additional fields
        item.amount_to_pay = sum(drone.get("total", Decimal(0)) for drone in updated_dronedetails)
        item.sum_of_item_total_price = round(sum(Decimal(drone.get("item_total_price", Decimal(0))) for drone in updated_dronedetails), 2)
        item.sum_of_igst_percentage = round(sum(Decimal(drone.get("igst_percentage", Decimal(0))) for drone in updated_dronedetails), 2)
        item.sum_of_cgst_percentage = round(sum(Decimal(drone.get("cgst_percentage", Decimal(0))) for drone in updated_dronedetails), 2)
        item.sum_of_sgst_percentage = round(sum(Decimal(drone.get("sgst_percentage", Decimal(0))) for drone in updated_dronedetails), 2)
        item.sum_of_discount_amount = round(sum(Decimal(drone.get("discount_amount", Decimal(0))) for drone in updated_dronedetails), 2)

        # Save the changes
        item.save()

        # new code for preventing deletion of the main id when all drones are deleted
        if not updated_dronedetails:
            # If all dronedetails are being deleted, don't delete the main id
            response_data = {
                'message': 'Drones are deleted successfully!',
                'item_id': item.id,
                'dronedetails': updated_dronedetails,
                'discount_amount_after_deletion': discount_amount_after_deletion,
                'total_price_after_deletion': total_price_after_deletion,
                'amount_to_pay': item.amount_to_pay,
                'sum_of_item_total_price': item.sum_of_item_total_price,
                'sum_of_igst_percentage': item.sum_of_igst_percentage,
                'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
                'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
                'sum_of_discount_amount': item.sum_of_discount_amount,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        response_data = {
            'message': 'Drones are deleted successfully!',
            'item_id': item.id,
            'dronedetails': updated_dronedetails,
            'discount_amount_after_deletion': discount_amount_after_deletion,
            'total_price_after_deletion': total_price_after_deletion,
            'amount_to_pay': item.amount_to_pay,
            'sum_of_item_total_price': item.sum_of_item_total_price,
            'sum_of_igst_percentage': item.sum_of_igst_percentage,
            'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
            'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
            'sum_of_discount_amount': item.sum_of_discount_amount,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


from django.db.models import F

class AddDiscountAPI(APIView):
    def post(self, request, item_id):
        item = get_object_or_404(AddItem, id=item_id)
        # discount = request.data.get('discount', 0)
        # igst = request.data.get('igst', 0)
        # sgst = request.data.get('sgst', 0)
        # cgst = request.data.get('cgst', 0)
        # utgst = request.data.get('utgst', 0)
        signature_data = request.data.get('signature')


        drone_details = item.dronedetails

        # total_price = sum(item_data['price'] * item_data['quantity'] for item_data in drone_details)
        # percentage = float(discount) if discount else 0
        # discount_amount = (percentage / 100) * total_price
        #
        # total_price_after_discount = total_price - discount_amount
        #
        # igst_percentage = float(request.data.get('igst', 0))
        # sgst_percentage = float(request.data.get('sgst', 0))
        # cgst_percentage = float(request.data.get('cgst', 0))
        # utgst_percentage = float(request.data.get('utgst', 0))
        #
        # igst_amount = (igst_percentage / 100) * total_price_after_discount
        # sgst_amount = (sgst_percentage / 100) * total_price_after_discount
        # cgst_amount = (cgst_percentage / 100) * total_price_after_discount
        # utgst_amount = (utgst_percentage / 100) * total_price_after_discount
        #
        # total_price_with_additional_percentages = total_price_after_discount + igst_amount + sgst_amount + cgst_amount + utgst_amount
        #
        # item.discount = discount
        # item.igst = igst
        # item.sgst = sgst
        # item.cgst = cgst
        # item.utgst = utgst
        # item.discount_amount = discount_amount
        # item.total_price = total_price
        # item.total_price_after_discount = total_price_after_discount
        # item.total_price_with_additional_percentages = total_price_with_additional_percentages
        # item.igst_amount = igst_amount
        # item.sgst_amount = sgst_amount
        # item.cgst_amount = cgst_amount
        # item.utgst_amount = utgst_amount

        if signature_data:
            if signature_data.startswith(('http:', 'https:')):
                # If the image is provided as a URL, convert it to base64
                #signature_data = base64.b64encode(requests.get(signature_data).content).decode('utf-8')
                media_index = signature_data.find('media/')
                if media_index != -1:
                    signature_data = signature_data[media_index + 6:]  # Length of 'media/' is 6
                    item.signature = signature_data
            else:
                format, imgstr = signature_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'signature_{uuid.uuid4()}.{ext}')
                item.signature.save(data.name, data, save=True)


        try:
            pending_status = InvoiceStatus.objects.get(invoice_status_name='Pending')
        except InvoiceStatus.DoesNotExist:
            # If 'Pending' status does not exist, create it
            pending_status = InvoiceStatus.objects.create(invoice_status_name='Pending')

        item.invoice_status = pending_status

        # Update updated_date_time
        item.updated_date_time = timezone.now()

        item.save()

        response_data = {
            'result': 'Discount is applied successfully!',
            'item_id': item.id,
            # 'total_price_after_discount':total_price_after_discount,
            # 'discount_amount': discount_amount,
            # 'total_price': total_price,
            # "total_price_with_additional_percentages": total_price_with_additional_percentages,
            'signature_url': item.signature.url if item.signature else None

        }
        return Response(response_data, status=status.HTTP_200_OK)
        
    def put(self, request, item_id):
        item = get_object_or_404(AddItem, id=item_id)
        # discount = request.data.get('discount', item.discount)
        # igst = request.data.get('igst', item.igst)
        # sgst = request.data.get('sgst', item.sgst)
        # cgst = request.data.get('cgst', item.cgst)
        # utgst = request.data.get('utgst', item.utgst)
        signature_data = request.data.get('signature')

        drone_details = item.dronedetails

        # total_price = sum(item_data['price'] * item_data['quantity'] for item_data in drone_details)
        # percentage = float(discount) if discount else 0
        # discount_amount = (percentage / 100) * total_price
        # 
        # total_price_after_discount = total_price - discount_amount
        # 
        # igst_percentage = float(request.data.get('igst', 0))
        # sgst_percentage = float(request.data.get('sgst', 0))
        # cgst_percentage = float(request.data.get('cgst', 0))
        # utgst_percentage = float(request.data.get('utgst', 0))
        # 
        # igst_amount = (igst_percentage / 100) * total_price_after_discount
        # sgst_amount = (sgst_percentage / 100) * total_price_after_discount
        # cgst_amount = (cgst_percentage / 100) * total_price_after_discount
        # utgst_amount = (utgst_percentage / 100) * total_price_after_discount
        # 
        # total_price_with_additional_percentages = (
        #         total_price_after_discount + igst_amount + sgst_amount + cgst_amount + utgst_amount
        # )
        # 
        # item.discount = discount
        # item.igst = igst
        # item.sgst = sgst
        # item.cgst = cgst
        # item.utgst = utgst
        # item.discount_amount = discount_amount
        # item.total_price = total_price
        # item.total_price_after_discount = total_price_after_discount
        # item.total_price_with_additional_percentages = total_price_with_additional_percentages
        # item.igst_amount = igst_amount
        # item.sgst_amount = sgst_amount
        # item.cgst_amount = cgst_amount
        # item.utgst_amount = utgst_amount

        if signature_data:
            if signature_data.startswith(('http:', 'https:')):
                # If the image is provided as a URL, convert it to base64
                #signature_data = base64.b64encode(requests.get(signature_data).content).decode('utf-8')
                media_index = signature_data.find('media/')
                if media_index != -1:
                    signature_data = signature_data[media_index + 6:]  # Length of 'media/' is 6
                    item.signature = signature_data
            else:
                format, imgstr = signature_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'signature_{uuid.uuid4()}.{ext}')
                item.signature.save(data.name, data, save=True)
        item.updated_date_time = timezone.now()

        item.save()

        response_data = {
            'result': 'Discount is updated successfully!',
            'item_id': item.id,
            # 'total_price_after_discount': total_price_after_discount,
            # 'discount_amount': discount_amount,
            # 'total_price': total_price,
            # "total_price_with_additional_percentages": total_price_with_additional_percentages
        }
        return Response(response_data, status=status.HTTP_200_OK)
        
import requests
from geopy.geocoders import Nominatim

class CustomerCreateOrginizationAPIView(APIView):
    def get_state_code(self, state_name):
        # Define a dictionary mapping state names to their codes
        state_code_mapping = {
            "Andaman and Nicobar Islands": "35",
            "Andhra Pradesh": "28",
            "Arunachal Pradesh": "12",
            "Assam": "18",
            "Bihar": "10",
            "Chandigarh": "04",
            "Chhattisgarh": "22",
            "Dadra and Nagar Haveli and Daman and Diu": "26",
            "Delhi": "07",
            "Goa": "30",
            "Gujarat": "24",
            "Haryana": "06",
            "Himachal Pradesh": "02",
            "Jharkhand": "20",
            "Karnataka": "29",
            "Kerala": "32",
            "Lakshadweep": "31",
            "Madhya Pradesh": "23",
            "Maharashtra": "27",
            "Manipur": "14",
            "Meghalaya": "17",
            "Mizoram": "15",
            "Nagaland": "13",
            "Odisha": "21",
            "Puducherry": "34",
            "Punjab": "03",
            "Rajasthan": "08",
            "Sikkim": "11",
            "Tamil Nadu": "33",
            "Telangana": "36",
            "Tripura": "16",
            "Uttar Pradesh": "09",
            "Uttarakhand": "05",
            "West Bengal": "19",
            "Jammu and Kashmir": "01",
            "Ladakh": "02",
        }

        # Retrieve the state code from the dictionary
        return state_code_mapping.get(state_name, '')

    def get_location_details(self, pin_code):
        geolocator = Nominatim(user_agent="amxcrm")
        location = geolocator.geocode(pin_code)

        if location:
            raw_data = location.raw
            print(raw_data, "Raw Data")

            display_name = raw_data.get('display_name', '')
            print(display_name, "Display Name")

            # Extracting information from display_name
            parts = display_name.split(', ')
            state = parts[-2]
            city = parts[-3]
            country = parts[-1]

            # Retrieve state code using the predefined mapping
            state_code = self.get_state_code(state)
            print(state_code, "State Code")

            return {
                'state': state,
                'state_code': state_code,
                'city': city,
                'country': country
            }

        return None
    def post(self, request, *args, **kwargs):
        data = request.data

        email = data.get('email')
        mobile_number = data.get('phone')
        created_by_id = data.get('created_by')

        if CustomUser.objects.filter(created_by__id=created_by_id, email=email).exists():
            return Response({"message": "Customer with the provided email already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(created_by__id=created_by_id, mobile_number=mobile_number).exists():
            return Response({"message": "Customer with the provided mobile number already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        gst = data.get('gst')
        pan = data.get('pan')
        cin = data.get('cin')
        shipping_address = data.get('shipping_address')
        billing_address = data.get('billing_address')
        shipping_pincode = data.get('shipping_pincode')
        billing_pincode = data.get('billing_pincode')
        created_by_id = data.get('created_by')
        category_id = data.get('category_id')
        invoice = data.get('invoice_id')
        role_id = data.get('role_id')
        state_name = data.get('state_name')
        state_code = data.get('state_code')
        pin_code = data.get('pin_code')
        company_name = data.get('company_name')
        gstin_reg_type = data.get('gstin_reg_type')

        if created_by_id is None or invoice is None or role_id is None:
            return Response({"message": "created_by_id, invoice_id, and role_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            created_by = CustomUser.objects.get(id=created_by_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with ID {} does not exist.".format(created_by_id)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = InvoiceType.objects.get(id=invoice)
        except InvoiceType.DoesNotExist:
            return Response({"message": "InvoiceType with ID {} does not exist.".format(invoice)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            role_id = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"message": "Role with ID {} does not exist.".format(role_id)},
                            status=status.HTTP_400_BAD_REQUEST)

        new_user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=phone,
            company_gst_num=gst,
            gst_number=gst,
            pan_number=pan,
            company_cin_num=cin,
            shipping_address=shipping_address,
            billing_address=billing_address,
            category_id=category_id,
            created_by=created_by,
            invoice=invoice,
            role_id=role_id,
            state_name=state_name,
            state_code=state_code,
            shipping_pincode=shipping_pincode,
            billing_pincode=billing_pincode,
            pin_code=pin_code,
            company_name=company_name,
            gstin_reg_type= gstin_reg_type,
        )

        shipping_location_details = self.get_location_details(shipping_pincode)
        billing_location_details = self.get_location_details(billing_pincode)

        if shipping_location_details:
            new_user.shipping_state = shipping_location_details.get('state')
            new_user.shipping_state_code = shipping_location_details.get('state_code')
            new_user.shipping_state_city = shipping_location_details.get('city')
            new_user.shipping_state_country = shipping_location_details.get('country')

        if billing_location_details:
            new_user.billing_state = billing_location_details.get('state')
            new_user.billing_state_code = billing_location_details.get('state_code')
            new_user.billing_state_city = billing_location_details.get('city')
            new_user.billing_state_country = billing_location_details.get('country')

        try:
            new_user.save()
            return Response({"message": "Customer created successfully", "customer_id": new_user.id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        if customer_id is None:
            return Response({"message": "Customer ID is required for updating"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        email = data.get('email')
        mobile_number = data.get('phone')
        created_by_id = data.get('created_by')

        if CustomUser.objects.filter(created_by__id=created_by_id, email=email).exclude(id=customer_id).exists():
            return Response({"message": "Customer with the provided email already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(created_by__id=created_by_id, mobile_number=mobile_number).exclude(
                id=customer_id).exists():
            return Response({"message": "Customer with the provided mobile number already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = CustomUser.objects.get(id=customer_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Customer with ID {} does not exist.".format(customer_id)},
                            status=status.HTTP_404_NOT_FOUND)

        #if customer.role_id.role_name != 'Customer':
            #return Response({"message": "You do not have permission to update this customer."},
                            #status=status.HTTP_403_FORBIDDEN)
        if customer.category.name != 'Organization':
            return Response({"message": "You can update only Orginization here"},
                            status=status.HTTP_403_FORBIDDEN)

        if customer.created_by_id != data.get('created_by'):
            return Response({"message": "You do not have permission to update this customer."},
                            status=status.HTTP_403_FORBIDDEN)

        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.email = data.get('email', customer.email)
        customer.mobile_number = data.get('phone', customer.mobile_number)
        customer.company_gst_num = data.get('gst', customer.company_gst_num)
        customer.pan_number = data.get('pan', customer.pan_number)
        customer.company_cin_num = data.get('cin', customer.company_cin_num)
        customer.shipping_address = data.get('shipping_address', customer.shipping_address)
        customer.billing_address = data.get('billing_address', customer.billing_address)
        # customer.category_id = data.get('category_id', customer.category_id)
        customer.state_name = data.get('state_name', customer.state_name)
        customer.state_code = data.get('state_code', customer.state_code)
        customer.shipping_pincode = data.get('shipping_pincode', customer.shipping_pincode)
        customer.billing_pincode = data.get('billing_pincode', customer.billing_pincode)
        customer.pin_code = data.get('pin_code', customer.pin_code)
        customer.company_name = data.get('company_name',customer.company_name)
        customer.gstin_reg_type = data.get('gstin_reg_type',customer.gstin_reg_type)
        customer.gst_number = data.get('gst',customer.gst_number)        

        shipping_location_details = self.get_location_details(customer.shipping_pincode)
        if shipping_location_details:
            customer.shipping_state = shipping_location_details['state']
            customer.shipping_state_code = shipping_location_details['state_code']
            customer.shipping_state_city = shipping_location_details['city']
            customer.shipping_state_country = shipping_location_details['country']

        # Fetch and update billing location details
        billing_location_details = self.get_location_details(customer.billing_pincode)
        if billing_location_details:
            customer.billing_state = billing_location_details['state']
            customer.billing_state_code = billing_location_details['state_code']
            customer.billing_state_city = billing_location_details['city']
            customer.billing_state_country = billing_location_details['country']

        try:
            customer.save()
            return Response({"message": "Customer updated successfully", "customer_id": customer.id},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        if customer_id is None:
            return Response({"message": "Customer ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = CustomUser.objects.get(id=customer_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Customer with ID {} does not exist.".format(customer_id)},
                            status=status.HTTP_404_NOT_FOUND)

        if customer.role_id.role_name != 'Customer':
            return Response({"message": "You do not have permission to delete this customer."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            customer.delete()
            return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CustomerCreateIndividualAPIView(APIView):

    def get_state_code(self, state_name):
        # Define a dictionary mapping state names to their codes
        state_code_mapping = {
            "Andaman and Nicobar Islands": "35",
            "Andhra Pradesh": "28",
            "Arunachal Pradesh": "12",
            "Assam": "18",
            "Bihar": "10",
            "Chandigarh": "04",
            "Chhattisgarh": "22",
            "Dadra and Nagar Haveli and Daman and Diu": "26",
            "Delhi": "07",
            "Goa": "30",
            "Gujarat": "24",
            "Haryana": "06",
            "Himachal Pradesh": "02",
            "Jharkhand": "20",
            "Karnataka": "29",
            "Kerala": "32",
            "Lakshadweep": "31",
            "Madhya Pradesh": "23",
            "Maharashtra": "27",
            "Manipur": "14",
            "Meghalaya": "17",
            "Mizoram": "15",
            "Nagaland": "13",
            "Odisha": "21",
            "Puducherry": "34",
            "Punjab": "03",
            "Rajasthan": "08",
            "Sikkim": "11",
            "Tamil Nadu": "33",
            "Telangana": "36",
            "Tripura": "16",
            "Uttar Pradesh": "09",
            "Uttarakhand": "05",
            "West Bengal": "19",
            "Jammu and Kashmir": "01",
            "Ladakh": "02",
        }

        # Retrieve the state code from the dictionary
        return state_code_mapping.get(state_name, '')

    def get_location_details(self, pin_code):
        geolocator = Nominatim(user_agent="amxcrm")
        location = geolocator.geocode(pin_code)

        if location:
            raw_data = location.raw
            print(raw_data, "Raw Data")

            display_name = raw_data.get('display_name', '')
            print(display_name, "Display Name")

            # Extracting information from display_name
            parts = display_name.split(', ')
            state = parts[-2]
            city = parts[-3]
            country = parts[-1]

            # Retrieve state code using the predefined mapping
            state_code = self.get_state_code(state)
            print(state_code, "State Code")

            return {
                'state': state,
                'state_code': state_code,
                'city': city,
                'country': country
            }

        return None


    def post(self, request, *args, **kwargs):
        data = request.data

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        mobile_number = data.get('phone')
        date_of_birth = data.get('date_of_birth')
        shipping_address = data.get('shipping_address')
        shipping_pincode = data.get('shipping_pincode')
        billing_pincode = data.get('billing_pincode')
        created_by_id = data.get('created_by')
        category_id = data.get('category_id')
        invoice_id = data.get('invoice_id')
        role_id = data.get('role_id')
        gender = data.get('gender')
        state_name = data.get('state_name')
        state_code = data.get('state_code')
        billing_address = data.get('billing_address')
        pin_code = data.get('pin_code')
        pan_number = data.get('pan_number')

        if created_by_id is None:
            return Response({"message": "created_by is required"}, status=status.HTTP_400_BAD_REQUEST)

        if role_id is None:
            return Response({"message": "role_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            created_by = CustomUser.objects.get(id=created_by_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with ID {} does not exist.".format(created_by_id)},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the given email already has the same customer
        if CustomUser.objects.filter(created_by__id=created_by_id, email=email).exists():
            return Response({"message": "Customer with the provided email already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the given mobile number already has the same customer
        if CustomUser.objects.filter(created_by__id=created_by_id, mobile_number=mobile_number).exists():
            return Response({"message": "Customer with the provided mobile number already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the Role instance
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"message": "Role with ID {} does not exist.".format(role_id)},
                            status=status.HTTP_400_BAD_REQUEST)


        new_user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            date_of_birth=date_of_birth,
            shipping_address=shipping_address,
            category_id=category_id,
            created_by=created_by,
            invoice_id=invoice_id,
            role_id=role,
            gender=gender,
            state_name=state_name,
            state_code=state_code,
            billing_address=billing_address,
            shipping_pincode=shipping_pincode,
            billing_pincode=billing_pincode,
            pin_code=pin_code,
            pan_number=pan_number

        )
        shipping_location_details = self.get_location_details(shipping_pincode)
        billing_location_details = self.get_location_details(billing_pincode)

        if shipping_location_details:
            new_user.shipping_state = shipping_location_details.get('state')
            new_user.shipping_state_code = shipping_location_details.get('state_code')
            new_user.shipping_state_city = shipping_location_details.get('city')
            new_user.shipping_state_country = shipping_location_details.get('country')

        if billing_location_details:
            new_user.billing_state = billing_location_details.get('state')
            new_user.billing_state_code = billing_location_details.get('state_code')
            new_user.billing_state_city = billing_location_details.get('city')
            new_user.billing_state_country = billing_location_details.get('country')

        try:
            new_user.save()
            return Response({"message": "Customer created successfully", "customer_id": new_user.id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        if customer_id is None:
            return Response({"message": "Customer ID is required for updating"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        try:
            customer = CustomUser.objects.get(id=customer_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Customer with ID {} does not exist.".format(customer_id)},
                            status=status.HTTP_404_NOT_FOUND)

        #if customer.role_id.role_name != 'Customer':
            #return Response({"message": "You do not have permission to update this customer."},
                            #status=status.HTTP_403_FORBIDDEN)

        if customer.category.name != 'Individual':
            return Response({"message": "You can update only Individual here"},
                            status=status.HTTP_403_FORBIDDEN)

        if customer.created_by_id != data.get('created_by'):
            return Response({"message": "You do not have permission to update this customer."},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if a user with the given email already has the same customer
        if CustomUser.objects.filter(created_by__id=customer.created_by_id, email=data.get('email')).exclude(
                id=customer.id).exists():
            return Response({"message": "Customer with the provided email already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a user with the given mobile number already has the same customer
        if CustomUser.objects.filter(created_by__id=customer.created_by_id, mobile_number=data.get('phone')).exclude(
                id=customer.id).exists():
            return Response({"message": "Customer with the provided mobile number already exists for this user"},
                            status=status.HTTP_400_BAD_REQUEST)

        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.email = data.get('email', customer.email)
        customer.mobile_number = data.get('phone', customer.mobile_number)
        customer.date_of_birth = data.get('date_of_birth', customer.date_of_birth)
        customer.shipping_address = data.get('shipping_address', customer.shipping_address)
        # customer.category_id = data.get('category_id', customer.category_id)
        customer.gender = data.get('gender', customer.gender)
        customer.state_name = data.get('state_name', customer.state_name)
        customer.state_code = data.get('state_code', customer.state_code)
        customer.billing_address = data.get('billing_address', customer.billing_address)
        customer.shipping_pincode = data.get('shipping_pincode', customer.shipping_pincode)
        customer.billing_pincode = data.get('billing_pincode', customer.billing_pincode)
        customer.pin_code = data.get('pin_code', customer.pin_code)
        customer.pan_number = data.get('pan_number',customer.pan_number)

        shipping_location_details = self.get_location_details(customer.shipping_pincode)
        if shipping_location_details:
            customer.shipping_state = shipping_location_details['state']
            customer.shipping_state_code = shipping_location_details['state_code']
            customer.shipping_state_city = shipping_location_details['city']
            customer.shipping_state_country = shipping_location_details['country']

        # Fetch and update billing location details
        billing_location_details = self.get_location_details(customer.billing_pincode)
        if billing_location_details:
            customer.billing_state = billing_location_details['state']
            customer.billing_state_code = billing_location_details['state_code']
            customer.billing_state_city = billing_location_details['city']
            customer.billing_state_country = billing_location_details['country']

        try:
            customer.save()
            return Response({"message": "Customer updated successfully", "customer_id": customer.id},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        if customer_id is None:
            return Response({"message": "Customer ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = CustomUser.objects.get(id=customer_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Customer with ID {} does not exist.".format(customer_id)},
                            status=status.HTTP_404_NOT_FOUND)
        if customer.role_id.role_name != 'Customer':
            return Response({"message": "You do not have permission to delete this customer."},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            customer.delete()
            return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CustomInvoice, CustomerCategory, CustomUser, InvoiceType

from django.shortcuts import get_object_or_404

class CustomInvoiceTypeAPI(APIView):
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')

        if id is not None:
            custom_invoice = get_object_or_404(CustomInvoice, id=id)
            data = self.get_invoice_details(custom_invoice)
            return Response(data)
        else:
            custom_invoices = CustomInvoice.objects.all()
            custom_invoices_data = [self.get_invoice_details(invoice) for invoice in custom_invoices]
            return Response({'Result': custom_invoices_data})

    def get_invoice_details(self, custom_invoice):
        customer_details = {
            'id': custom_invoice.customer_id.id,
            'username': custom_invoice.customer_id.username,
            'email': custom_invoice.customer_id.email,
            'mobile_number': custom_invoice.customer_id.mobile_number,
            'address': custom_invoice.customer_id.address,
            'pin_code': custom_invoice.customer_id.pin_code,
            'pan_number': custom_invoice.customer_id.pan_number,
            'profile_pic': custom_invoice.customer_id.profile_pic.url if custom_invoice.customer_id.profile_pic else None,
            'company_name': custom_invoice.customer_id.company_name,
            'company_email': custom_invoice.customer_id.company_email,
            'company_address': custom_invoice.customer_id.company_address,
            'shipping_address': custom_invoice.customer_id.shipping_address,
            'billing_address': custom_invoice.customer_id.billing_address,
            'company_phn_number': custom_invoice.customer_id.company_phn_number,
            'company_gst_num': custom_invoice.customer_id.company_gst_num,
            'company_cin_num': custom_invoice.customer_id.company_cin_num,
            'company_logo': custom_invoice.customer_id.company_logo.url if custom_invoice.customer_id.company_logo else None,
            'role_id': custom_invoice.customer_id.role_id.id,
            'created_date_time': custom_invoice.customer_id.created_date_time,
            'updated_date_time': custom_invoice.customer_id.updated_date_time,
            'status': custom_invoice.customer_id.status,
            'location': custom_invoice.customer_id.location,
            'reason': custom_invoice.customer_id.reason,
            'partner_initial_update': custom_invoice.customer_id.partner_initial_update,
            'gst_number': custom_invoice.customer_id.gst_number,
            'category': custom_invoice.customer_id.category.id if custom_invoice.customer_id.category else None,
            'date_of_birth': custom_invoice.customer_id.date_of_birth,
            'gender': custom_invoice.customer_id.gender,
            'created_by': custom_invoice.customer_id.created_by.id if custom_invoice.customer_id.created_by else None,
            'invoice': custom_invoice.customer_id.invoice.id if custom_invoice.customer_id.invoice else None,
        }

        owner_details = {
            'id': custom_invoice.owner_id.id,
            'username': custom_invoice.owner_id.username,
            'email': custom_invoice.owner_id.email,
            'mobile_number': custom_invoice.owner_id.mobile_number,
            'address': custom_invoice.owner_id.address,
            'pin_code': custom_invoice.owner_id.pin_code,
            'pan_number': custom_invoice.owner_id.pan_number,
            'profile_pic': custom_invoice.owner_id.profile_pic.url if custom_invoice.owner_id.profile_pic else None,
            'company_name': custom_invoice.owner_id.company_name,
            'company_email': custom_invoice.owner_id.company_email,
            'company_address': custom_invoice.owner_id.company_address,
            'shipping_address': custom_invoice.owner_id.shipping_address,
            'billing_address': custom_invoice.owner_id.billing_address,
            'company_phn_number': custom_invoice.owner_id.company_phn_number,
            'company_gst_num': custom_invoice.owner_id.company_gst_num,
            'company_cin_num': custom_invoice.owner_id.company_cin_num,
            'company_logo': custom_invoice.owner_id.company_logo.url if custom_invoice.owner_id.company_logo else None,
            'role_id': custom_invoice.owner_id.role_id.id,
            'created_date_time': custom_invoice.owner_id.created_date_time,
            'updated_date_time': custom_invoice.owner_id.updated_date_time,
            'status': custom_invoice.owner_id.status,
            'location': custom_invoice.owner_id.location,
            'reason': custom_invoice.owner_id.reason,
            'partner_initial_update': custom_invoice.owner_id.partner_initial_update,
            'gst_number': custom_invoice.owner_id.gst_number,
            'category': custom_invoice.owner_id.category.id if custom_invoice.owner_id.category else None,
            'date_of_birth': custom_invoice.owner_id.date_of_birth,
            'gender': custom_invoice.owner_id.gender,
            'created_by': custom_invoice.owner_id.created_by.id if custom_invoice.owner_id.created_by else None,
            'invoice': custom_invoice.owner_id.invoice.id if custom_invoice.owner_id.invoice else None,
        }

        invoice_type_details = {
            'id': custom_invoice.invoice_type_id.id,
            'name': custom_invoice.invoice_type_id.invoice_type_name,
            'created_date_time': custom_invoice.invoice_type_id.created_date_time,
            'updated_date_time': custom_invoice.invoice_type_id.updated_date_time,
        }

        customer_type_details = {
            'id': custom_invoice.customer_type_id.id,
            'name': custom_invoice.customer_type_id.name,
            'created_date_time': custom_invoice.customer_type_id.created_date_time,
            'updated_date_time': custom_invoice.customer_type_id.updated_date_time,
        }

        data = {
            'id': custom_invoice.id,
            'item_name': custom_invoice.item_name,
            'price': custom_invoice.price,
            'quantity': custom_invoice.quantity,
            'hsn_number': custom_invoice.hsn_number,
            'customer_type_id': custom_invoice.customer_type_id.id,
            'owner_id': custom_invoice.owner_id.id,
            'customer_id': custom_invoice.customer_id.id,
            'invoice_type_id': custom_invoice.invoice_type_id.id,
            'customer_details': customer_details,
            'owner_details': owner_details,
            'invoice_type_details': invoice_type_details,
            'customer_type_details': customer_type_details,
        }

        return data

    def post(self, request):
        data = request.data
        item_name = data.get('item_name')
        price = data.get('price')
        quantity = data.get('quantity')
        customer_type_id = data.get('customer_type_id')
        owner_id = data.get('owner_id')
        invoice_type_id = data.get('invoice_type_id')
        hsn_number = data.get('hsn_number')
        customer_id = data.get('customer_id')

        # Fix the following lines, use correct model for each instance
        customer_type_instance = get_object_or_404(CustomerCategory, id=customer_type_id)
        owner_id_instance = get_object_or_404(CustomUser, id=owner_id)
        invoice_type_instance = get_object_or_404(InvoiceType, id=invoice_type_id)
        customuser_id_instance = get_object_or_404(CustomUser, id=customer_id)

        if CustomInvoice.objects.filter(item_name=item_name).exists():
            return Response({'message': 'item_name is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_custom_invoice = CustomInvoice.objects.create(
                item_name=item_name,
                price=price,
                quantity=quantity,
                customer_type_id=customer_type_instance,
                owner_id=owner_id_instance,
                invoice_type_id=invoice_type_instance,
                hsn_number=hsn_number,
                customer_id=customuser_id_instance
            )
            return Response({'result': 'CustomInvoice is created successfully!'}, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #         data = request.data
    #         items = data.get('items', [])
    #         owner_id = data.get('owner_id')
    #         customer_type_id = data.get('customer_type_id')
    #         customer_id = data.get('customer_id')
    #         invoice_type_id = data.get('invoice_type_id')
    #         partner_instance = get_object_or_404(CustomUser, id=owner_id)
    #         all_serialnumbers = []

    #         dronedetails_lists = CustomInvoice.objects.values_list('custom_item_details', flat=True)

    #         for dronedetails_list in dronedetails_lists:
    #             if dronedetails_list:
    #                 serial_numbers = [serial_number for entry in dronedetails_list for serial_number in
    #                                 entry.get('serial_numbers', [])]
    #                 all_serialnumbers.extend(serial_numbers)

    #         items_data = []
    #         custom_item_details = []
    #         total_price = Decimal('0.00')
    #         total_price_with_additional_percentages = Decimal('0.00')
    #         all_serial_numbers = set()

    #         is_super_admin = partner_instance.role_id.role_name == 'Super_admin'

    #         with transaction.atomic():
    #             entered_serial_numbers = []
    #             for item_data in items:
    #                 drone_id = item_data.get('drone_id')
    #                 quantity = item_data.get('quantity')
    #                 discount = item_data.get('discount')[0] if isinstance(item_data.get('discount'), tuple) else item_data.get('discount')
    #                 igst = item_data.get('igst')[0] if isinstance(item_data.get('igst'), tuple) else item_data.get('igst')
    #                 cgst = item_data.get('cgst')[0] if isinstance(item_data.get('cgst'), tuple) else item_data.get('cgst')
    #                 sgst = item_data.get('sgst')[0] if isinstance(item_data.get('sgst'), tuple) else item_data.get('sgst')
    #                 item_total_price=(quantity) * (item_data.get('price'))
    #                 discount_amount = (discount / 100) * item_total_price
    #                 user_id = get_object_or_404(CustomUser, id=customer_id)

    #                 serial_numbers = item_data.get('serial_numbers', [])
    #                 entered_serial_numbers.extend(serial_numbers)

    #                 if quantity != len(serial_numbers):
    #                     return Response(
    #                         {'message': f"Quantity and the number of serial numbers must be equal in each drone entry"},
    #                         status=status.HTTP_400_BAD_REQUEST)

    #                 if len(set(serial_numbers)) != len(serial_numbers):
    #                     return Response({'message': f"Serial numbers must be unique within each drone entry"},
    #                                     status=status.HTTP_400_BAD_REQUEST)

    #                 if any(serial_number in all_serial_numbers for serial_number in serial_numbers):
    #                     return Response({'message': f"Serial numbers must be unique across all drone entries"},
    #                                     status=status.HTTP_400_BAD_REQUEST)

    #                 all_serial_numbers.update(serial_numbers)
    #                 item_total_price = (quantity) * (item_data.get('price'))

    #                 custom_item_details.append({
    #                     'drone_id': drone_id,
    #                     'quantity': quantity,
    #                     'price': item_data.get('price'),
    #                     'serial_numbers': serial_numbers,
    #                     'hsn_number': item_data.get('hsn_number'),
    #                     'item_total_price': item_total_price,
    #                     'discount':discount,
    #                     'igst':igst,
    #                     'cgst':cgst,
    #                     'sgst':sgst,
    #                     'discount_amount': discount_amount,
    #                     'price_after_discount':item_total_price-discount_amount,
    #                     'igst_percentage':(igst / 100) * (item_total_price - discount_amount),
    #                     'cgst_percentage': (cgst / 100) * (item_total_price - discount_amount),
    #                     'sgst_percentage': (sgst / 100) * (item_total_price - discount_amount),
    #                     'total': (item_total_price - discount_amount) +
    #         (igst / 100) * (item_total_price - discount_amount) +
    #         (cgst / 100) * (item_total_price - discount_amount) +
    #         (sgst / 100) * (item_total_price - discount_amount)

    #                 })



    #                 items_data.append({
    #                     'drone_id': drone_id,
    #                     'price': item_data.get('price'),
    #                     'serial_numbers': serial_numbers,
    #                     'hsn_number': item_data.get('hsn_number'),
    #                     'item_total_price': item_total_price,
    #                     'discount': discount,
    #                     'igst': igst,
    #                     'cgst': cgst,
    #                     'sgst': sgst,
    #                     'discount_amount':discount_amount,
    #                     'price_after_discount': item_total_price - discount_amount,
    #                     'igst_percentage':(igst / 100) * (item_total_price-discount_amount),
    #                     'cgst_percentage': (cgst / 100) * (item_total_price - discount_amount),
    #                     'sgst_percentage': (sgst / 100) * (item_total_price - discount_amount),
    #                     'total': (item_total_price - discount_amount) +
    #         (igst / 100) * (item_total_price - discount_amount) +
    #         (cgst / 100) * (item_total_price - discount_amount) +
    #         (sgst / 100) * (item_total_price - discount_amount)


    #                 })

    #                 total_price += Decimal(item_data.get('price')) * quantity
    #                 total_price_with_additional_percentages += Decimal(item_data.get('price')) * quantity
    #             print(entered_serial_numbers, "sssssssssssssssssbbbbbbbbbbbbbbbbbb")
    #             duplicate_serial_numbers = []
    #             for entered_serial in entered_serial_numbers:
    #                 if entered_serial in all_serialnumbers:
    #                     duplicate_serial_numbers.append(entered_serial)

    #             if duplicate_serial_numbers:
    #                 return Response({
    #                     'message': f"Serial numbers {', '.join(map(str, duplicate_serial_numbers))} already exist in the table"},
    #                     status=status.HTTP_400_BAD_REQUEST)

    #             if len(custom_item_details) == 0:
    #                 return Response({'message': 'custom_item_details cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

    #             for item_data in items:
    #                 drone_id = item_data.get('drone_id')
    #                 quantity = item_data.get('quantity')
    #                 user_id = get_object_or_404(CustomUser, id=customer_id)

    #                 # Skip quantity checks for Super_admin
    #                 if not is_super_admin:
    #                     # Check if the drone exists in DroneOwnership
    #                     drone_ownership = DroneOwnership.objects.filter(user=owner_id, drone=drone_id).first()
    #                     if not drone_ownership or drone_ownership.quantity < quantity:
    #                         return Response({'message': f"Not enough quantity available for drone_id {drone_id}"},
    #                                         status=status.HTTP_400_BAD_REQUEST)

    #                     # Subtract the quantity from DroneOwnership
    #                     drone_ownership.quantity = F('quantity') - quantity
    #                     drone_ownership.save()

    #                     # Check if the drone's quantity is now zero and prevent adding the item
    #                     if drone_ownership.quantity == 0:
    #                         return Response({'message': f"Drone_id {drone_id} is out of stock"},
    #                                         status=status.HTTP_400_BAD_REQUEST)

    #             else:
    #                 try:
    #                     draft_status = InvoiceStatus.objects.get(invoice_status_name='Inprogress')
    #                 except InvoiceStatus.DoesNotExist:
    #                     # If 'Draft' status does not exist, create it
    #                     draft_status = InvoiceStatus.objects.create(invoice_status_name='Inprogress')
    #                 new_item = CustomInvoice.objects.create(
    #                     customer_type_id=get_object_or_404(CustomerCategory, id=customer_type_id),
    #                     customer_id=get_object_or_404(CustomUser, id=customer_id),
    #                     owner_id=partner_instance,
    #                     invoice_type_id=get_object_or_404(InvoiceType, id=invoice_type_id),
    #                     invoice_status=draft_status,
    #                 )

    #                 new_item.invoice_number = self.create_invoice_number()
    #                 new_item.save()

    #                 # If dronedetails is empty, return a response without creating the item
    #                 new_item.dronedetails = dronedetails
    #                 new_item.total_price = total_price
    #                 new_item.total_price_with_additional_percentages = total_price_with_additional_percentages
    #                 amount_to_pay = sum(item['total'] for item in dronedetails)
    #                 sum_of_item_total_price = sum(item['item_total_price'] for item in dronedetails)
    #                 sum_of_igst_percentage = sum(item['igst_percentage'] for item in dronedetails)
    #                 sum_of_cgst_percentage = sum(item['cgst_percentage'] for item in dronedetails)
    #                 sum_of_sgst_percentage = sum(item['sgst_percentage'] for item in dronedetails)
    #                 sum_of_discount_amount = sum(item['discount_amount'] for item in dronedetails)
    #                 new_item.amount_to_pay = amount_to_pay
    #                 new_item.sum_of_item_total_price = sum_of_item_total_price
    #                 new_item.sum_of_igst_percentage = sum_of_igst_percentage
    #                 new_item.sum_of_cgst_percentage = sum_of_cgst_percentage
    #                 new_item.sum_of_sgst_percentage = sum_of_sgst_percentage
    #                 new_item.sum_of_discount_amount = sum_of_discount_amount
    #                 new_item.save()
    #                 # total_amount = sum(item['total'] for item in dronedetails)
    #                 response_data = {
    #                     'message': 'Items are created successfully!',
    #                     'item_id': new_item.id,
    #                     'items_data': [
    #                         {
    #                             'drone_id': item_data['drone_id'],
    #                             'price': item_data['price'],
    #                             'serial_numbers': item_data['serial_numbers'],
    #                             'hsn_number': item_data['hsn_number'],
    #                             'item_total_price': (quantity) * (item_data.get('price')),
    #                             'discount': item_data.get('discount'),
    #                             'igst': item_data.get('igst'),
    #                             'cgst': item_data.get('cgst'),
    #                             'sgst': item_data.get('sgst'),
    #                             'remaining_quantity': None if is_super_admin else DroneOwnership.objects.filter(
    #                                 user=owner_id, drone=item_data['drone_id']
    #                             ).first().quantity
    #                         } for item_data in items_data
    #                     ],
    #                     'Amount_to_pay':amount_to_pay,
    #                     "sum_of_item_total_price":sum_of_item_total_price,
    #                     "sum_of_igst_percentage": sum_of_igst_percentage,
    #                     "sum_of_cgst_percentage": sum_of_cgst_percentage,
    #                     "sum_of_sgst_percentage": sum_of_sgst_percentage,
    #                     "sum_of_discount_amount":sum_of_discount_amount

    #                 }
    #                 return Response(response_data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        data = request.data
        item_name = data.get('item_name')
        price = data.get('price')
        quantity = data.get('quantity')
        customer_type_id = data.get('customer_type_id')
        owner_id = data.get('owner_id')
        invoice_type_id = data.get('invoice_type_id')
        hsn_number = data.get('hsn_number')
        customer_id = data.get('customer_id')

        custom_invoice = get_object_or_404(CustomInvoice, pk=pk)

        # Check if the new item_name already exists for a different CustomInvoice
        if item_name != custom_invoice.item_name and CustomInvoice.objects.filter(item_name=item_name).exists():
            return Response({'message': 'Item name is already in use by another CustomInvoice'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the fields with the new data
        custom_invoice.item_name = item_name
        custom_invoice.hsn_number = hsn_number
        custom_invoice.price = price
        custom_invoice.quantity = quantity
        custom_invoice.customer_type_id = get_object_or_404(CustomerCategory, id=customer_type_id)
        custom_invoice.owner_id = get_object_or_404(CustomUser, id=owner_id)
        custom_invoice.invoice_type_id = get_object_or_404(InvoiceType, id=invoice_type_id)
        custom_invoice.customer_id = get_object_or_404(CustomUser, id=customer_id)
        custom_invoice.save()

        return Response({'result': 'CustomInvoice is updated successfully!'}, status=status.HTTP_200_OK)

    def delete(self,request,pk):
        data=request.data
        

        if CustomInvoice.objects.filter(id=pk).exists():
            data=CustomInvoice.objects.filter(id=pk).delete()
            return Response({'message':'CustomInvoice deleted!!'})
        else:
            return Response({'result':'CustomInvoice id not found!!'})

from django.db.models import Sum

class MydronespartnerAPI(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"message": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        if user.role_id.role_name == 'Partner':
            drone_ownership = DroneOwnership.objects.filter(user=user)
            serialized_data = [{
                'drone_id': ownership.drone.id,
                'drone_name': ownership.drone.drone_name,
                'total_quantity': ownership.quantity,
                'details': {
                    'drone_category': ownership.drone.drone_category.category_name,
                    'market_price': ownership.drone.market_price,
                    'our_price': ownership.drone.our_price,
                    'hsn_number': ownership.drone.hsn_number,
                    'units':ownership.drone.units.units if ownership.drone.units else None,
                    'igstvalue': ownership.drone.igstvalue,
                    'sgstvalue': ownership.drone.sgstvalue,
                    'cgstvalue': ownership.drone.cgstvalue,
                    'drone_specification': ownership.drone.drone_specification,
                    'sales_status': ownership.drone.sales_status,
                    'created_date_time': ownership.drone.created_date_time,
                    'updated_date_time': ownership.drone.updated_date_time,
                    'quantity_available': ownership.drone.quantity_available,
                    'thumbnail_image': ownership.drone.thumbnail_image.url if ownership.drone.thumbnail_image else None,
                    'drone_sub_images': ownership.drone.drone_sub_images,
                }
            } for ownership in drone_ownership if ownership.quantity > 0]
        elif user.role_id.role_name == 'Super_admin':
            drones = Drone.objects.all()
            serialized_data = [{
                'drone_id': drone.id,
                'drone_name': drone.drone_name,
                'total_quantity': 1,  # Total quantity is not applicable for Super_admin
                'details': {
                    'drone_category': drone.drone_category.category_name,
                    'market_price': drone.market_price,
                    'our_price': drone.our_price,
                    'units':drone.units.units if drone.units else None,
                    'hsn_number': drone.hsn_number,
                    'igstvalue': drone.igstvalue,
                    'sgstvalue': drone.sgstvalue,
                    'cgstvalue': drone.cgstvalue,
                    'drone_specification': drone.drone_specification,
                    'sales_status': drone.sales_status,
                    'created_date_time': drone.created_date_time,
                    'updated_date_time': drone.updated_date_time,
                    'quantity_available': drone.quantity_available,
                    'thumbnail_image': drone.thumbnail_image.url if drone.thumbnail_image else None,
                    'drone_sub_images': drone.drone_sub_images,
                }
            } for drone in drones]
        else:
            return Response({"message": "Invalid role for this API"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'result': {
                'status': 'GET ALL',
                'data': serialized_data,
            },
        })

class GetItemDetailsAPI(APIView):
    def get(self, request, user_id):
        items = AddItem.objects.filter(customer_id=user_id, status=False)

        if not items.exists():
            return Response({"message": "No items found for the provided criteria"}, status=status.HTTP_404_NOT_FOUND)

        total_price = sum(float(item.price) * int(item.quantity) for item in items)

        percentage_value = request.data.get('discount', 0)
        percentage = float(percentage_value) if percentage_value else 0

        discount_amount = (percentage / 100) * total_price

        total_price_after_discount = total_price - discount_amount

        partner_details = {}
        partner_id = items.first().partner_id_id
        if partner_id:
            partner = get_object_or_404(CustomUser, id=partner_id)
            partner_details = {
                'partner_id': partner.id,
                'partner_name': partner.get_full_name(),
                'partner_email': partner.email,
                'partner_mobile_number': partner.mobile_number,
                'partner_address': partner.address,
                'partner_pin_code': partner.pin_code,
                'partner_pan_number': partner.pan_number,
                'partner_profile_pic': partner.profile_pic.url if partner.profile_pic else None,
                'partner_company_name': partner.company_name,
                'partner_company_email': partner.company_email,
                'partner_company_address': partner.company_address,
                'partner_shipping_address': partner.shipping_address,
                'partner_billing_address': partner.billing_address,
                'partner_company_phn_number': partner.company_phn_number,
                'partner_company_gst_num': partner.company_gst_num,
                'partner_company_cin_num': partner.company_cin_num,
                'partner_company_logo': partner.company_logo.url if partner.company_logo else None,
                'partner_role_id': partner.role_id.id,
                'partner_created_date_time': partner.created_date_time,
                'partner_updated_date_time': partner.updated_date_time,
                'partner_status': partner.status,
                'partner_location': partner.location,
                'partner_reason': partner.reason,
                'partner_partner_initial_update': partner.partner_initial_update,
                'partner_gst_number': partner.gst_number,
                'partner_inventory_count': partner.inventory_count,
                'partner_category_id': partner.category.id if partner.category else None,
                'partner_date_of_birth': partner.date_of_birth,
                'partner_gender': partner.gender,
                'partner_created_by_id': partner.created_by.id if partner.created_by else None,
                'partner_invoice_id': partner.invoice.id if partner.invoice else None,
            }

        # Get customer details if available
        customer_details = {}
        customer_id = items.first().customer_id_id
        if customer_id:
            customer = get_object_or_404(CustomUser, id=customer_id)
            customer_details = {
                'customer_id': customer.id,
                'customer_name': customer.get_full_name(),
                'customer_email': customer.email,
                'customer_mobile_number': customer.mobile_number,
                'customer_address': customer.address,
                'customer_pin_code': customer.pin_code,
                'customer_pan_number': customer.pan_number,
                'customer_profile_pic': customer.profile_pic.url if customer.profile_pic else None,
                'customer_company_name': customer.company_name,
                'customer_company_email': customer.company_email,
                'customer_company_address': customer.company_address,
                'customer_shipping_address': customer.shipping_address,
                'customer_billing_address': customer.billing_address,
                'customer_company_phn_number': customer.company_phn_number,
                'customer_company_gst_num': customer.company_gst_num,
                'customer_company_cin_num': customer.company_cin_num,
                'customer_company_logo': customer.company_logo.url if customer.company_logo else None,
                'customer_role_id': customer.role_id.id,
                'customer_created_date_time': customer.created_date_time,
                'customer_updated_date_time': customer.updated_date_time,
                'customer_status': customer.status,
                'customer_location': customer.location,
                'customer_reason': customer.reason,
                'customer_partner_initial_update': customer.partner_initial_update,
                'customer_gst_number': customer.gst_number,
                'customer_category_id': customer.category.id if customer.category else None,
                'customer_date_of_birth': customer.date_of_birth,
                'customer_gender': customer.gender,
                'customer_created_by_id': customer.created_by.id if customer.created_by else None,
                'customer_invoice_id': customer.invoice.id if customer.invoice else None,
            }

        # Get details of each item
        items_details = []
        for item in items:
            item_details = {
                'item_id': item.id,
                'drone_id': item.drone_id.id,
                'drone_name': item.drone_id.drone_name,
                'drone_category': item.drone_id.drone_category.category_name,
                'price': item.price,
                'quantity': item.quantity,
                'customer_type_id': item.customer_type_id.id,
                'customer_type_name': item.customer_type_id.name,
                'invoice_type_id': item.invoice_type_id.id,
                'invoice_type_name': item.invoice_type_id.invoice_type_name,
                'serial_numbers': json.loads(item.serial_number),
                # Add other item details as needed
            }
            items_details.append(item_details)

        response_data = {
            'total_price': total_price,
            'discount_percentage': percentage,
            'discount_amount': discount_amount,
            'total_price_after_discount': total_price_after_discount,
            'partner_details': partner_details,
            'customer_details': customer_details,
            'items_details': items_details,
        }

        return Response(response_data, status=status.HTTP_200_OK)

class SuperAdminGetAllView(APIView):
    def get(self, request, super_admin_id):
        try:
            # Retrieve the Super Admin user
            super_admin = CustomUser.objects.get(id=super_admin_id)

            # Retrieve all users (partners and customers) created by the Super Admin
            users = CustomUser.objects.filter(created_by=super_admin)

            user_data = [
                {
                    'id': user.id,
                    'profile_pic_url': user.profile_pic.url if user.profile_pic else None,
                    'invoice_name': user.invoice.invoice_type_name if user.invoice else None,
                    'category_name': user.category.name if user.category else None,
                    'full_name': user.get_full_name(),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'email_altr': user.email_altr,
                    'username': user.username,
                    'mobile_number': user.mobile_number,
                    'address': user.address,
                    'pin_code': user.pin_code,
                    'pan_number': user.pan_number,
                    'profile_pic': user.profile_pic.url if user.profile_pic else None,
                    'company_name': user.company_name,
                    'company_address': user.company_address,
                    'shipping_address': user.shipping_address,
                    'shipping_pincode':user.shipping_pincode,
                    'billing_pincode':user.billing_pincode,
                    'billing_address': user.billing_address,
                    'company_phn_number': user.company_phn_number,
                    'company_gst_num': user.company_gst_num,
                    'company_cin_num': user.company_cin_num,
                    'company_logo': user.company_logo.url if user.company_logo else None,
                    'created_date_time': user.created_date_time,
                    'updated_date_time': user.updated_date_time,
                    'status': user.status,
                    'company_email': user.company_email,
                    'location': user.location,
                    'reason': user.reason,
                    'partner_initial_update': user.partner_initial_update,
                    'gst_number': user.gst_number,
                    'inventory_count': user.inventory_count,
                    'date_of_birth': user.date_of_birth,
                    'gender': user.gender,
                    'role_id': user.role_id.id if user.role_id else None,
                    'category': user.category.id if user.category else None,
                    'created_by': user.created_by.id if user.created_by else None,
                    'invoice': user.invoice.id if user.invoice else None,
                }
                for user in users
            ]

            return Response(user_data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "Super Admin user not found"}, status=status.HTTP_404_NOT_FOUND)

class GetItemsByOwnerIdView(View):
    def get(self, request, owner_id):
        try:
            owner = CustomUser.objects.get(id=owner_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({"message": "Owner not found"}, status=404)

        if owner.role_id.role_name == 'Super_admin':
            items = AddItem.objects.filter(owner_id=owner)
        elif owner.role_id.role_name == 'Partner':
            items = AddItem.objects.filter(owner_id=owner)
        else:
            items = AddItem.objects.filter(owner_id=owner)

        items = items.exclude(invoice_status__invoice_status_name="Completed")

        item_list = []
        for item in items:
            owner_data = {
                "id": owner.id,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "full_name": owner.get_full_name(),
                "email": owner.email,
                "mobile_number": owner.mobile_number,
                "address": owner.address,
                "pin_code": owner.pin_code,
                "pan_number": owner.pan_number,
                # "profile_pic": str(owner.profile_pic) if owner.profile_pic else None,
                "profile_pic": f"/media/{owner.profile_pic}" if owner.profile_pic else None,
                "company_name": owner.company_name,
                "company_email": owner.company_email,
                "company_address": owner.company_address,
                "shipping_address": owner.shipping_address,
                "billing_address": owner.billing_address,
                "company_phn_number": owner.company_phn_number,
                "company_gst_num": owner.company_gst_num,
                "company_cin_num": owner.company_cin_num,
                # "company_logo": str(owner.company_logo) if owner.company_logo else None,
                "role_id": owner.role_id.id if owner.role_id else None,
                "location": owner.location,
                "reason": owner.reason,
                "partner_initial_update": owner.partner_initial_update,
                "gst_number": owner.gst_number,
                "inventory_count": owner.inventory_count,
                "category_id": owner.category.id if owner.category else None,
                "date_of_birth": owner.date_of_birth,
                "gender": owner.gender,
                "created_by_id": owner.created_by_id,
                "company_logo": f"/media/{owner.company_logo}" if owner.company_logo else None,
                # "invoice_id": owner.invoice_id.id if owner.invoice_id else None,
                "state_name": owner.state_name,
                "state_code": owner.state_code,
                "shipping_pincode": owner.shipping_pincode,
                "billing_pincode": owner.billing_pincode,
                "shipping_state": owner.shipping_state,
                "shipping_state_code": owner.shipping_state_code,
                "shipping_state_city": owner.shipping_state_city,
                "shipping_state_country": owner.shipping_state_country,
                "billing_state": owner.billing_state,
                "billing_state_code": owner.billing_state_code,
                "billing_state_city": owner.billing_state_city,
                "billing_state_country": owner.billing_state_country,
                "gstin_reg_type":owner.gstin_reg_type,
            }

            customer_data = {
                "id": item.customer_id.id if item.customer_id else None,
                "first_name": item.customer_id.first_name if item.customer_id else None,
                "last_name": item.customer_id.last_name if item.customer_id else None,
                "full_name": item.customer_id.get_full_name() if item.customer_id else None,
                "email": item.customer_id.email if item.customer_id else None,
                "mobile_number": item.customer_id.mobile_number if item.customer_id else None,
                "address": item.customer_id.address if item.customer_id else None,
                "pin_code": item.customer_id.pin_code if item.customer_id else None,
                "pan_number": item.customer_id.pan_number if item.customer_id else None,
                # "profile_pic": str(
                #     item.customer_id.profile_pic) if item.customer_id and item.customer_id.profile_pic else None,
                'profile_pic': f"/media/{item.customer_id.profile_pic}" if item.customer_id and item.customer_id.profile_pic else None,
                "company_name": item.customer_id.company_name if item.customer_id else None,
                "company_email": item.customer_id.company_email if item.customer_id else None,
                "company_address": item.customer_id.company_address if item.customer_id else None,
                "shipping_address": item.customer_id.shipping_address if item.customer_id else None,
                "billing_address": item.customer_id.billing_address if item.customer_id else None,
                "company_phn_number": item.customer_id.company_phn_number if item.customer_id else None,
                "company_gst_num": item.customer_id.company_gst_num if item.customer_id else None,
                "company_cin_num": item.customer_id.company_cin_num if item.customer_id else None,
                'company_logo': f"/media/{item.customer_id.company_logo}" if item.customer_id and item.customer_id.company_logo else None,
                # "company_logo": str(
                #     item.customer_id.company_logo) if item.customer_id and item.customer_id.company_logo else None,
                "role_id": item.customer_id.role_id.id if item.customer_id and item.customer_id.role_id else None,
                "created_date_time": item.customer_id.created_date_time if item.customer_id else None,
                "updated_date_time": item.customer_id.updated_date_time if item.customer_id else None,
                "status": item.customer_id.status if item.customer_id else None,
                "location": item.customer_id.location if item.customer_id else None,
                "reason": item.customer_id.reason if item.customer_id else None,
                "partner_initial_update": item.customer_id.partner_initial_update if item.customer_id else None,
                "gst_number": item.customer_id.gst_number if item.customer_id else None,
                "inventory_count": item.customer_id.inventory_count if item.customer_id else None,
                "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                "date_of_birth": item.customer_id.date_of_birth if item.customer_id else None,
                "gender": item.customer_id.gender if item.customer_id else None,
                "created_by_id": item.customer_id.created_by_id if item.customer_id else None,
                # "invoice_id": item.customer_id.invoice_id.id if item.customer_id and item.customer_id.invoice_id else None,
                # "state_name": item.customer_id.state_name if item.customer_id else None,
                # "state_code": item.customer_id.state_code if item.customer_id else None,
                "shipping_pincode": item.customer_id.shipping_pincode if item.customer_id else None,
                "billing_pincode": item.customer_id.billing_pincode if item.customer_id else None,
                "shipping_state": item.customer_id.shipping_state if item.customer_id else None,
                "shipping_state_code": item.customer_id.shipping_state_code if item.customer_id else None,
                "shipping_state_city": item.customer_id.shipping_state_city if item.customer_id else None,
                "shipping_state_country": item.customer_id.shipping_state_country if item.customer_id else None,
                "billing_state": item.customer_id.billing_state if item.customer_id else None,
                "billing_state_code": item.customer_id.billing_state_code if item.customer_id else None,
                "billing_state_city": item.customer_id.billing_state_city if item.customer_id else None,
                "billing_state_country": item.customer_id.billing_state_country if item.customer_id else None,
                "gstin_reg_type":item.customer_id.gstin_reg_type if item.customer_id else None,
            }
            invoice_type_details = {
                'id': item.invoice_type_id.id if item.invoice_type_id else None,
                'name': item.invoice_type_id.invoice_type_name if item.invoice_type_id else None,
            }

            customer_category = {
                "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
            }

            drone_details = item.dronedetails
            drone_info_list = []

            if drone_details:
                for drone_detail in drone_details:
                    drone_id = drone_detail["drone_id"]
                    quantity = drone_detail["quantity"]
                    price = drone_detail["price"]
                    serial_numbers = drone_detail.get("serial_numbers", [])
                    hsn_number = drone_detail["hsn_number"]
                    item_total_price = drone_detail.get("item_total_price", 0)
                    discount = drone_detail.get("discount", 0)
                    igst = drone_detail.get("igst", 0)
                    cgst = drone_detail.get("cgst", 0)
                    sgst = drone_detail.get("sgst", 0)
                    created_datetime = drone_detail.get("created_datetime")
                    updated_datetime = drone_detail.get("updated_datetime")
                    discount_amount = drone_detail.get("discount_amount")
                    price_after_discount = drone_detail.get("price_after_discount")
                    igst_percentage = drone_detail.get("igst_percentage", 0)
                    cgst_percentage = drone_detail.get("cgst_percentage", 0)
                    sgst_percentage = drone_detail.get("sgst_percentage", 0)
                    total = drone_detail.get("total", 0)

                    try:
                        drone = Drone.objects.get(id=drone_id)
                        drone_ownership = DroneOwnership.objects.filter(user=owner, drone=drone_id).first()
                        remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                        drone_info = {
                            "drone_id": drone.id,
                            "drone_name": drone.drone_name,
                            "drone_category": drone.drone_category.category_name if drone.drone_category else None,
                            "quantity": quantity,
                            "price": price,
                            "serial_numbers": serial_numbers,
                            "hsn_number": hsn_number,
                            "item_total_price": item_total_price,
                            "remaining_quantity": remaining_quantity,
                            "discount": discount,
                            "igst": igst,
                            "cgst": cgst,
                            "sgst": sgst,
                            "created_datetime": created_datetime,
                            "updated_datetime": updated_datetime,
                            "discount_amount": discount_amount,
                            "price_after_discount": price_after_discount,
                            "igst_percentage": igst_percentage,
                            "cgst_percentage": cgst_percentage,
                            "sgst_percentage": sgst_percentage,
                            "total": total
                        }
                        drone_info_list.append(drone_info)
                    except Drone.DoesNotExist:
                        pass

            item_data = {
                "id": item.id,
                "customer_type_id": item.customer_type_id.id if item.customer_type_id else None,
                "customer_details": customer_data,
                "owner_id": item.owner_id.id if item.owner_id else None,
                "owner_details": owner_data,
                'invoice_type_details': invoice_type_details,
                'customer_category': customer_category,
                "dronedetails": drone_info_list,
                "e_invoice_status": item.e_invoice_status,
                "invoice_number": item.invoice_number,
                "created_date_time": item.created_date_time,
                "updated_date_time": item.updated_date_time,
                "signature_url": item.signature.url if item.signature else None,
                "invoice_status": item.invoice_status.invoice_status_name if item.invoice_status else None,
                "invoice_status_id": item.invoice_status.id if item.invoice_status else None,

            }
            item_list.append(item_data)
        item_list.sort(key=lambda x: x['updated_date_time'], reverse=True)
        return JsonResponse({"items": item_list}, status=200)


class PartnerAddedItems(APIView):
    def get(self, request):
        partners = CustomUser.objects.filter(role_id__role_name='Partner')
        item_list = []

        for partner in partners:
            items = AddItem.objects.filter(owner_id=partner)

            for item in items:
                owner_data = {
                    "id": partner.id,
                    "first_name": partner.first_name,
                    "last_name": partner.last_name,
                    "full_name": partner.get_full_name(),
                    "email": partner.email,
                    "mobile_number": partner.mobile_number,
                    "address": partner.address,
                    "pin_code": partner.pin_code,
                    "pan_number": partner.pan_number,
                    # "profile_pic": str(partner.profile_pic) if partner.profile_pic else None,
                    "profile_pic": f"/media/{partner.profile_pic}" if partner.profile_pic else None,
                    "company_name": partner.company_name,
                    "company_email": partner.company_email,
                    "company_address": partner.company_address,
                    "shipping_address": partner.shipping_address,
                    "billing_address": partner.billing_address,
                    "company_phn_number": partner.company_phn_number,
                    "company_gst_num": partner.company_gst_num,
                    "company_cin_num": partner.company_cin_num,
                    # "company_logo": str(partner.company_logo) if partner.company_logo else None,
                    "company_logo": f"/media/{partner.company_logo}" if partner.company_logo else None,
                    "role_id": partner.role_id.id if partner.role_id else None,
                    "location": partner.location,
                    "reason": partner.reason,
                    "partner_initial_update": partner.partner_initial_update,
                    "gst_number": partner.gst_number,
                    "inventory_count": partner.inventory_count,
                    "category_id": partner.category.id if partner.category else None,
                    "date_of_birth": partner.date_of_birth,
                    "gender": partner.gender,
                    "created_by_id": partner.created_by_id,
                    # "invoice_id": partner.invoice_id.id if partner.invoice_id else None,
                    "state_name": partner.state_name,
                    "state_code": partner.state_code,
                    "shipping_pincode": partner.shipping_pincode,
                    "billing_pincode": partner.billing_pincode,
                    "state_name": partner.state_name,
                    "state_code": partner.state_code,
                    "gstin_reg_type":partner.gstin_reg_type,
                }

                customer_data = {
                    "id": item.customer_id.id if item.customer_id else None,
                    "first_name": item.customer_id.first_name if item.customer_id else None,
                    "last_name": item.customer_id.last_name if item.customer_id else None,
                    "full_name": item.customer_id.get_full_name() if item.customer_id else None,
                    "email": item.customer_id.email if item.customer_id else None,
                    "mobile_number": item.customer_id.mobile_number if item.customer_id else None,
                    "address": item.customer_id.address if item.customer_id else None,
                    "pin_code": item.customer_id.pin_code if item.customer_id else None,
                    "pan_number": item.customer_id.pan_number if item.customer_id else None,
                    'profile_pic': f"/media/{item.customer_id.profile_pic}" if item.customer_id and item.customer_id.profile_pic else None,
                    # "profile_pic": str(
                    #     item.customer_id.profile_pic) if item.customer_id and item.customer_id.profile_pic else None,
                    "company_name": item.customer_id.company_name if item.customer_id else None,
                    "company_email": item.customer_id.company_email if item.customer_id else None,
                    "company_address": item.customer_id.company_address if item.customer_id else None,
                    "shipping_address": item.customer_id.shipping_address if item.customer_id else None,
                    "billing_address": item.customer_id.billing_address if item.customer_id else None,
                    "company_phn_number": item.customer_id.company_phn_number if item.customer_id else None,
                    "company_gst_num": item.customer_id.company_gst_num if item.customer_id else None,
                    "company_cin_num": item.customer_id.company_cin_num if item.customer_id else None,
                    'company_logo': f"/media/{item.customer_id.company_logo}" if item.customer_id and item.customer_id.company_logo else None,
                    # "company_logo": str(
                    #     item.customer_id.company_logo) if item.customer_id and item.customer_id.company_logo else None,
                    "role_id": item.customer_id.role_id.id if item.customer_id and item.customer_id.role_id else None,
                    "created_date_time": item.customer_id.created_date_time if item.customer_id else None,
                    "updated_date_time": item.customer_id.updated_date_time if item.customer_id else None,
                    "status": item.customer_id.status if item.customer_id else None,
                    "location": item.customer_id.location if item.customer_id else None,
                    "reason": item.customer_id.reason if item.customer_id else None,
                    "partner_initial_update": item.customer_id.partner_initial_update if item.customer_id else None,
                    "gst_number": item.customer_id.gst_number if item.customer_id else None,
                    "inventory_count": item.customer_id.inventory_count if item.customer_id else None,
                    "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                    "date_of_birth": item.customer_id.date_of_birth if item.customer_id else None,
                    "gender": item.customer_id.gender if item.customer_id else None,
                    "created_by_id": item.customer_id.created_by_id if item.customer_id else None,
                    # "invoice_id": item.customer_id.invoice_id.id if item.customer_id and item.customer_id.invoice_id else None,
                    "state_name": item.customer_id.state_name if item.customer_id else None,
                    "state_code": item.customer_id.state_code if item.customer_id else None,
                    "shipping_pincode": item.customer_id.shipping_pincode if item.customer_id else None,
                    "billing_pincode": item.customer_id.billing_pincode if item.customer_id else None,
                    "state_name": item.customer_id.state_name if item.customer_id else None,
                    "state_code": item.customer_id.state_code if item.customer_id else None,
                    "gstin_reg_type":item.customer_id.gstin_reg_type if item.customer_id else None,

                }
                invoice_type_details = {
                    'id': item.invoice_type_id.id if item.invoice_type_id else None,
                    'name': item.invoice_type_id.invoice_type_name if item.invoice_type_id else None,
                }

                customer_category = {
                    "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                    "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
                }

                drone_details = item.dronedetails
                drone_info_list = []

                if drone_details:
                    for drone_detail in drone_details:
                        drone_id = drone_detail["drone_id"]
                        quantity = drone_detail["quantity"]
                        price = drone_detail["price"]
                        serial_numbers = drone_detail.get("serial_numbers", [])
                        hsn_number = drone_detail["hsn_number"]
                        item_total_price = drone_detail.get("item_total_price", 0)
                        discount = drone_detail.get("discount", 0)
                        igst = drone_detail.get("igst", 0)
                        cgst = drone_detail.get("cgst", 0)
                        sgst = drone_detail.get("sgst", 0)
                        created_datetime = drone_detail.get("created_datetime")
                        updated_datetime = drone_detail.get("updated_datetime")
                        discount_amount = drone_detail.get("discount_amount")
                        price_after_discount = drone_detail.get("price_after_discount")
                        igst_percentage = drone_detail.get("igst_percentage", 0)
                        cgst_percentage = drone_detail.get("cgst_percentage", 0)
                        sgst_percentage = drone_detail.get("sgst_percentage", 0)
                        total = drone_detail.get("total", 0)

                        try:
                            drone = Drone.objects.get(id=drone_id)
                            drone_ownership = DroneOwnership.objects.filter(user=partner, drone=drone_id).first()
                            remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                            drone_info = {
                                "drone_id": drone.id,
                                "drone_name": drone.drone_name,
                                "drone_category": drone.drone_category.category_name if drone.drone_category else None,
                                "quantity": quantity,
                                "price": price,
                                "serial_numbers": serial_numbers,
                                "hsn_number": hsn_number,
                                "item_total_price": item_total_price,
                                "remaining_quantity": remaining_quantity,
                                "discount": discount,
                                "igst": igst,
                                "cgst": cgst,
                                "sgst": sgst,
                                "created_datetime": created_datetime,
                                "updated_datetime": updated_datetime,
                                "discount_amount": discount_amount,
                                "price_after_discount": price_after_discount,
                                "igst_percentage": igst_percentage,
                                "cgst_percentage": cgst_percentage,
                                "sgst_percentage": sgst_percentage,
                                "total": total
                            }
                            drone_info_list.append(drone_info)
                        except Drone.DoesNotExist:
                            pass

                item_data = {
                    "id": item.id,
                    "customer_type_id": item.customer_type_id.id if item.customer_type_id else None,
                    "customer_details": customer_data,
                    "owner_id": partner.id if partner else None,
                    "owner_details": owner_data,
                    'invoice_type_details': invoice_type_details,
                    'customer_category': customer_category,
                    "dronedetails": drone_info_list,
                    "e_invoice_status": item.e_invoice_status,
                    "invoice_number": item.invoice_number,
                    "created_date_time": item.created_date_time,
                    "updated_date_time": item.updated_date_time,
                    "signature_url": item.signature.url if item.signature else None,
                    "invoice_status": item.invoice_status.invoice_status_name if item.invoice_status else None,

                }
                item_list.append(item_data)

        return Response({"items": item_list}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pycountry

class StateCodeAPI(APIView):
    def get(self, request, *args, **kwargs):
        # List of states with their codes
        states_data = [
            {"name": "Andaman and Nicobar Islands", "code": "35"},
            {"name": "Andhra Pradesh", "code": "28"},
            {"name": "Arunachal Pradesh", "code": "12"},
            {"name": "Assam", "code": "18"},
            {"name": "Bihar", "code": "10"},
            {"name": "Chandigarh", "code": "04"},
            {"name": "Chhattisgarh", "code": "22"},
            {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "26"},
            {"name": "Delhi", "code": "07"},
            {"name": "Goa", "code": "30"},
            {"name": "Gujarat", "code": "24"},
            {"name": "Haryana", "code": "06"},
            {"name": "Himachal Pradesh", "code": "02"},
            {"name": "Jharkhand", "code": "20"},
            {"name": "Karnataka", "code": "29"},
            {"name": "Kerala", "code": "32"},
            {"name": "Lakshadweep", "code": "31"},
            {"name": "Madhya Pradesh", "code": "23"},
            {"name": "Maharashtra", "code": "27"},
            {"name": "Manipur", "code": "14"},
            {"name": "Meghalaya", "code": "17"},
            {"name": "Mizoram", "code": "15"},
            {"name": "Nagaland", "code": "13"},
            {"name": "Odisha", "code": "21"},
            {"name": "Puducherry", "code": "34"},
            {"name": "Punjab", "code": "03"},
            {"name": "Rajasthan", "code": "08"},
            {"name": "Sikkim", "code": "11"},
            {"name": "Tamil Nadu", "code": "33"},
            {"name": "Telangana", "code": "36"},
            {"name": "Tripura", "code": "16"},
            {"name": "Uttar Pradesh", "code": "09"},
            {"name": "Uttarakhand", "code": "05"},
            {"name": "West Bengal", "code": "19"},
            {"name": "Jammu and Kashmir", "code": "01"},
            {"name": "Ladakh", "code": "02"},
        ]

        # Return the state data in the response
        return Response({'state_data': states_data}, status=status.HTTP_200_OK)

class InvoiceStatusAPI(APIView):
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        pk = kwargs.get('pk')  # Retrieve pk from URL parameters

        if id is not None:
            status = InvoiceStatus.objects.filter(id=id).first()
            if status:
                data = {'id': status.id, 'invoice_status_name': status.invoice_status_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Invoice type not found for the specified id'}, status=404)
        elif pk is not None:
            status = InvoiceStatus.objects.filter(id=pk).first()  # Use pk instead of id
            if status:
                data = {'id': status.id, 'invoice_status_name': status.invoice_status_name,'created_date_time':status.created_date_time,'updated_date_time':status.updated_date_time}
                return Response(data)
            else:
                return Response({'message': 'Invoice type not found for the specified id'}, status=404)
        else:
            data = InvoiceStatus.objects.all().values()
            return Response({'Result':data})


    def post(self, request):
        data = request.data
        invoice_status_name = data.get('invoice_status_name')

        if InvoiceStatus.objects.filter(invoice_status_name=invoice_status_name).exists():
            return Response({'message': 'Invoice status name is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_status = InvoiceStatus.objects.create(invoice_status_name=invoice_status_name)
            return Response({'result': 'Invoice status name is created successfully!'}, status=status.HTTP_201_CREATED)

    # def put(self,request,pk):
    #     data=request.data
    #     invoice_status_name=data.get('invoice_status_name')

    #     if InvoiceStatus.objects.filter(id=pk).exists():
    #         data=InvoiceStatus.objects.filter(id=pk).update(invoice_status_name=invoice_status_name)
    #         return Response({'message':'Invoice status name Updated!!'})
    #     else:
    #         return Response({'message':'invoice status name id not found!!'})

    def put(self, request, pk):
        data = request.data
        invoice_status_name = data.get('invoice_status_name')

        try:
            status_instance = InvoiceStatus.objects.get(id=pk)

            if InvoiceStatus.objects.filter(invoice_status_name=invoice_status_name).exclude(id=pk).exists():
                return Response({'message': 'DroneCategory name already exists. Choose a different name.'},
                                status=status.HTTP_400_BAD_REQUEST)

            status_instance.invoice_status_name = invoice_status_name
            status_instance.updated_date_time = datetime.now()
            status_instance.save()

            return Response({'message': 'Invoice status name  Updated!!'})
        except InvoiceStatus.DoesNotExist:
            return Response({'message': 'Invoice status name  id not found!!'}, status=status.HTTP_404_NOT_FOUND)


    def delete(self,request,pk):
        data=request.data
        invoice_status_name=data.get('invoice_status_name')

        if InvoiceStatus.objects.filter(id=pk).exists():
            data=InvoiceStatus.objects.filter(id=pk).delete()
            return Response({'message':'Invoice status name deleted!!'})
        else:
            return Response({'result':'Invoice status name id not found!!'})




from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
import base64
import json
import os
from .models import AuthToken  # Import your AuthToken model



# class MyApiView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Extract JSON data from the request
#         try:
#             json_data = JSONParser().parse(request)
#         except json.JSONDecodeError:
#             return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve sek from the AuthToken model (assuming you have only one entry)
#         try:
#             auth_token_entry = AuthToken.objects.first()
#             sek = auth_token_entry.sek
#         except AuthToken.DoesNotExist:
#             return Response({"error": "AuthToken entry not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Use sek as the encryption key (base64-decoded)
#         key = base64.b64decode(sek)

#         # Encrypt the data
#         encrypted_data = self.encrypt_data(json_data, key, sek)

#         # Return the encrypted data along with sek
#         return Response({"encrypted_data": encrypted_data, "sek": sek}, status=status.HTTP_200_OK)

    # def encrypt_data(self, data, key, sek):
    #     # Serialize the data to JSON
    #     json_data = json.dumps(data)

    #     # Generate a random initialization vector (IV)
    #     iv = os.urandom(algorithms.AES.block_size // 8)

    #     # Use sek as the encryption key (base64-decoded)
    #     sek_key = base64.b64decode(sek)

    #     # Create an AES cipher object with the IV and sek_key
    #     cipher = Cipher(algorithms.AES(sek_key), modes.CBC(iv), backend=default_backend())

    #     # Pad the data using PKCS7
    #     padder = PKCS7(algorithms.AES.block_size).padder()
    #     padded_data = padder.update(json_data.encode('utf-8')) + padder.finalize()

    #     # Encrypt the data
    #     encryptor = cipher.encryptor()
    #     encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    #     # Combine IV and encrypted data, then encode the result in base64
    #     combined_data = iv + encrypted_data
    #     encrypted_base64 = base64.b64encode(combined_data).decode('utf-8')

    #     return encrypted_base64

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from Crypto.Util.Padding import unpad
import json
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from collections import OrderedDict




class MyApiView(APIView):
    def clean_payload(self, payload):
        cleaned_payload = ''.join(char for char in payload if char.isprintable())
        return cleaned_payload

    def encrypt(self, payload, sek_key):
        cleaned_payload = self.clean_payload(json.dumps(payload, separators=(',', ':')))
        decoded_sek_key = base64.b64decode(sek_key)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_payload = padder.update(cleaned_payload.encode())
        padded_payload += padder.finalize()
        cipher = Cipher(algorithms.AES(decoded_sek_key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_payload) + encryptor.finalize()
        encrypted_text = base64.b64encode(encrypted_data).decode()
        print(f"Encrypted Data: {encrypted_text}")

        # Clean up the encrypted payload using json.dumps
        cleaned_encrypted_payload = json.dumps(encrypted_text).strip('"')
        print(f"Cleaned Encrypted Data: {cleaned_encrypted_payload}")

        return cleaned_encrypted_payload

    def get(self, request, *args, **kwargs):
        invoice_number = request.query_params.get('invoice_number')
        invoice_type = request.query_params.get('invoice_type')

        if not invoice_number:
            return Response({"error": "Missing invoice_number in the request body."},
                            status=status.HTTP_400_BAD_REQUEST)

        if invoice_type == 'Drone':
            item = get_object_or_404(AddItem.objects.select_related('invoice_type_id'),
                                     invoice_number=invoice_number,
                                     invoice_type_id__invoice_type_name=invoice_type)
            if item:
                try:
                    auth_token = AuthToken.objects.first()

                    if auth_token:
                        sek_key = auth_token.sek

                        owner_details = CustomUser.objects.filter(id=item.owner_id.id).values(
                            'company_gst_num', 'company_name', 'billing_address', 'billing_state_city',
                            'billing_pincode', 'billing_state_code'
                        ).first()
                        print(owner_details, "ownerrrrrrrrrrrrrrrrrrrrrrrrrrrrr")

                        buyer_details = CustomUser.objects.filter(id=item.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location','company_gst_num',
                            'billing_pincode', 'state_code', 'billing_address',
                            'billing_state_city', 'billing_state_code', 'shipping_address', 'shipping_state_city',
                            'shipping_state_code', 'shipping_pincode'
                        ).first()
                        print(buyer_details, "buyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")

                        shipping_details = CustomUser.objects.filter(id=item.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code','company_gst_num',
                            'shipping_address', 'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()
                        print(shipping_details, "shippppppppppppppppppppppppppppppp")

                        if owner_details and buyer_details and shipping_details:
                            item.invoice_payload = {
                                "Version": "1.1",
                                "TranDtls": {
                                    "TaxSch": "GST",
                                    "SupTyp": "B2B",
                                    "RegRev": "Y",
                                    "EcmGstin": None,
                                    "IgstOnIntra": "N"
                                },
                                "DocDtls": {
                                    "Typ": "INV",
                                    "No": item.invoice_number,
                                    "Dt": item.created_date_time.strftime('%d/%m/%Y')
                                },
                                "SellerDtls": {
                                    "Gstin": owner_details['company_gst_num'],
                                    "LglNm": owner_details['company_name'],
                                    "Addr1": owner_details['billing_address'],
                                    "Loc": owner_details['billing_state_city'],
                                    "Pin": owner_details['billing_pincode'],
                                    "Stcd": owner_details['billing_state_code']
                                },
                                "BuyerDtls": {
                                    "Gstin": buyer_details['company_gst_num'],
                                    "LglNm": buyer_details['company_name'],
                                    "Pos": buyer_details['billing_state_code'],
                                    "Addr1": buyer_details['billing_address'],
                                    "Loc": buyer_details['billing_state_city'],
                                    "Pin": buyer_details['billing_pincode'],
                                    "Stcd": buyer_details['billing_state_code']
                                },
                                "ShipDtls": {
                                    "Gstin": shipping_details['company_gst_num'],
                                    "LglNm": shipping_details['company_name'],
                                    "Addr1": shipping_details['shipping_address'],
                                    "Loc": shipping_details['shipping_state_city'],
                                    "Pin": shipping_details['shipping_pincode'],
                                    "Stcd": shipping_details['shipping_state_code']
                                },
                                "ItemList": [
                                    {
                                        "SlNo": str(index + 1),
                                        "IsServc": "N",
                                        "HsnCd": str(drone_detail.get('hsn_number', '')),
                                        "Qty": str(drone_detail.get('quantity', 1)),
                                        "UnitPrice": str(drone_detail.get('price', 0)),
                                        # "Unit": "KGS",
                                        "Unit": str(drone_detail.get('units', '')),
                                        "TotAmt": drone_detail.get('item_total_price', ''),
                                        "AssAmt": drone_detail.get('price_after_discount', ''),
                                        "GstRt": drone_detail.get('igst', ''),
                                        "IgstAmt": drone_detail.get('igst_percentage', ''),
                                        "CgstAmt": drone_detail.get('cgst_percentage', ''),
                                        "SgstAmt": drone_detail.get('sgst_percentage', ''),
                                        "Discount": drone_detail.get('discount_amount', ''),
                                        "TotItemVal": drone_detail.get('total', '')
                                    }
                                    for index, drone_detail in enumerate(item.dronedetails)
                                ],
                                "ValDtls": {
                                    "AssVal": item.sum_of_price_after_discount,
                                    "TotInvVal": item.amount_to_pay
                                },
                                "PrecDocDtls": [{
                                    "InvNo": request.data.get('prec_doc_inv_no', '') or item.invoice_number,
                                    "InvDt": item.created_date_time.strftime('%d/%m/%Y')
                                }]
                            }

                            draft_status, _ = InvoiceStatus.objects.get_or_create(invoice_status_name='Draft')
                            item.invoice_status = draft_status
                            item.save()

                            encrypted_payload = self.encrypt(item.invoice_payload, sek_key)
                            formatted_payload = json.loads(json.dumps(item.invoice_payload, separators=(',', ':')))

                            # Prepare the data for the API request
                            api_url = "https://einv-apisandbox.nic.in/eicore/v1.03/Invoice"
                            headers = {
                                "client-id": auth_token.client_id,
                                "client-secret": "76KkYyE3SGguAaOocIWw",
                                "gstin": "29AAGCE4783K1Z1",
                                "user_name": auth_token.user_name,
                                "authtoken": auth_token.auth_token,
                            }
                            api_data = {
                                "Data": encrypted_payload,
                                "sek": sek_key
                            }

                            # Make the POST request to the API endpoint
                            response = requests.post(api_url, headers=headers, json=api_data)

                            if response.status_code == 200:
                                api_response = response.json()
                                print(f"API Response: {api_response}")
                                response_data = api_response['Status']
                                print('res_data------------', response_data)
                                response_error_details=api_response['ErrorDetails']
                                print(''''response_error_details-------------------------------------------''',response_error_details)
                                if response_error_details:  # Check if error details are present
                                    error_details = response_error_details[0]['ErrorMessage']  # Accessing the first error message
                                    print('Error Message------------------------------:', error_details)
                                # response_error_message=response_error_details['ErrorMessage']
                                # print('===========================response_error_message',response_error_message)
                                encrypted_data = api_response.get('Data')
                                print('encrypted_data----------------------', encrypted_data)

                                # Check if encrypted data is available
                                if encrypted_data:
                                    decrypted_data = self.decrypt_data(encrypted_data, sek_key)

                                    if decrypted_data is not None:
                                        print(f"Decrypted Data: {decrypted_data}")

                                        # Include decrypted data in the response
                                        api_response = {'DecryptedData': decrypted_data}

                                # Save API response as JSON string
                                api_response_json = json.dumps(api_response)

                                # Check if the status is 1 or 0
                                if response_data == 1:
                                    # Set invoice status to 2
                                    item.invoice_status_id = 2
                                    item.save(update_fields=['invoice_status_id'])
                                    item.e_invoice_status = True
                                    item.save(update_fields=['e_invoice_status'])

                                    # Save api_response in EInvoice table
                                    e_invoice_instance = EInvoice.objects.create(
                                        invoice_number=item,
                                        api_response=api_response_json,
                                        data=item.invoice_payload
                                    )

                                # Check if the error message is 'Duplicate IRN'
                                error_message = next(
                                    (error['ErrorMessage'] for error in api_response.get('ErrorDetails', []) if
                                     'Duplicate IRN' in error.get('ErrorMessage', '')), None)
                                if response_data == 0 and error_message == 'Duplicate IRN':
                                    # Set invoice status to 2
                                    item.invoice_status_id = 2
                                    item.save(update_fields=['invoice_status_id'])
                                    item.e_invoice_status = True
                                    item.save(update_fields=['e_invoice_status'])
                                # if response_data == 0:
                                #     return Response(
                                #         {"message": error_details},
                                #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                #     )

                                # Prepare response data
                                response_data = {
                                    "message": "Invoice payload updated successfully.",
                                    "Data": item.invoice_payload,
                                    "sek": sek_key,
                                    "api_response": api_response,
                                    # "Error_details": error_details
                                }
                                # if response_data == 0:
                                #     return Response(
                                #         {"message": error_details},
                                #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                #     )

                                return Response(response_data, status=status.HTTP_200_OK)

                            else:
                                return Response(
                                    {"error": f"API sheetal request failed with status code {response.status_code}"},
                                    status=response.status_code)


                        else:
                            return Response({"error": "Details not found."}, status=status.HTTP_404_NOT_FOUND)

                    else:
                        return Response({"error": "AuthToken not found."}, status=status.HTTP_404_NOT_FOUND)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif invoice_type == 'Custom':
            custom = get_object_or_404(CustomInvoice.objects.select_related('invoice_type_id'),
                                       invoice_number=invoice_number,
                                       invoice_type_id__invoice_type_name=invoice_type)
            print(custom,"custttttttttttttttttttttt")

            if custom:
                try:
                    auth_token = AuthToken.objects.first()
                    error_details=[]

                    if auth_token:
                        sek_key = auth_token.sek

                        custom_owner_details = CustomUser.objects.filter(id=custom.owner_id.id).values(
                            'company_gst_num', 'company_name', 'company_address', 'location',
                            'billing_state_city', 'billing_pincode', 'billing_state_code', 'shipping_pincode',
                            'billing_address'
                        ).first()

                        custom_buyer_details = CustomUser.objects.filter(id=custom.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code','company_gst_num',
                            'billing_address', 'billing_state_city', 'billing_state_code', 'shipping_address',
                            'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        custom_shipping_details = CustomUser.objects.filter(id=custom.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code','company_gst_num',
                            'shipping_address', 'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        if custom_owner_details and custom_buyer_details and custom_shipping_details:
                            custom.invoice_payload = {
                                "Version": "1.1",
                                "TranDtls": {
                                    "TaxSch": "GST",
                                    "SupTyp": "B2B",
                                    "RegRev": "Y",
                                    "EcmGstin": None,
                                    "IgstOnIntra": "N"
                                },
                                "DocDtls": {
                                    "Typ": "INV",
                                    "No": custom.invoice_number,
                                    "Dt": custom.created_date_time.strftime('%d/%m/%Y')
                                },
                                "SellerDtls": {
                                    "Gstin": custom_owner_details['company_gst_num'],
                                    "LglNm": custom_owner_details['company_name'],
                                    "Addr1": custom_owner_details['billing_address'],
                                    "Loc": custom_owner_details['billing_state_city'],
                                    "Pin": custom_owner_details['billing_pincode'],
                                    "Stcd": custom_owner_details['billing_state_code']
                                },
                                "BuyerDtls": {
                                    "Gstin": custom_buyer_details['company_gst_num'],
                                    "LglNm": custom_buyer_details['company_name'],
                                    "Pos": custom_buyer_details['billing_state_code'],
                                    "Addr1": custom_buyer_details['billing_address'],
                                    "Loc": custom_buyer_details['billing_state_city'],
                                    "Pin": custom_buyer_details['billing_pincode'],
                                    "Stcd": custom_buyer_details['billing_state_code']
                                },
                                "ShipDtls": {
                                    "Gstin": custom_buyer_details['company_gst_num'],
                                    "LglNm": custom_buyer_details['company_name'],
                                    "Addr1": custom_buyer_details['shipping_address'],
                                    "Loc": custom_buyer_details['shipping_state_city'],
                                    "Pin": custom_buyer_details['shipping_pincode'],
                                    "Stcd": custom_buyer_details['shipping_state_code']
                                },
                                "ItemList": [
                                    {
                                        "SlNo": str(index + 1),
                                        "IsServc": "N",
                                        "HsnCd": str(custom_item_detail.get('hsn_number', '')),
                                        "Qty": str(custom_item_detail.get('quantity', 1)),
                                        "UnitPrice": str(custom_item_detail.get('price', 0)),
                                        # "Unit": "KGS",
                                        "Unit": str(custom_item_detail.get('units', '')),
                                        "TotAmt": str(custom_item_detail.get('item_total_price', '')),
                                        "AssAmt": custom_item_detail.get('price_after_discount', ''),
                                        "GstRt": str(custom_item_detail.get('igst', '')),
                                        "IgstAmt": str(custom_item_detail.get('igst_percentage', '')),
                                        "CgstAmt": str(custom_item_detail.get('cgst_percentage', '')),
                                        "SgstAmt": str(custom_item_detail.get('sgst_percentage', '')),
                                        "Discount": str(custom_item_detail.get('discount_amount', '')),
                                        "TotItemVal": custom_item_detail.get('total', '')
                                    }
                                    for index, custom_item_detail in enumerate(custom.custom_item_details)
                                ],
                                "ValDtls": {
                                    "AssVal": custom.sum_of_price_after_discount,
                                    "TotInvVal": custom.amount_to_pay
                                },
                                "PrecDocDtls": [{
                                    "InvNo": request.data.get('prec_doc_inv_no', '') or custom.invoice_number,
                                    "InvDt": custom.created_date_time.strftime('%d/%m/%Y')
                                }]
                            }

                            draft_status, _ = InvoiceStatus.objects.get_or_create(invoice_status_name='Draft')
                            custom.invoice_status = draft_status
                            custom.save()

                            encrypted_payload = self.encrypt(custom.invoice_payload, sek_key)
                            formatted_payload = json.loads(json.dumps(custom.invoice_payload, separators=(',', ':')))

                            # Prepare the data for the API request
                            api_url = "https://einv-apisandbox.nic.in/eicore/v1.03/Invoice"
                            headers = {
                                "client-id": auth_token.client_id,
                                "client-secret": "76KkYyE3SGguAaOocIWw",
                                "gstin": "29AAGCE4783K1Z1",
                                "user_name": auth_token.user_name,
                                "authtoken": auth_token.auth_token,
                            }
                            api_data = {
                                "Data": encrypted_payload,
                                "sek": sek_key
                            }

                            # Make the POST request to the API endpoint
                            response = requests.post(api_url, headers=headers, json=api_data)

                            if response.status_code == 200:
                                api_response = response.json()
                                print(f"API Response: {api_response}")
                                response_data = api_response['Status']
                                print('res_data------------', response_data)
                                response_error_details=api_response['ErrorDetails']
                                print(''''response_error_details-------------------------------------------''',response_error_details)
                                if response_error_details:  # Check if error details are present
                                    error_details = response_error_details[0]['ErrorMessage']  # Accessing the first error message
                                    print('Error Message------------------------------:', error_details)
                                encrypted_data = api_response.get('Data')
                                print('encrypted_data----------------------', encrypted_data)

                                # Check if encrypted data is available
                                if encrypted_data:
                                    decrypted_data = self.decrypt_data(encrypted_data, sek_key)

                                    if decrypted_data is not None:
                                        print(f"Decrypted Data: {decrypted_data}")

                                        # Include decrypted data in the response
                                        api_response = {'DecryptedData': decrypted_data}

                                # Save API response as JSON string
                                api_response_json = json.dumps(api_response)

                                # Check if the status is 1 or 0
                                if response_data == 1:
                                    # Set invoice status to 2
                                    custom.invoice_status_id = 2
                                    custom.save(update_fields=['invoice_status_id'])
                                    custom.e_invoice_status = True
                                    custom.save(update_fields=['e_invoice_status'])

                                    # ewaybill_status = True if 'EwbNo' in decrypted_data else False

                                    # Update ewaybill_status in AddItem model
                                    # custom.ewaybill_status = ewaybill_status
                                    # custom.save(update_fields=['ewaybill_status'])
                                    print(custom.invoice_payload,"vvvvvvvvvvvvvvvvvvvvvvvv")
                                    print(api_response_json,"ppppppppppppppppppppppppppppppppp")

                                    # Save api_response in EInvoice table
                                    e_invoice_instance = EInvoice.objects.create(
                                        invoice_number_custominvoice=custom,
                                        api_response=api_response_json,
                                        data=custom.invoice_payload
                                    )



                                # Check if the error message is 'Duplicate IRN'
                                error_message = next(
                                    (error['ErrorMessage'] for error in api_response.get('ErrorDetails', []) if
                                     'Duplicate IRN' in error.get('ErrorMessage', '')), None)
                                if response_data == 0 and error_message == 'Duplicate IRN':
                                    # Set invoice status to 2
                                    custom.invoice_status_id = 2
                                    custom.save(update_fields=['invoice_status_id'])
                                    # custom.ewaybill_status = True
                                    custom.save(update_fields=['e_invoice_status'])

                                if response_data == 0:
                                    return Response(
                                        {"message": error_details},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                    )
                                # Prepare response data
                                response_data = {
                                    "message": "Invoice payload updated successfully.",
                                    "Data": custom.invoice_payload,
                                    "sek": sek_key,
                                    "api_response": api_response,
                                    "Error_details": error_details
                                }
                                print('encrypted payload', response_data['Data'])
                                if response_data == 0:
                                    return Response(
                                        {"message": error_details},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                    )

                                return Response(response_data, status=status.HTTP_200_OK)

                            else:
                                return Response(
                                    {"error": f"API sheetal request failed with status code "},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        else:
                            return Response({"error": "Details not found."}, status=status.HTTP_404_NOT_FOUND)

                    else:
                        return Response({"error": "AuthToken not found."}, status=status.HTTP_404_NOT_FOUND)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Invoice not found or invoice_type not supported."}, status=status.HTTP_404_NOT_FOUND)



    def decrypt_data(self, encrypted_data, sek_key_base64):
        try:
            # Decode the base64 encoded sek key
            sek_key = base64.b64decode(sek_key_base64)

            # Decode the base64 encoded data
            decoded_data = base64.b64decode(encrypted_data)

            # Create AES cipher object with ECB mode
            cipher = AES.new(sek_key, AES.MODE_ECB)

            # Decrypt the data
            decrypted_data = cipher.decrypt(decoded_data)

            # Unpad the decrypted data
            unpadded_data = unpad(decrypted_data, AES.block_size)

            # Convert decrypted data from bytes to string
            decrypted_string = unpadded_data.decode('utf-8')

            # Convert decrypted string to JSON
            decrypted_json = json.loads(decrypted_string)

            return decrypted_json

        except Exception as e:
            print(f"Error decrypting data: {str(e)}")
            return None

    def post(self, request, *args, **kwargs):
        invoice_number = request.data.get('invoice_number')
        invoice_type = request.data.get('invoice_type')

        if not invoice_number:
            return Response({"error": "Missing invoice_number in the request body."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not invoice_type:
            return Response({"error": "Missing invoice_type in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        if invoice_type == "Drone":
            item = get_object_or_404(AddItem, invoice_number=invoice_number)

            if item:
                try:
                    auth_token = AuthToken.objects.first()

                    if auth_token:
                        sek_key = auth_token.sek

                        owner_details = CustomUser.objects.filter(id=item.owner_id.id).values(
                            'company_gst_num', 'company_name', 'company_address', 'location',
                            'billing_state_city', 'billing_pincode', 'billing_state_code', 'shipping_pincode',
                            'billing_address'
                        ).first()

                        buyer_details = CustomUser.objects.filter(id=item.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code',
                            'billing_address', 'billing_state_city', 'billing_state_code', 'shipping_address',
                            'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        shipping_details = CustomUser.objects.filter(id=item.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code',
                            'shipping_address', 'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        if owner_details and buyer_details and shipping_details:
                            item.invoice_payload = {
                                "Version": "1.1",
                                "TranDtls": {
                                    "TaxSch": "GST",
                                    "SupTyp": "B2B",
                                    "RegRev": "Y",
                                    "EcmGstin": None,
                                    "IgstOnIntra": "N"
                                },
                                "DocDtls": {
                                    "Typ": "INV",
                                    "No": item.invoice_number,
                                    "Dt": item.created_date_time.strftime('%d/%m/%Y')
                                },
                                "SellerDtls": {
                                    "Gstin": owner_details['company_gst_num'],
                                    "LglNm": owner_details['company_name'],
                                    "Addr1": owner_details['billing_address'],
                                    "Loc": owner_details['billing_state_city'],
                                    "Pin": owner_details['billing_pincode'],
                                    "Stcd": owner_details['billing_state_code']
                                },
                                "BuyerDtls": {
                                    "Gstin": buyer_details['gst_number'],
                                    "LglNm": buyer_details['company_name'],
                                    "Pos": buyer_details['billing_state_code'],
                                    "Addr1": buyer_details['billing_address'],
                                    "Loc": buyer_details['billing_state_city'],
                                    "Pin": buyer_details['billing_pincode'],
                                    "Stcd": buyer_details['billing_state_code']
                                },
                                "ShipDtls": {
                                    "Gstin": buyer_details['gst_number'],
                                    "LglNm": buyer_details['company_name'],
                                    "Addr1": buyer_details['shipping_address'],
                                    "Loc": buyer_details['shipping_state_city'],
                                    "Pin": buyer_details['shipping_pincode'],
                                    "Stcd": buyer_details['shipping_state_code']
                                },
                                "ItemList": [
                                    {
                                        "SlNo": str(index + 1),
                                        "IsServc": "N",
                                        "HsnCd": str(drone_detail.get('hsn_number', '')),
                                        "Qty": str(drone_detail.get('quantity', 1)),
                                        "UnitPrice": str(drone_detail.get('price', 0)),
                                        # "Unit": "KGS",  # You can adjust this field based on your data
                                        "Unit": str(drone_detail.get('units', '')),
                                        "TotAmt": str(drone_detail.get('item_total_price', '')),
                                        "AssAmt": str(float(drone_detail.get('item_total_price', 0)) - float(
                                            item.discount_amount)),
                                        "GstRt": item.igst,
                                        "CgstAmt": item.cgst_amount,
                                        "SgstAmt": item.sgst_amount,
                                        "Discount": item.discount_amount,
                                        "TotItemVal": str(float(drone_detail.get('item_total_price', 0)) - float(
                                            item.discount_amount) + float(
                                            item.igst) + item.cgst_amount + item.sgst_amount)
                                    }
                                    for index, drone_detail in enumerate(item.dronedetails)
                                ],
                                "ValDtls": {
                                    "AssVal": str(sum(
                                        float(drone_detail.get('item_total_price', 0)) - float(item.discount_amount) for
                                        drone_detail in item.dronedetails)),
                                    "TotInvVal": str(sum(float(drone_detail.get('item_total_price', 0)) - float(
                                        item.discount_amount) + float(item.igst) + item.cgst_amount + item.sgst_amount
                                                         for drone_detail in item.dronedetails))
                                },
                                "PrecDocDtls": [{
                                    "InvNo": request.data.get('prec_doc_inv_no', '') or item.invoice_number,
                                    "InvDt": item.created_date_time.strftime('%d/%m/%Y')
                                }]
                            }

                            draft_status, _ = InvoiceStatus.objects.get_or_create(invoice_status_name='Draft')
                            item.invoice_status = draft_status
                            item.save()

                            encrypted_payload = self.encrypt(item.invoice_payload, sek_key)
                            formatted_payload = json.loads(json.dumps(item.invoice_payload, separators=(',', ':')))

                            # Prepare the data for the API request
                            api_url = "https://einv-apisandbox.nic.in/eicore/v1.03/Invoice"
                            headers = {
                                "client-id": auth_token.client_id,
                                "client-secret": "76KkYyE3SGguAaOocIWw",
                                "gstin": "29AAGCE4783K1Z1",
                                "user_name": auth_token.user_name,
                                "authtoken": auth_token.auth_token,
                            }
                            api_data = {
                                "encrypted_payload": encrypted_payload,
                                "sek": sek_key
                            }

                            # Make the POST request to the API endpoint
                            response = requests.post(api_url, headers=headers, json=api_data)

                            # Check if the request was successful
                            if response.status_code == 200:
                                api_response = response.json()
                                print(f"API Response: {api_response}")
                                response_data = api_response['Status']
                                print('res_data------------', response_data)

                                response_data = {
                                    "message": "Invoice data saved successfully.",
                                }
                                return Response(response_data, status=status.HTTP_200_OK)
                            else:
                                return Response(
                                    {"error": f"API request failed with status code {response.status_code}"},
                                    status=response.status_code)

                        else:
                            return Response({"error": "Details not found."}, status=status.HTTP_404_NOT_FOUND)

                    else:
                        return Response({"error": "AuthToken not found."}, status=status.HTTP_404_NOT_FOUND)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        elif invoice_type == "Custom":
            custom = get_object_or_404(CustomInvoice, invoice_number=invoice_number)

            if custom:
                try:
                    auth_token = AuthToken.objects.first()

                    if auth_token:
                        sek_key = auth_token.sek

                        custom_owner_details = CustomUser.objects.filter(id=custom.owner_id.id).values(
                            'company_gst_num', 'company_name', 'company_address', 'location',
                            'billing_state_city', 'billing_pincode', 'billing_state_code', 'shipping_pincode',
                            'billing_address'
                        ).first()

                        custom_buyer_details = CustomUser.objects.filter(id=custom.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code',
                            'billing_address', 'billing_state_city', 'billing_state_code', 'shipping_address',
                            'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        custom_shipping_details = CustomUser.objects.filter(id=custom.customer_id.id).values(
                            'gst_number', 'company_name', 'address', 'location', 'billing_pincode', 'state_code',
                            'shipping_address', 'shipping_state_city', 'shipping_state_code', 'shipping_pincode'
                        ).first()

                        if custom_owner_details and custom_buyer_details and custom_shipping_details:
                            custom.invoice_payload = {
                                "Version": "1.1",
                                "TranDtls": {
                                    "TaxSch": "GST",
                                    "SupTyp": "B2B",
                                    "RegRev": "Y",
                                    "EcmGstin": None,
                                    "IgstOnIntra": "N"
                                },
                                "DocDtls": {
                                    "Typ": "INV",
                                    "No": custom.invoice_number,
                                    "Dt": custom.created_date_time.strftime('%d/%m/%Y')
                                },
                                "SellerDtls": {
                                    "Gstin": custom_owner_details['company_gst_num'],
                                    "LglNm": custom_owner_details['company_name'],
                                    "Addr1": custom_owner_details['billing_address'],
                                    "Loc": custom_owner_details['billing_state_city'],
                                    "Pin": custom_owner_details['billing_pincode'],
                                    "Stcd": custom_owner_details['billing_state_code']
                                },
                                "BuyerDtls": {
                                    "Gstin": custom_buyer_details['gst_number'],
                                    "LglNm": custom_buyer_details['company_name'],
                                    "Pos": custom_buyer_details['billing_state_code'],
                                    "Addr1": custom_buyer_details['billing_address'],
                                    "Loc": custom_buyer_details['billing_state_city'],
                                    "Pin": custom_buyer_details['billing_pincode'],
                                    "Stcd": custom_buyer_details['billing_state_code']
                                },
                                "ShipDtls": {
                                    "Gstin": custom_buyer_details['gst_number'],
                                    "LglNm": custom_buyer_details['company_name'],
                                    "Addr1": custom_buyer_details['shipping_address'],
                                    "Loc": custom_buyer_details['shipping_state_city'],
                                    "Pin": custom_buyer_details['shipping_pincode'],
                                    "Stcd": custom_buyer_details['shipping_state_code']
                                },
                                "ItemList": [
                                    {
                                        "SlNo": str(index + 1),
                                        "IsServc": "N",
                                        "HsnCd": str(custom_item_detail.get('hsn_number', '')),
                                        "Qty": str(custom_item_detail.get('quantity', 1)),
                                        "UnitPrice": str(custom_item_detail.get('price', 0)),
                                        # "Unit": "KGS",  # You can adjust this field based on your data
                                        "Unit": str(custom_item_detail.get('units', '')),
                                        "TotAmt": str(custom_item_detail.get('item_total_price', '')),
                                        "AssAmt": str(float(custom_item_detail.get('item_total_price', 0)) - float(
                                            custom_item_detail.get('discount_amount', ''))),
                                        "GstRt": str(custom_item_detail.get('igst', '')),
                                        "IgstAmt": str(custom_item_detail.get('igst_percentage', '')),
                                        "CgstAmt": str(custom_item_detail.get('cgst_percentage', '')),
                                        "SgstAmt": str(custom_item_detail.get('sgst_percentage', '')),
                                        "Discount": str(custom_item_detail.get('discount_amount', '')),
                                        "TotItemVal": str(float(custom_item_detail.get('item_total_price', 0)) - float(
                                            custom_item_detail.get('discount_amount', '')) + float(
                                            custom_item_detail.get('igst', '')) + float(
                                            custom_item_detail.get('cgst_percentage', '')) + float(
                                            custom_item_detail.get('sgst_percentage', '')))
                                    }
                                    for index, custom_item_detail in enumerate(custom.custom_item_details)
                                ],
                                "ValDtls": {
                                    "AssVal": custom.sum_of_price_after_discount,
                                    "TotInvVal": custom.amount_to_pay
                                },
                                "PrecDocDtls": [{
                                    "InvNo": request.data.get('prec_doc_inv_no', '') or custom.invoice_number,
                                    "InvDt": custom.created_date_time.strftime('%d/%m/%Y')
                                }]
                            }

                            draft_status, _ = InvoiceStatus.objects.get_or_create(invoice_status_name='Draft')
                            custom.invoice_status = draft_status
                            custom.save()

                            encrypted_payload = self.encrypt(custom.invoice_payload, sek_key)
                            formatted_payload = json.loads(json.dumps(custom.invoice_payload, separators=(',', ':')))

                            # Prepare the data for the API request
                            api_url = "https://einv-apisandbox.nic.in/eicore/v1.03/Invoice"
                            headers = {
                                "client-id": auth_token.client_id,
                                "client-secret": "76KkYyE3SGguAaOocIWw",
                                "gstin": "29AAGCE4783K1Z1",
                                "user_name": auth_token.user_name,
                                "authtoken": auth_token.auth_token,
                            }
                            api_data = {
                                "encrypted_payload": encrypted_payload,
                                "sek": sek_key
                            }

                            # Make the POST request to the API endpoint
                            response = requests.post(api_url, headers=headers, json=api_data)

                            # Check if the request was successful
                            if response.status_code == 200:
                                api_response = response.json()
                                print(f"API Response: {api_response}")
                                response_data = api_response['Status']
                                print('res_data------------', response_data)

                                response_data = {
                                    "message": "Invoice data saved successfully.",
                                }
                                return Response(response_data, status=status.HTTP_200_OK)
                            else:
                                return Response(
                                    {"error": f"API request failed with status code {response.status_code}"},
                                    status=response.status_code)

                        else:
                            return Response({"error": "Details not found."}, status=status.HTTP_404_NOT_FOUND)

                    else:
                        return Response({"error": "AuthToken not found."}, status=status.HTTP_404_NOT_FOUND)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Invalid invoice_type provided."}, status=status.HTTP_400_BAD_REQUEST)
import ast

class InvoiceHistoy(APIView):
    def get(self, request, owner_id=None, invoice_number=None):
        role_filter = request.query_params.get('filter', '').lower()
        partner_id = request.query_params.get('id', None)

        if role_filter == 'all':
            if owner_id:
                try:
                    owner = CustomUser.objects.get(id=owner_id)
                except CustomUser.DoesNotExist:
                    return JsonResponse({"message": "Owner not found"}, status=404)

                # Assuming 'role' is a field in your user model
                user_role = owner.role_id.role_name  # Replace 'role' with your actual field name for role

                if user_role != 'Super_admin':
                    return JsonResponse({"message": "Access denied"}, status=403)

            # Display all data for super admin and partner with status as completed
            items = AddItem.objects.filter(invoice_status__invoice_status_name="Completed")

        elif role_filter == 'partner':
            if partner_id and owner_id and CustomUser.objects.filter(id=owner_id,
                                                                     role_id__role_name='Super_admin').exists():
                # Display all partners with status as completed based on the provided partner_id
                items = AddItem.objects.filter(owner_id__role_id__role_name='Partner', owner_id=partner_id,
                                               invoice_status__invoice_status_name="Completed")
            else:
                # Display all partners with status as completed
                items = AddItem.objects.filter(owner_id__role_id__role_name='Partner',
                                               invoice_status__invoice_status_name="Completed")

        elif owner_id:
            try:
                owner = CustomUser.objects.get(id=owner_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({"message": "Owner not found"}, status=404)

            items = AddItem.objects.filter(owner_id=owner, invoice_status__invoice_status_name="Completed")

        elif invoice_number:
            try:
                item = AddItem.objects.get(invoice_number=invoice_number,
                                           invoice_status__invoice_status_name="Completed")
            except AddItem.DoesNotExist:
                return JsonResponse({"message": "Invoice not found"}, status=404)
            owner = item.owner_id
            items = [item]  # Since we are dealing with a single invoice

        else:
            return JsonResponse({"message": "Invalid request"}, status=400)
        # items = items.order_by('-id')
        item_list = []
        for item in items:
            ewaybill_status = False
    
            # Check if the invoice status is completed
            if item.invoice_status == "Completed":
                # Set ewaybill_status to True
                ewaybill_status = True
            # Your existing code to process owner_data, customer_data, etc.
            owner = item.owner_id
            owner_data = {
                "id": owner.id,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "full_name": owner.get_full_name(),
                "email": owner.email,
                "mobile_number": owner.mobile_number,
                "address": owner.address,
                "pin_code": owner.pin_code,
                "pan_number": owner.pan_number,
                "profile_pic": f"/media/{owner.profile_pic}" if owner.profile_pic else None,
                # "profile_pic": str(owner.profile_pic) if owner.profile_pic else None,
                "company_name": owner.company_name,
                "company_email": owner.company_email,
                "company_address": owner.company_address,
                "shipping_address": owner.shipping_address,
                "billing_address": owner.billing_address,
                "company_phn_number": owner.company_phn_number,
                "company_gst_num": owner.company_gst_num,
                "company_cin_num": owner.company_cin_num,
                "company_logo": f"/media/{owner.company_logo}" if owner.company_logo else None,
                # "company_logo": str(owner.company_logo) if owner.company_logo else None,
                "role_id": owner.role_id.id if owner.role_id else None,
                "location": owner.location,
                "reason": owner.reason,
                "partner_initial_update": owner.partner_initial_update,
                "gst_number": owner.gst_number,
                "inventory_count": owner.inventory_count,
                "category_id": owner.category.id if owner.category else None,
                "date_of_birth": owner.date_of_birth,
                "gender": owner.gender,
                "created_by_id": owner.created_by_id,
                "state_name": owner.state_name,
                "state_code": owner.state_code,
                "shipping_pincode": owner.shipping_pincode,
                "billing_pincode": owner.billing_pincode,
                "shipping_state": owner.shipping_state,
                "shipping_state_code": owner.shipping_state_code,
                "shipping_state_city": owner.shipping_state_city,
                "shipping_state_country": owner.shipping_state_country,
                "billing_state": owner.billing_state,
                "billing_state_code": owner.billing_state_code,
                "billing_state_city": owner.billing_state_city,
                "billing_state_country": owner.billing_state_country,
                "gstin_reg_type": owner.gstin_reg_type,
            }


            customer_data = {
                "id": item.customer_id.id if item.customer_id else None,
                "first_name": item.customer_id.first_name if item.customer_id else None,
                "last_name": item.customer_id.last_name if item.customer_id else None,
                "full_name": item.customer_id.get_full_name() if item.customer_id else None,
                "email": item.customer_id.email if item.customer_id else None,
                "mobile_number": item.customer_id.mobile_number if item.customer_id else None,
                "address": item.customer_id.address if item.customer_id else None,
                "pin_code": item.customer_id.pin_code if item.customer_id else None,
                "pan_number": item.customer_id.pan_number if item.customer_id else None,
                'profile_pic': f"/media/{item.customer_id.profile_pic}" if item.customer_id and item.customer_id.profile_pic else None,

                # "profile_pic": str(
                #     item.customer_id.profile_pic) if item.customer_id and item.customer_id.profile_pic else None,
                "company_name": item.customer_id.company_name if item.customer_id else None,
                "company_email": item.customer_id.company_email if item.customer_id else None,
                "company_address": item.customer_id.company_address if item.customer_id else None,
                "shipping_address": item.customer_id.shipping_address if item.customer_id else None,
                "billing_address": item.customer_id.billing_address if item.customer_id else None,
                "company_phn_number": item.customer_id.company_phn_number if item.customer_id else None,
                "company_gst_num": item.customer_id.company_gst_num if item.customer_id else None,
                "company_cin_num": item.customer_id.company_cin_num if item.customer_id else None,
                # "company_logo": str(
                #     item.customer_id.company_logo) if item.customer_id and item.customer_id.company_logo else None,
                'company_logo': f"/media/{item.customer_id.company_logo}" if item.customer_id and item.customer_id.company_logo else None,
                "role_id": item.customer_id.role_id.id if item.customer_id and item.customer_id.role_id else None,
                "created_date_time": item.customer_id.created_date_time if item.customer_id else None,
                "updated_date_time": item.customer_id.updated_date_time if item.customer_id else None,
                "status": item.customer_id.status if item.customer_id else None,
                "location": item.customer_id.location if item.customer_id else None,
                "reason": item.customer_id.reason if item.customer_id else None,
                "partner_initial_update": item.customer_id.partner_initial_update if item.customer_id else None,
                "gst_number": item.customer_id.gst_number if item.customer_id else None,
                "inventory_count": item.customer_id.inventory_count if item.customer_id else None,
                "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                "date_of_birth": item.customer_id.date_of_birth if item.customer_id else None,
                "gender": item.customer_id.gender if item.customer_id else None,
                "created_by_id": item.customer_id.created_by_id if item.customer_id else None,
                "shipping_pincode": item.customer_id.shipping_pincode if item.customer_id else None,
                "billing_pincode": item.customer_id.billing_pincode if item.customer_id else None,
                "shipping_state": item.customer_id.shipping_state if item.customer_id else None,
                "shipping_state_code": item.customer_id.shipping_state_code if item.customer_id else None,
                "shipping_state_city": item.customer_id.shipping_state_city if item.customer_id else None,
                "shipping_state_country": item.customer_id.shipping_state_country if item.customer_id else None,
                "billing_state": item.customer_id.billing_state if item.customer_id else None,
                "billing_state_code": item.customer_id.billing_state_code if item.customer_id else None,
                "billing_state_city": item.customer_id.billing_state_city if item.customer_id else None,
                "billing_state_country": item.customer_id.billing_state_country if item.customer_id else None,
                "gstin_reg_type":item.customer_id.gstin_reg_type if item.customer_id else None,
            }

            invoice_type_details = {
                'id': item.invoice_type_id.id if item.invoice_type_id else None,
                'name': item.invoice_type_id.invoice_type_name if item.invoice_type_id else None,
            }

            customer_category = {
                "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
                "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
            }
            drone_details = item.dronedetails
            drone_info_list = []

            if drone_details:
                for drone_detail in drone_details:
                    drone_id = drone_detail["drone_id"]
                    quantity = drone_detail["quantity"]
                    price = drone_detail["price"]
                    serial_numbers = drone_detail.get("serial_numbers", [])
                    hsn_number = drone_detail["hsn_number"]
                    item_total_price = drone_detail.get("item_total_price", 0)
                    discount = drone_detail.get("discount", 0)
                    igst = drone_detail.get("igst", 0)
                    cgst = drone_detail.get("cgst", 0)
                    sgst = drone_detail.get("sgst", 0)
                    created_datetime = drone_detail.get("created_datetime")
                    updated_datetime = drone_detail.get("updated_datetime")
                    discount_amount = drone_detail.get("discount_amount")
                    price_after_discount = drone_detail.get("price_after_discount")
                    igst_percentage = drone_detail.get("igst_percentage", 0)
                    cgst_percentage = drone_detail.get("cgst_percentage", 0)
                    sgst_percentage = drone_detail.get("sgst_percentage", 0)
                    total = drone_detail.get("total", 0)

                    try:
                        drone = Drone.objects.get(id=drone_id)
                        drone_ownership = DroneOwnership.objects.filter(user=owner, drone=drone_id).first()
                        remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                        drone_info = {
                            "drone_id": drone.id,
                            "drone_name": drone.drone_name,
                            "drone_category": drone.drone_category.category_name if drone.drone_category else None,
                            "quantity": quantity,
                            "price": price,
                            "serial_numbers": drone_detail.get("serial_numbers", []),
                            "hsn_number": drone_detail["hsn_number"],
                            "item_total_price": drone_detail.get("item_total_price", 0),
                            "remaining_quantity": remaining_quantity,
                            "discount":discount,
                            "igst":igst,
                            "cgst":cgst,
                            "sgst":sgst,
                            "created_datetime":created_datetime,
                            "updated_datetime":updated_datetime,
                            "discount_amount":discount_amount,
                            "price_after_discount":price_after_discount,
                            "igst_percentage":igst_percentage,
                            "cgst_percentage":cgst_percentage,
                            "sgst_percentage":sgst_percentage,
                            "total":total
                        }
                        drone_info_list.append(drone_info)
                    except Drone.DoesNotExist:
                        pass

            item_data = {
                "id": item.id,
                "customer_type_id": item.customer_type_id.id if item.customer_type_id else None,
                "customer_details": customer_data,
                "owner_id": owner.id if owner else None,
                "owner_details": owner_data,
                'invoice_type_details': invoice_type_details,
                'customer_category': customer_category,
                "dronedetails": drone_info_list,
                "e_invoice_status": item.e_invoice_status,
                "ewaybill_status":item.ewaybill_status,
                "invoice_number": item.invoice_number,
                "created_date_time": item.created_date_time,
                "updated_date_time": item.updated_date_time,
                "signature_url": item.signature.url if item.signature else None,
                "invoice_status": item.invoice_status.invoice_status_name if item.invoice_status else None,
                "invoice_status_id": item.invoice_status.id if item.invoice_status else None,
                "amount_to_pay":item.amount_to_pay,
                "sum_of_item_total_price":item.sum_of_item_total_price,
                "sum_of_igst_percentage":item.sum_of_igst_percentage,
                "sum_of_cgst_percentage":item.sum_of_cgst_percentage,
                "sum_of_sgst_percentage": item.sum_of_sgst_percentage,
                "sum_of_discount_amount": item.sum_of_discount_amount,
                "sum_of_price_after_discount": item.sum_of_price_after_discount,

            }

            # e_invoice_data = EInvoice.objects.filter(invoice_number=item).values('api_response', 'data','e_waybill').first()
            #
            # # Parse JSON data if available
            # api_response_data = json.loads(e_invoice_data['api_response']) if e_invoice_data and e_invoice_data[
            #     'api_response'] else None
            #
            # # Convert 'data' field from string to dictionary
            # data_dict = ast.literal_eval(e_invoice_data['data']) if e_invoice_data and e_invoice_data['data'] else None
            #
            # # Add EInvoice data to the item_data dictionary
            # item_data['e_invoice_data'] = {
            #     'api_response': api_response_data,
            #     'data': data_dict,
            #     'e_waybill': e_invoice_data['e_waybill'],
            # }
            e_invoice_data = EInvoice.objects.filter(invoice_number=item).values('api_response', 'data',
                                                                                 'e_waybill').first()

            # Check if e_invoice_data is not None
            if e_invoice_data:
                # Parse JSON data if available
                api_response_data = json.loads(e_invoice_data['api_response']) if e_invoice_data and e_invoice_data[
                    'api_response'] else None

                # Convert 'data' field from string to dictionary
                data_dict = ast.literal_eval(e_invoice_data['data']) if e_invoice_data and e_invoice_data[
                    'data'] else None

                # Add EInvoice data to the item_data dictionary
                item_data['e_invoice_data'] = {
                    'api_response': api_response_data,
                    'data': data_dict,
                }

                # Convert 'e_waybill' field from string to dictionary
                try:
                    e_waybill_dict = ast.literal_eval(e_invoice_data.get('e_waybill', '{}'))
                except ValueError:
                    e_waybill_dict = {}

                # Add e_waybill outside e_invoice_data
                item_data['ewaybill'] = {
                    'EwbNo': e_waybill_dict.get('EwbNo', None),
                    'EwbDt': e_waybill_dict.get('EwbDt', None),
                    'EwbValidTill': e_waybill_dict.get('EwbValidTill', None),
                }

            item_list.append(item_data)
        item_list.sort(key=lambda x: x['updated_date_time'], reverse=True)

        return JsonResponse({"items": item_list}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class EwayBill(View):
    @transaction.atomic
    def post(self, request):
        error_details=[]
        try:
            payload = json.loads(request.body)
            invoice_number = payload.get('invoice_number')
            invoice_type = payload.get('invoice_type')

            if invoice_type == 'Drone':
                add_item = AddItem.objects.get(invoice_number=invoice_number)
                e_invoices = EInvoice.objects.filter(invoice_number__invoice_number=invoice_number)
            elif invoice_type == 'Custom':
                add_item = CustomInvoice.objects.get(invoice_number=invoice_number)
                e_invoices = EInvoice.objects.filter(invoice_number_custominvoice__invoice_number=invoice_number)
            else:
                return JsonResponse({'message': 'Invalid invoice_type'}, status=400)

            e_invoice = e_invoices.first()

            if e_invoice:
                api_response = json.loads(e_invoice.api_response)
                print('api_response----------------',api_response)
                Irn = api_response.get('DecryptedData', {}).get('Irn')
                print('irn--------------',Irn)
            else:
                return JsonResponse({'message': 'EInvoice record not found for the provided invoice_number'}, status=404)

            transport_details = TransportationDetails.objects.get(invoice_number=invoice_number)
            Distance = transport_details.distance
            TransMode = transport_details.transmode
            TransId = transport_details.transid
            TransName = transport_details.transname
            TransDocDt = transport_details.transDocDt
            TransDocNo = transport_details.transDocNo
            VehNo = transport_details.vehNo
            VehType = transport_details.vehType

            data = {
                "Irn": Irn,
                "Distance": Distance,
                "TransMode": TransMode,
                "TransId": TransId,
                "TransName": TransName,
                "TransDocDt": TransDocDt,
                "TransDocNo": TransDocNo,
                "VehNo": VehNo,
                "VehType": VehType
            }

            auth_token = AuthToken.objects.first()
            sek_key = auth_token.sek
            encrypted_payload, sek_key = self.encrypt(data, sek_key)

            add_item.ewaybill_payload = data
            add_item.save()

            api_url = "https://einv-apisandbox.nic.in/eiewb/v1.03/ewaybill"
            headers = {
                "client-id": auth_token.client_id,
                "client-secret": "76KkYyE3SGguAaOocIWw",
                "gstin": "29AAGCE4783K1Z1",
                "user_name": auth_token.user_name,
                "authtoken": auth_token.auth_token,
            }
            api_data = {
                "Data": encrypted_payload,
                "sek": sek_key
            }
            response = requests.post(api_url, json=api_data, headers=headers)
            print('''''''response---------------''',response)
            response_json = response.json()
            print("Response JSONnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn:", response_json)
            response_status=response_json.get('Status')
            print('ooooooooooooooooooooooooresponse_status',response_status)
            # error_details = []
            # if response_status == 0:
            #     return Response(
            #         {"message": error_details},
            #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
            #         )
            ewaybill_error_data = response_json['ErrorDetails']
            print('ewaybill_error_data======================',ewaybill_error_data)
            if ewaybill_error_data:  # Check if error details are present
                error_details = ewaybill_error_data[0]['ErrorMessage']  # Accessing the first error message
                print('Error Message------------------------------:', error_details)

            if response.status_code == 200:
                decrypted_data = self.decrypt_data(response.json().get('Data'), sek_key)
                print('decrypted_data---------------',decrypted_data)
 
                response_data = {
                    # 'Error_details':error_details,
                    'ewaybill': response.json(),
                    'sek': sek_key,
                    'Decrypted_data': decrypted_data,
                    'e_waybill_payload': payload,
                    "Irn": Irn,
                    "Distance": Distance,
                    "TransMode": TransMode,
                    "TransId": TransId,
                    "TransName": TransName,
                    "TransDocDt": TransDocDt,
                    "TransDocNo": TransDocNo,
                    "VehNo": VehNo,
                    "VehType": VehType, 
                    "error_details": error_details 
                }
                ewaybill_data = response_data['ewaybill']
                print('ewaybill_data----------ewaybill_data,',ewaybill_data)
                ewaybill_status = ewaybill_data.get('Status')
                # print('ewaybill_status----------ewaybill_status,',ewaybill_status)
                if ewaybill_status == 1:
                    e_invoice.e_waybill = json.dumps(decrypted_data)
                    e_invoice.save()
                    add_item.ewaybill_status = True
                    add_item.save()
                elif ewaybill_status == 0:
                    # Handle status 0 accordingly
                    pass
                if ewaybill_status == 0:
                    # If ewaybill_status is 0, return 500 Internal Server Error
                    return JsonResponse(response_data, status=500)
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({'message': 'Failed to update E-waybill payload', 'response': response.json()}, status=response.status_code)

        except AddItem.DoesNotExist:
            return JsonResponse({'message': 'AddItem not found for the provided invoice_number'}, status=404)
        except EInvoice.DoesNotExist:
            return JsonResponse({'message': 'EInvoice record not found for the provided invoice_number'}, status=404)
        except TransportationDetails.DoesNotExist:
            return JsonResponse({'message': 'Transportation details not found for the provided invoice_number'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)

    def encrypt(self, payload, sek_key):
        cleaned_payload = self.clean_payload(json.dumps(payload, separators=(',', ':')))
        decoded_sek_key = base64.b64decode(sek_key)
        cipher = AES.new(decoded_sek_key, AES.MODE_ECB)
        encrypted_data = cipher.encrypt(pad(cleaned_payload.encode(), AES.block_size))
        encrypted_text = base64.b64encode(encrypted_data).decode()
        return encrypted_text, sek_key

    def decrypt_data(self, encrypted_data, sek_key_base64):
        try:
            sek_key = base64.b64decode(sek_key_base64)
            cipher = AES.new(sek_key, AES.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
            decrypted_string = decrypted_data.decode('utf-8')
            decrypted_json = json.loads(decrypted_string)
            return decrypted_json
        except Exception as e:
            print(f"Error decrypting data: {str(e)}")
            return None

    def clean_payload(self, payload):
        cleaned_payload = ''.join(char for char in payload if char.isprintable())
        return cleaned_payload


class GstRateValuesAPI(APIView):
    def get(self, request):
        id = request.query_params.get('id')

        if id is not None:
            gst_type = GstRateValues.objects.filter(id=id).first()
            if gst_type:
                data = {'id': gst_type.id, 'gstrates': gst_type.gstrates}
                return Response(data)
            else:
                return Response({'message': 'Gstrate not found for the specified id'}, status=404)
        else:
            # Convert the queryset to a list of dictionaries
            invoice_types = list(GstRateValues.objects.values())
            return Response({'Result': invoice_types})


    def post(self,request):
        data=request.data
        gstrates=data.get('gstrates')

        if GstRateValues.objects.filter(gstrates=gstrates).exists():
            return Response({'message': 'gstrates is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data=GstRateValues.objects.create(gstrates=gstrates)
            return Response({'message': 'GST rate value added successfully'})

    def delete(self,request,pk):
        data=request.data
        

        if GstRateValues.objects.filter(id=pk).exists():
            data=GstRateValues.objects.filter(id=pk).delete()
            return Response({'message':'gstrates deleted!!'})
        else:
            return Response({'result':'gstrates not found!!'})
            


from decimal import Decimal, ROUND_HALF_UP

class AddCustomItemAPI(APIView):
    def create_invoice_number(self):
        try:
            while True:
                # Generate a unique UUID
                unique_uuid = uuid.uuid4()

                # Convert UUID to a 4-digit string and prepend "IAMX"
                invoice_number = f"IAMX-{int(unique_uuid.int % 1e4):04d}"

                # Check if the generated invoice_number is unique in the AddItem table
                if not AddItem.objects.filter(invoice_number=invoice_number).exists() and \
                        not CustomInvoice.objects.filter(invoice_number=invoice_number).exists():
                    return invoice_number
        except Exception as e:
            # Handle any exceptions that may occur during invoice_number generation
            raise RuntimeError(f"Error generating invoice_number: {str(e)}")

    # def calculate_item_total_price(self, price, quantity):
    #     return str(Decimal(price) * Decimal(quantity))

    def calculate_item_total_price(self, price, quantity):
        total_price = Decimal(price) * Decimal(quantity)
        rounded_total_price = total_price.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return float(rounded_total_price)

    def post(self, request):
        data = request.data
        items = data.get('items', [])
        owner_id = data.get('owner_id')
        customer_type_id = data.get('customer_type_id')
        customer_id = data.get('customer_id')
        invoice_type_id = data.get('invoice_type_id')
        partner_instance = get_object_or_404(CustomUser, id=owner_id)
        all_serialnumbers = []

        custom_item_details_lists = CustomInvoice.objects.values_list('custom_item_details', flat=True)

        for custom_item_details_list in custom_item_details_lists:
            if custom_item_details_list:
                serial_numbers = [serial_number for entry in custom_item_details_list for serial_number in
                                  entry.get('serial_numbers', [])]
                all_serialnumbers.extend(serial_numbers)

        all_items_except_given_id = AddItem.objects.all().values('id', 'dronedetails')
        for item_data in all_items_except_given_id:
            for drone_detail in item_data['dronedetails']:
                serial_numbers = drone_detail.get('serial_numbers', [])
                all_serialnumbers.extend(serial_numbers)

        items_data = []
        custom_item_details = []
        all_serial_numbers = set()

        is_super_admin = partner_instance.role_id.role_name == 'Super_admin'

        with transaction.atomic():
            entered_serial_numbers = []
            for item_data in items:
                item_name = item_data.get('item_name')
                units = item_data.get('units')
                quantity = item_data.get('quantity')
                discount = item_data.get('discount')[0] if isinstance(item_data.get('discount'), tuple) else item_data.get('discount')
                igst = item_data.get('igst')[0] if isinstance(item_data.get('igst'), tuple) else item_data.get('igst')
                cgst = item_data.get('cgst')[0] if isinstance(item_data.get('cgst'), tuple) else item_data.get('cgst')
                sgst = item_data.get('sgst')[0] if isinstance(item_data.get('sgst'), tuple) else item_data.get('sgst')
                item_total_price = round(quantity * item_data.get('price'), 2)
                discount_amount = round((discount / 100) * item_total_price, 2)
                user_id = get_object_or_404(CustomUser, id=customer_id)


                serial_numbers = item_data.get('serial_numbers', [])
                entered_serial_numbers.extend(serial_numbers)

                # Check if quantity and serial numbers are equal
                if quantity != len(serial_numbers):
                    return Response(
                        {'message': f"Quantity and the number of serial numbers must be equal in each drone entry"},
                        status=status.HTTP_400_BAD_REQUEST)

                # Check if serial numbers are unique within each drone entry
                if len(set(serial_numbers)) != len(serial_numbers):
                    return Response({'message': f"Serial numbers must be unique within each drone entry"},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Check if serial numbers are unique across all drone entries
                if any(serial_number in all_serial_numbers for serial_number in serial_numbers):
                    return Response({'message': f"Serial numbers must be unique across all drone entries"},
                                    status=status.HTTP_400_BAD_REQUEST)

                all_serial_numbers.update(serial_numbers)
                item_total_price = round((quantity) * (item_data.get('price')), 2)

                custom_item_details.append({
                    'item_name': item_name,
                    'quantity': quantity,
                    'price': item_data.get('price'),
                    'serial_numbers': serial_numbers,
                    'hsn_number': item_data.get('hsn_number'),
                    'item_total_price': item_total_price,
                    'discount':discount,
                    'igst':igst,
                    'cgst':cgst,
                    'sgst':sgst,
                    'units':units,
                    'created_datetime': [timezone.now().isoformat()],
                    'updated_datetime': [timezone.now().isoformat()],
                    'discount_amount': round(discount_amount, 2),
                'price_after_discount': round(item_total_price - discount_amount, 2),
                'igst_percentage': round((igst / 100) * (item_total_price - discount_amount), 2),
                'cgst_percentage': round((cgst / 100) * (item_total_price - discount_amount), 2),
                'sgst_percentage': round((sgst / 100) * (item_total_price - discount_amount), 2),
                'total': round(
                    (item_total_price - discount_amount) +
                    (igst / 100) * (item_total_price - discount_amount) +
                    (cgst / 100) * (item_total_price - discount_amount) +
                    (sgst / 100) * (item_total_price - discount_amount),
                    2
                )
            })

                items_data.append({
                    'item_name': item_name,
                    'price': item_data.get('price'),
                    'serial_numbers': serial_numbers,
                    'hsn_number': item_data.get('hsn_number'),
                    'item_total_price': item_total_price,
                    'discount': discount,
                    'igst': igst,
                    'cgst': cgst,
                    'sgst': sgst,
                    'units':units,
                    'created_datetime': [timezone.now().isoformat()],
                    'updated_datetime': [timezone.now().isoformat()],
                    'discount_amount': round(discount_amount, 2),
                'price_after_discount': round(item_total_price - discount_amount, 2),
                'igst_percentage': round((igst / 100) * (item_total_price - discount_amount), 2),
                'cgst_percentage': round((cgst / 100) * (item_total_price - discount_amount), 2),
                'sgst_percentage': round((sgst / 100) * (item_total_price - discount_amount), 2),
                'total': round(
                    (item_total_price - discount_amount) +
                    (igst / 100) * (item_total_price - discount_amount) +
                    (cgst / 100) * (item_total_price - discount_amount) +
                    (sgst / 100) * (item_total_price - discount_amount),
                    2
                )
            })

            duplicate_serial_numbers = []
            for entered_serial in entered_serial_numbers:
                if entered_serial in all_serialnumbers:
                    duplicate_serial_numbers.append(entered_serial)

            if duplicate_serial_numbers:
                return Response({
                    'message': f"Serial numbers {', '.join(map(str, duplicate_serial_numbers))} already exist in the table"},
                    status=status.HTTP_400_BAD_REQUEST)

            if len(custom_item_details) == 0:
                return Response({'message': 'details cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

            for item_data in items:
                item_name = item_data.get('item_name')
                quantity = item_data.get('quantity')
                user_id = get_object_or_404(CustomUser, id=customer_id)

            else:
                try:
                    draft_status = InvoiceStatus.objects.get(invoice_status_name='Inprogress')
                except InvoiceStatus.DoesNotExist:
                    # If 'Draft' status does not exist, create it
                    draft_status = InvoiceStatus.objects.create(invoice_status_name='Inprogress')
                new_item = CustomInvoice.objects.create(
                    customer_type_id=get_object_or_404(CustomerCategory, id=customer_type_id),
                    customer_id=get_object_or_404(CustomUser, id=customer_id),
                    owner_id=partner_instance,
                    invoice_type_id=get_object_or_404(InvoiceType, id=invoice_type_id),
                    invoice_status=draft_status,
                )

                new_item.invoice_number = self.create_invoice_number()
                new_item.save()

                # If dronedetails is empty, return a response without creating the item
                new_item.custom_item_details = custom_item_details
                amount_to_pay = round(sum(item['total'] for item in custom_item_details), 2)
                sum_of_item_total_price = round(sum(item['item_total_price'] for item in custom_item_details), 2)
                sum_of_igst_percentage = round(sum(item['igst_percentage'] for item in custom_item_details), 2)
                sum_of_cgst_percentage = round(sum(item['cgst_percentage'] for item in custom_item_details), 2)
                sum_of_sgst_percentage = round(sum(item['sgst_percentage'] for item in custom_item_details), 2)
                sum_of_discount_amount = round(sum(item['discount_amount'] for item in custom_item_details), 2)
                sum_of_price_after_discount = round(sum(item['price_after_discount'] for item in custom_item_details),
                                                    2)

                new_item.amount_to_pay = amount_to_pay
                new_item.sum_of_item_total_price = sum_of_item_total_price
                new_item.sum_of_igst_percentage = sum_of_igst_percentage
                new_item.sum_of_cgst_percentage = sum_of_cgst_percentage
                new_item.sum_of_sgst_percentage = sum_of_sgst_percentage
                new_item.sum_of_discount_amount = sum_of_discount_amount
                new_item.sum_of_price_after_discount = sum_of_price_after_discount

                new_item.save()
                # total_amount = sum(item['total'] for item in dronedetails)
                response_data = {
                    'message': 'Items are created successfully!',
                    'item_id': new_item.id,
                    'items_data': [
                        {
                            'item_name': item_data['item_name'],
                            'price': item_data['price'],
                            'serial_numbers': item_data['serial_numbers'],
                            'hsn_number': item_data['hsn_number'],
                            'item_total_price': round(quantity * item_data.get('price'), 2),
                            'discount': item_data.get('discount'),
                            'igst': item_data.get('igst'),
                            'cgst': item_data.get('cgst'),
                            'sgst': item_data.get('sgst'),

                        } for item_data in items_data
                    ],
                    'Amount_to_pay':amount_to_pay,
                    "sum_of_item_total_price":sum_of_item_total_price,
                    "sum_of_igst_percentage": sum_of_igst_percentage,
                    "sum_of_cgst_percentage": sum_of_cgst_percentage,
                    "sum_of_sgst_percentage": sum_of_sgst_percentage,
                    "sum_of_discount_amount":sum_of_discount_amount,
                    "sum_of_price_after_discount" : sum_of_price_after_discount


                    # 'total_price': total_price,
                    # 'total_price_with_additional_percentages': total_price_with_additional_percentages
                }
                return Response(response_data, status=status.HTTP_201_CREATED)



    def get(self, request, item_id=None):
        if item_id:
            # Retrieve a specific record by ID
            add_item_instance = get_object_or_404(CustomInvoice, id=item_id)

            invoice_status = add_item_instance.invoice_status
            customer_category_instance=add_item_instance.customer_type_id
            print("--------------customer_category_instance---------",customer_category_instance)
            invoice_status_name = invoice_status.invoice_status_name if invoice_status else None
            invoice_status_id = invoice_status.id if invoice_status else None

            customer_instance = add_item_instance.customer_id
            partner_instance = add_item_instance.owner_id
            customer_category = {
                "category_id": customer_category_instance.id,
                "category_name": customer_category_instance.name
            }

            customer_details = {
                'id': customer_instance.id,
                'username': customer_instance.username,
                'email': customer_instance.email,
                'first_name': customer_instance.first_name,
                'full_name': customer_instance.get_full_name(),
                'mobile_number': customer_instance.mobile_number,
                'address': customer_instance.address,
                'pin_code': customer_instance.pin_code,
                'pan_number': customer_instance.pan_number,
                'profile_pic': customer_instance.profile_pic.url if customer_instance.profile_pic else None,
                'company_name': customer_instance.company_name,
                'company_email': customer_instance.company_email,
                'company_address': customer_instance.company_address,
                'shipping_address': customer_instance.shipping_address,
                'billing_address': customer_instance.billing_address,
                'company_phn_number': customer_instance.company_phn_number,
                'company_gst_num': customer_instance.company_gst_num,
                'company_cin_num': customer_instance.company_cin_num,
                'company_logo': customer_instance.company_logo.url if customer_instance.company_logo else None,
                'role_id': customer_instance.role_id.id,
                'created_date_time': customer_instance.created_date_time,
                'updated_date_time': customer_instance.updated_date_time,
                'status': customer_instance.status,
                'location': customer_instance.location,
                'reason': customer_instance.reason,
                'partner_initial_update': customer_instance.partner_initial_update,
                'gst_number': customer_instance.gst_number,
                'category': customer_instance.category.id if customer_instance.category else None,
                'date_of_birth': customer_instance.date_of_birth,
                'gender': customer_instance.gender,
                'created_by': customer_instance.created_by.id if customer_instance.created_by else None,
                'invoice': customer_instance.invoice.id if customer_instance.invoice else None,
                'shipping_pincode': customer_instance.shipping_pincode,
                'billing_pincode': customer_instance.billing_pincode,
                # 'state_name': customer_instance.state_name,
                # 'state_code': customer_instance.state_code,
                'shipping_state': customer_instance.shipping_state,
                'shipping_state_code': customer_instance.shipping_state_code,
                'shipping_state_city': customer_instance.shipping_state_city,
                'shipping_state_country': customer_instance.shipping_state_country,
                'billing_state': customer_instance.billing_state,
                'billing_state_code': customer_instance.billing_state_code,
                'billing_state_city': customer_instance.billing_state_city,
                'billing_state_country': customer_instance.billing_state_country,

            }

            partner_details = {
                'id': partner_instance.id,
                'username': partner_instance.username,
                'email': partner_instance.email,
                'first_name': partner_instance.first_name,
                'full_name': partner_instance.get_full_name(),
                'mobile_number': partner_instance.mobile_number,
                'address': partner_instance.address,
                'pin_code': partner_instance.pin_code,
                'pan_number': partner_instance.pan_number,
                'profile_pic': partner_instance.profile_pic.url if partner_instance.profile_pic else None,
                'company_name': partner_instance.company_name,
                'company_email': partner_instance.company_email,
                'company_address': partner_instance.company_address,
                'shipping_address': partner_instance.shipping_address,
                'billing_address': partner_instance.billing_address,
                'company_phn_number': partner_instance.company_phn_number,
                'company_gst_num': partner_instance.company_gst_num,
                'company_cin_num': partner_instance.company_cin_num,
                'company_logo': partner_instance.company_logo.url if partner_instance.company_logo else None,
                'role_id': partner_instance.role_id.id,
                'created_date_time': partner_instance.created_date_time,
                'updated_date_time': partner_instance.updated_date_time,
                'status': partner_instance.status,
                'location': partner_instance.location,
                'reason': partner_instance.reason,
                'partner_initial_update': partner_instance.partner_initial_update,
                'gst_number': partner_instance.gst_number,
                'category': partner_instance.category.id if partner_instance.category else None,
                'date_of_birth': partner_instance.date_of_birth,
                'gender': partner_instance.gender,
                'created_by': partner_instance.created_by.id if partner_instance.created_by else None,
                'invoice': partner_instance.invoice.id if partner_instance.invoice else None,
                'shipping_pincode': partner_instance.shipping_pincode,
                'billing_pincode': partner_instance.billing_pincode,
                # 'state_name': partner_instance.state_name,
                # 'state_code': partner_instance.state_code,
                'shipping_state': partner_instance.shipping_state,
                'shipping_state_code': partner_instance.shipping_state_code,
                'shipping_state_city': partner_instance.shipping_state_city,
                'shipping_state_country': partner_instance.shipping_state_country,
                'billing_state': partner_instance.billing_state,
                'billing_state_code': partner_instance.billing_state_code,
                'billing_state_city': partner_instance.billing_state_city,
                'billing_state_country': partner_instance.billing_state_country,
            }

            invoice_type_details = {
                'id': add_item_instance.invoice_type_id.id,
                'name': add_item_instance.invoice_type_id.invoice_type_name,
            }

            custom_item_details = add_item_instance.custom_item_details or []

            drone_info_list = []

            if custom_item_details:
                for drone_detail in custom_item_details:
                    item_name = drone_detail["item_name"]
                    quantity = drone_detail["quantity"]
                    price = drone_detail["price"]
                    units = drone_detail.get("units")
                    serial_numbers = drone_detail.get("serial_numbers", [])
                    hsn_number = drone_detail["hsn_number"]
                    created_datetime = drone_detail.get("created_datetime", None)
                    updated_datetime = drone_detail.get("updated_datetime", None)
                    item_total_price = drone_detail.get("item_total_price", 0)
                    discount = drone_detail.get("discount", 0)
                    igst = drone_detail.get("igst", 0)
                    cgst = drone_detail.get("cgst", 0)
                    sgst = drone_detail.get("sgst", 0)
                    discount_amount = drone_detail.get("discount_amount", 0)
                    price_after_discount = drone_detail.get("price_after_discount", 0)
                    igst_percentage = drone_detail.get("igst_percentage", 0)
                    cgst_percentage = drone_detail.get("cgst_percentage", 0)
                    sgst_percentage = drone_detail.get("sgst_percentage", 0)
                    total = drone_detail.get("total", 0)

                        # drone = Drone.objects.get(id=drone_id)
                        # drone_ownership = DroneOwnership.objects.filter(user=partner_instance, drone=drone_id).first()
                        # remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                    drone_info = {
                        "item_name":item_name,
                        "quantity": quantity,
                        "price": price,
                        "units":units,
                        "serial_numbers": serial_numbers,
                        "hsn_number": hsn_number,
                        "item_total_price": item_total_price,
                        "discount" :discount,
                        "igst" : igst,
                        "cgst" : cgst,
                        "sgst" : sgst,
                        "discount_amount" : discount_amount,
                        "price_after_discount" : price_after_discount,
                        "igst_percentage" : igst_percentage,
                        "cgst_percentage" : cgst_percentage,
                        "sgst_percentage" : sgst_percentage,
                        "total" :total,
                        "created_datetime":created_datetime,
                        "updated_datetime":updated_datetime,

                    }
                    drone_info_list.append(drone_info)


            response_data = {
                'id': add_item_instance.id,
                'created_date_time': add_item_instance.created_date_time,
                'updated_date_time': add_item_instance.updated_date_time,
                'customer_details': customer_details,
                'customer_category':customer_category,
                'owner_details': partner_details,
                'invoice_type_details': invoice_type_details,
                'itemdetails': drone_info_list,
                "invoice_number": add_item_instance.invoice_number,
                'signature_url': add_item_instance.signature.url if add_item_instance.signature else None,
                'invoice_status': invoice_status_name,
                'invoice_status_id': invoice_status_id,
                'amount_to_pay' : add_item_instance.amount_to_pay,
                'sum_of_item_total_price' : add_item_instance.sum_of_item_total_price,
                'sum_of_igst_percentage' : add_item_instance.sum_of_igst_percentage,
                'sum_of_cgst_percentage' : add_item_instance.sum_of_cgst_percentage,
                'sum_of_sgst_percentage' : add_item_instance.sum_of_sgst_percentage,
                'sum_of_discount_amount' : add_item_instance.sum_of_discount_amount,
                'sum_of_price_after_discount': add_item_instance.sum_of_price_after_discount,

            }

        else:
            # Retrieve all records
            all_add_items = CustomInvoice.objects.all()
            records_list = []

            for add_item_instance in all_add_items:
                customer_instance = add_item_instance.customer_id
                partner_instance = add_item_instance.owner_id
                customer_category_instance=add_item_instance.customer_type_id
                print("--------------customer_category_instance000000000000000000000000000000---------",customer_category_instance)

                invoice_status = add_item_instance.invoice_status
                invoice_status_name = invoice_status.invoice_status_name if invoice_status else None
                invoice_status_id = invoice_status.id if invoice_status else None

                customer_category = {
                    "category_id": customer_category_instance.id,
                    "category_name": customer_category_instance.name
                }
                customer_details = {
                    'id': customer_instance.id,
                    'username': customer_instance.username,
                    'email': customer_instance.email,
                    'first_name': customer_instance.first_name,
                    'full_name': customer_instance.get_full_name(),
                    'mobile_number': customer_instance.mobile_number,
                    'address': customer_instance.address,
                    'pin_code': customer_instance.pin_code,
                    'pan_number': customer_instance.pan_number,
                    'profile_pic': customer_instance.profile_pic.url if customer_instance.profile_pic else None,
                    'company_name': customer_instance.company_name,
                    'company_email': customer_instance.company_email,
                    'company_address': customer_instance.company_address,
                    'shipping_address': customer_instance.shipping_address,
                    'billing_address': customer_instance.billing_address,
                    'company_phn_number': customer_instance.company_phn_number,
                    'company_gst_num': customer_instance.company_gst_num,
                    'company_cin_num': customer_instance.company_cin_num,
                    'company_logo': customer_instance.company_logo.url if customer_instance.company_logo else None,
                    'role_id': customer_instance.role_id.id,
                    'created_date_time': customer_instance.created_date_time,
                    'updated_date_time': customer_instance.updated_date_time,
                    'status': customer_instance.status,
                    'location': customer_instance.location,
                    'reason': customer_instance.reason,
                    'partner_initial_update': customer_instance.partner_initial_update,
                    'gst_number': customer_instance.gst_number,
                    'category': customer_instance.category.id if customer_instance.category else None,
                    'date_of_birth': customer_instance.date_of_birth,
                    'gender': customer_instance.gender,
                    'created_by': customer_instance.created_by.id if customer_instance.created_by else None,
                    'invoice': customer_instance.invoice.id if customer_instance.invoice else None,
                    'shipping_pincode': customer_instance.shipping_pincode,
                    'billing_pincode': customer_instance.billing_pincode,
                    # 'state_name': customer_instance.state_name,
                    # 'state_code': customer_instance.state_code,
                    'shipping_state': customer_instance.shipping_state,
                    'shipping_state_code': customer_instance.shipping_state_code,
                    'shipping_state_city': customer_instance.shipping_state_city,
                    'shipping_state_country': customer_instance.shipping_state_country,
                    'billing_state': customer_instance.billing_state,
                    'billing_state_code': customer_instance.billing_state_code,
                    'billing_state_city': customer_instance.billing_state_city,
                    'billing_state_country': customer_instance.billing_state_country,
                }

                partner_details = {
                    'id': partner_instance.id,
                    'username': partner_instance.username,
                    'email': partner_instance.email,
                    'first_name': partner_instance.first_name,
                    'full_name': partner_instance.get_full_name(),
                    'mobile_number': partner_instance.mobile_number,
                    'address': partner_instance.address,
                    'pin_code': partner_instance.pin_code,
                    'pan_number': partner_instance.pan_number,
                    'profile_pic': partner_instance.profile_pic.url if partner_instance.profile_pic else None,
                    'company_name': partner_instance.company_name,
                    'company_email': partner_instance.company_email,
                    'company_address': partner_instance.company_address,
                    'shipping_address': partner_instance.shipping_address,
                    'billing_address': partner_instance.billing_address,
                    'company_phn_number': partner_instance.company_phn_number,
                    'company_gst_num': partner_instance.company_gst_num,
                    'company_cin_num': partner_instance.company_cin_num,
                    'company_logo': partner_instance.company_logo.url if partner_instance.company_logo else None,
                    'role_id': partner_instance.role_id.id,
                    'created_date_time': partner_instance.created_date_time,
                    'updated_date_time': partner_instance.updated_date_time,
                    'status': partner_instance.status,
                    'location': partner_instance.location,
                    'reason': partner_instance.reason,
                    'partner_initial_update': partner_instance.partner_initial_update,
                    'gst_number': partner_instance.gst_number,
                    'category': partner_instance.category.id if partner_instance.category else None,
                    'date_of_birth': partner_instance.date_of_birth,
                    'gender': partner_instance.gender,
                    'created_by': partner_instance.created_by.id if partner_instance.created_by else None,
                    'invoice': partner_instance.invoice.id if partner_instance.invoice else None,
                    'shipping_pincode': partner_instance.shipping_pincode,
                    'billing_pincode': partner_instance.billing_pincode,
                    # 'state_name': partner_instance.state_name,
                    # 'state_code': partner_instance.state_code,
                    'shipping_state': partner_instance.shipping_state,
                    'shipping_state_code': partner_instance.shipping_state_code,
                    'shipping_state_city': partner_instance.shipping_state_city,
                    'shipping_state_country': partner_instance.shipping_state_country,
                    'billing_state': partner_instance.billing_state,
                    'billing_state_code': partner_instance.billing_state_code,
                    'billing_state_city': partner_instance.billing_state_city,
                    'billing_state_country': partner_instance.billing_state_country,
                }

                invoice_type_details = {
                    'id': add_item_instance.invoice_type_id.id,
                    'invoice_type_name': add_item_instance.invoice_type_id.invoice_type_name,
                }

                custom_item_details = add_item_instance.custom_item_details or []

                drone_info_list = []

                if custom_item_details:
                    for drone_detail in custom_item_details:
                        item_name = drone_detail["item_name"]
                        quantity = drone_detail["quantity"]
                        price = drone_detail["price"]
                        units = drone_detail.get("units")
                        serial_numbers = drone_detail.get("serial_numbers", [])
                        hsn_number = drone_detail["hsn_number"]
                        created_datetime = drone_detail.get("created_datetime", None)
                        updated_datetime = drone_detail.get("updated_datetime", None)
                        item_total_price = drone_detail.get("item_total_price", 0)
                        discount = drone_detail.get("discount", 0)
                        igst = drone_detail.get("igst", 0)
                        cgst = drone_detail.get("cgst", 0)
                        sgst = drone_detail.get("sgst", 0)
                        discount_amount = drone_detail.get("discount_amount", 0)
                        price_after_discount = drone_detail.get("price_after_discount", 0)
                        igst_percentage = drone_detail.get("igst_percentage", 0)
                        cgst_percentage = drone_detail.get("cgst_percentage", 0)
                        sgst_percentage = drone_detail.get("sgst_percentage", 0)
                        total = drone_detail.get("total", 0)

                        # try:
                        #     drone = Drone.objects.get(id=drone_id)
                        #     drone_ownership = DroneOwnership.objects.filter(user=partner_instance,
                        #                                                     drone=drone_id).first()
                        #     remaining_quantity = drone_ownership.quantity if drone_ownership else 0
                        drone_info = {
                            "item_name":item_name,
                            "quantity": quantity,
                            "price": price,
                            "units":units,
                            "serial_numbers": serial_numbers,
                            "hsn_number": hsn_number,
                            "item_total_price": item_total_price,
                            "discount": discount,
                            "igst": igst,
                            "cgst": cgst,
                            "sgst": sgst,
                            "discount_amount": discount_amount,
                            "price_after_discount": price_after_discount,
                            "igst_percentage": igst_percentage,
                            "cgst_percentage": cgst_percentage,
                            "sgst_percentage": sgst_percentage,
                            "total": total,
                            "created_datetime":created_datetime,
                        "updated_datetime" :updated_datetime,
                        }
                        drone_info_list.append(drone_info)
                        # except Drone.DoesNotExist:
                        #     pass

                record_details = {
                    'id': add_item_instance.id,
                    'created_date_time': add_item_instance.created_date_time,
                    'updated_date_time': add_item_instance.updated_date_time,
                    'customer_details': customer_details,
                    'customer_category':customer_category,
                    'owner_details': partner_details,
                    'invoice_type_details': invoice_type_details,
                    'itemdetails': drone_info_list,
                    'signature_url': add_item_instance.signature.url if add_item_instance.signature else None,
                    'invoice_status': invoice_status_name,
                    'invoice_status_id': invoice_status_id,
                    'amount_to_pay': add_item_instance.amount_to_pay,
                    'sum_of_item_total_price': add_item_instance.sum_of_item_total_price,
                    'sum_of_igst_percentage': add_item_instance.sum_of_igst_percentage,
                    'sum_of_cgst_percentage': add_item_instance.sum_of_cgst_percentage,
                    'sum_of_sgst_percentage': add_item_instance.sum_of_sgst_percentage,
                    'sum_of_discount_amount': add_item_instance.sum_of_discount_amount,
                    'sum_of_price_after_discount': add_item_instance.sum_of_price_after_discount,

                }

                records_list.append(record_details)

            response_data = records_list

        return Response(response_data, status=status.HTTP_200_OK)


    def put(self, request, item_id):

        def check_unique_serial_numbers(new_items):
            serial_numbers_set = set()

            for entry in new_items:
                for serial_number in entry['serial_numbers']:
                    if serial_number in serial_numbers_set:
                        return False  # Duplicate serial number found
                    else:
                        serial_numbers_set.add(serial_number)

            return True

        item = get_object_or_404(CustomInvoice, id=item_id)
        data = request.data
        new_items = data.get('items', [])

        all_serial = []

        all_items_except_given_id = AddItem.objects.all().values('id', 'dronedetails')
        for item_data in all_items_except_given_id:
            for drone_detail in item_data['dronedetails']:
                serial_numbers = drone_detail.get('serial_numbers', [])
                all_serial.extend(serial_numbers)

        all_items_except_given_id = CustomInvoice.objects.exclude(id=item_id).values('id', 'custom_item_details')
        for item_data in all_items_except_given_id:
            for drone_detail in item_data['custom_item_details']:
                serial_numbers = drone_detail.get('serial_numbers', [])
                all_serial.extend(serial_numbers)

        print(all_serial, "aaaaaaaaaaaaa")

        if not check_unique_serial_numbers(new_items):
            return Response({'message': f"Serial numbers must be unique with all drone entry"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            pass

        with transaction.atomic():
            duplicate_serial = []
            for j in new_items:
                for serial_number in j.get('serial_numbers', []):
                    if serial_number in all_serial:
                        duplicate_serial.append(serial_number)
                if duplicate_serial:
                    error_message = f"Serial numbers {', '.join(map(repr, duplicate_serial))} already exist in other items."
                    return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

                if len(j['serial_numbers']) != j['quantity']:
                    return Response(
                        {
                            'message': f"The number of serial numbers must be equal to the quantity"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            for new_item in new_items:
                existing_item = next(
                    (item for item in item.custom_item_details if item['item_name'] == new_item['item_name']), None
                )
                if existing_item:
                    existing_item.update(new_item)

                    # Calculate additional fields for existing_item
                    existing_item['updated_datetime'] = timezone.now().isoformat()
                    existing_item["item_total_price"] = round(self.calculate_item_total_price(existing_item["price"],
                                                                                                existing_item[
                                                                                                    "quantity"]), 2)
                    existing_item["discount_amount"] = round((existing_item["discount"] / 100) * (
                            existing_item["quantity"]) * (existing_item["price"]), 2)
                    existing_item["price_after_discount"] = round((existing_item["quantity"]) * (
                            existing_item["price"]) - (existing_item["discount"] / 100) * (
                                                                         existing_item["quantity"]) * (
                                                                         existing_item["price"]), 2)
                    existing_item["igst_percentage"] = round((existing_item["igst"] / 100) * (
                            (existing_item["quantity"]) * (existing_item["price"]) - (
                            existing_item["discount"] / 100) * (
                                                                     existing_item["quantity"]) * (
                                                                     existing_item["price"])), 2)
                    existing_item["cgst_percentage"] = round((existing_item["cgst"] / 100) * (
                            (existing_item["quantity"]) * (existing_item["price"]) - (
                            existing_item["discount"] / 100) * (
                                                                     existing_item["quantity"]) * (
                                                                     existing_item["price"])), 2)
                    existing_item["sgst_percentage"] = round((existing_item["sgst"] / 100) * (
                            (existing_item["quantity"]) * (existing_item["price"]) - (
                            existing_item["discount"] / 100) * (
                                                                     existing_item["quantity"]) * (
                                                                     existing_item["price"])), 2)
                    existing_item["total"] = round(((existing_item["quantity"]) * (existing_item["price"]) - (
                            existing_item["discount"] / 100) * (
                                                         existing_item["quantity"]) * (
                                                         existing_item["price"])) + existing_item[
                                                        "igst_percentage"] + existing_item["cgst_percentage"] + \
                                                    existing_item["sgst_percentage"], 2)
                    print(all_serial, "aaaaaaaaaaaaaaaaaaa")
                else:
                    new_item_data = {
                        'item_name': new_item['item_name'],
                        'units':new_item['units'],
                        'quantity': new_item['quantity'],
                        'price': new_item['price'],
                        'serial_numbers': new_item['serial_numbers'],
                        'hsn_number': new_item['hsn_number'],
                        'discount': new_item.get('discount', 0),
                        'igst': new_item.get('igst', 0),
                        'cgst': new_item.get('cgst', 0),
                        'sgst': new_item.get('sgst', 0),
                        'updated_datetime': timezone.now().isoformat(),
                    }
                    new_item_data["item_total_price"] = round(self.calculate_item_total_price(new_item_data["price"],
                                                                                                new_item_data[
                                                                                                    "quantity"]), 2)
                    new_item_data["discount_amount"] = round((new_item_data["discount"] / 100) * (
                            new_item_data["quantity"]) * (new_item_data["price"]), 2)
                    new_item_data["price_after_discount"] = round((new_item_data["quantity"]) * (
                            new_item_data["price"]) - (new_item_data["discount"] / 100) * (
                                                                          new_item_data["quantity"]) * (
                                                                          new_item_data["price"]), 2)
                    new_item_data["igst_percentage"] = round((new_item_data["igst"] / 100) * (
                            (new_item_data["quantity"]) * (new_item_data["price"]) - (
                            new_item_data["discount"] / 100) * (
                                                                      new_item_data["quantity"]) * (
                                                                      new_item_data["price"])), 2)
                    new_item_data["cgst_percentage"] = round((new_item_data["cgst"] / 100) * (
                            (new_item_data["quantity"]) * (new_item_data["price"]) - (
                            new_item_data["discount"] / 100) * (
                                                                      new_item_data["quantity"]) * (
                                                                      new_item_data["price"])), 2)
                    new_item_data["sgst_percentage"] = round((new_item_data["sgst"] / 100) * (
                            (new_item_data["quantity"]) * (new_item_data["price"]) - (
                            new_item_data["discount"] / 100) * (
                                                                      new_item_data["quantity"]) * (
                                                                      new_item_data["price"])), 2)
                    new_item_data["total"] = round(((new_item_data["quantity"]) * (new_item_data["price"]) - (
                            new_item_data["discount"] / 100) * (
                                                        new_item_data["quantity"]) * (
                                                        new_item_data["price"])) + new_item_data[
                                                       "igst_percentage"] + new_item_data["cgst_percentage"] + \
                                                   new_item_data["sgst_percentage"], 2)

                    item.custom_item_details.append(new_item_data)

            item.amount_to_pay = round(sum(i.get("total", 0) for i in item.custom_item_details), 2)
            item.sum_of_item_total_price = round(sum(float(i.get("item_total_price", 0)) for i in item.custom_item_details), 2)
            item.sum_of_igst_percentage = round(sum(float(i.get("igst_percentage", 0)) for i in item.custom_item_details), 2)
            item.sum_of_cgst_percentage = round(sum(float(i.get("cgst_percentage", 0)) for i in item.custom_item_details), 2)
            item.sum_of_sgst_percentage = round(sum(float(i.get("sgst_percentage", 0)) for i in item.custom_item_details), 2)
            item.sum_of_discount_amount = round(sum(float(i.get("discount_amount", 0)) for i in item.custom_item_details), 2)
            item.sum_of_price_after_discount = round(sum(float(i.get("price_after_discount", 0)) for i in item.custom_item_details), 2)
            
            updated_datetime = timezone.now().isoformat()
            for i in item.custom_item_details:
                i["updated_datetime"] = [updated_datetime]            

            item.save()

            response_data = {
                'message': 'Items are updated successfully!',
                'item_id': item.id,
                'items_data': new_items
            }
            return Response(response_data, status=status.HTTP_200_OK)
    def delete(self, request, item_id):
        try:
            item_names_param = request.query_params.get('item_name', None)

            if not item_names_param:
                return Response({'error': 'Item names are required in query parameters.'},
                                status=status.HTTP_400_BAD_REQUEST)

            item_names = item_names_param.split(',')

            # Find the CustomInvoice instance based on the item_id
            item = get_object_or_404(CustomInvoice, id=item_id)

            with transaction.atomic():
                # Remove the items with the specified item_names from custom_item_details
                item.custom_item_details = [i for i in item.custom_item_details if i['item_name'] not in item_names]

                # Recalculate everything with rounding
                item.amount_to_pay = round(sum(i.get("total", 0) for i in item.custom_item_details), 2)
                item.sum_of_item_total_price = round(
                    sum(int(i.get("item_total_price", 0)) for i in item.custom_item_details), 2)
                item.sum_of_igst_percentage = round(
                    sum(int(i.get("igst_percentage", 0)) for i in item.custom_item_details), 2)
                item.sum_of_cgst_percentage = round(
                    sum(int(i.get("cgst_percentage", 0)) for i in item.custom_item_details), 2)
                item.sum_of_sgst_percentage = round(
                    sum(int(i.get("sgst_percentage", 0)) for i in item.custom_item_details), 2)
                item.sum_of_discount_amount = round(
                    sum(int(i.get("discount_amount", 0)) for i in item.custom_item_details), 2)
                item.sum_of_price_after_discount = round(
                    sum(int(i.get("price_after_discount", 0)) for i in item.custom_item_details), 2)

                # Save the updated CustomInvoice instance
                item.save()

                # Prepare response data without serializer
                response_data = {
                    'message': f'Items with item_names {item_names} deleted successfully for item_id {item_id}!',
                    'item_data': {
                        'amount_to_pay': item.amount_to_pay,
                        'sum_of_item_total_price': item.sum_of_item_total_price,
                        'sum_of_igst_percentage': item.sum_of_igst_percentage,
                        'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
                        'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
                        'sum_of_discount_amount': item.sum_of_discount_amount,
                        'sum_of_price_after_discount': item.sum_of_price_after_discount,
                        # Include other fields as needed
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            
class AddCustomInvoiceSignature(APIView):
    def post(self, request, item_id):
        item = get_object_or_404(CustomInvoice, id=item_id)

        signature_data = request.data.get('signature')


        if signature_data:
            if signature_data.startswith(('http:', 'https:')):
                # If the image is provided as a URL, convert it to base64
                # signature_data = base64.b64encode(requests.get(signature_data).content).decode('utf-8')
                media_index = signature_data.find('media/')
                if media_index != -1:
                    signature_data = signature_data[media_index + 6:]  # Length of 'media/' is 6
                    item.signature = signature_data
            else:
                format, imgstr = signature_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'signature_{uuid.uuid4()}.{ext}')
                item.signature.save(data.name, data, save=True)

        try:
            pending_status = InvoiceStatus.objects.get(invoice_status_name='Pending')
        except InvoiceStatus.DoesNotExist:
            # If 'Pending' status does not exist, create it
            pending_status = InvoiceStatus.objects.create(invoice_status_name='Pending')

        item.invoice_status = pending_status

        item.updated_date_time = timezone.now()

        item.save()

        response_data = {
            'message': ' signature is applied successfully!',
            'item_id': item.id,
            'signature_url': item.signature.url if item.signature else None
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, item_id):
        item = get_object_or_404(CustomInvoice, id=item_id)
        signature_data = request.data.get('signature')

        if signature_data:
            if signature_data.startswith(('http:', 'https:')):
                # If the image is provided as a URL, convert it to base64
                # signature_data = base64.b64encode(requests.get(signature_data).content).decode('utf-8')
                media_index = signature_data.find('media/')
                if media_index != -1:
                    signature_data = signature_data[media_index + 6:]  # Length of 'media/' is 6
                    item.signature = signature_data
            else:
                format, imgstr = signature_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'signature_{uuid.uuid4()}.{ext}')
                item.signature.save(data.name, data, save=True)
            
        item.updated_date_time = timezone.now()

        item.save()

        response_data = {
            'result': 'signature is updated successfully!',
            'item_id': item.id,

        }
        return Response(response_data, status=status.HTTP_200_OK) 
        
        

class ALLinvoiceForSuperAdmin(APIView):
    def get(self, request, *args, **kwargs):
        try:
            add_items = AddItem.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(owner_id__role_id__role_name='Super_admin',invoice_status__invoice_status_name='Completed')

            custom_invoices = CustomInvoice.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(owner_id__role_id__role_name='Super_admin',invoice_status__invoice_status_name='Completed')

            response_data = []
            for add_item in add_items:
                response_data.append(self.get_item_details(add_item))

            for custom_invoice in custom_invoices:
                response_data.append(self.get_item_details(custom_invoice))
            
            response_data.sort(key=lambda x: x['updated_date_time'], reverse=True)
            return JsonResponse(response_data, safe=False)

        except (AddItem.DoesNotExist, CustomInvoice.DoesNotExist):
            return JsonResponse({'error': 'Data not found'}, status=404)

    def get_item_details(self, item):
        customer_details = self.get_custom_user_details(item.customer_id)
        owner_details = self.get_custom_user_details(item.owner_id)
        invoice_type_details = {
            'id': item.invoice_type_id.id,
            'name': item.invoice_type_id.invoice_type_name,
        }
        customer_category = {
            "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
            "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
        }
        if hasattr(item, 'transportation_details') and item.transportation_details:
            transportation_details = True
        else:
            transportation_details = False

        item_data = {
            'id': item.id,
            'customer_details': customer_details,
            'owner_details': owner_details,
            # 'invoice_type_id': item.invoice_type_id.id,
            # 'invoice_type_name': item.invoice_type_id.invoice_type_name,
            # 'e_invoice_status': item.e_invoice_status,
            'dronedetails': item.dronedetails if hasattr(item, 'dronedetails') else [],
            "invoice_type_details": invoice_type_details,
            "e_invoice_status": item.e_invoice_status,
            "ewaybill_status":item.ewaybill_status,            
            "customer_category":customer_category,
            'custom_item_details': item.custom_item_details if hasattr(item, 'custom_item_details') else [],
            'created_date_time': item.created_date_time,
            'updated_date_time': item.updated_date_time,
            'invoice_number': item.invoice_number,
            'signature': item.signature.url if item.signature else None,
            'invoice_payload': item.invoice_payload,
            'invoice_status': item.invoice_status.invoice_status_name,
            'ewaybill_payload': item.ewaybill_payload,
            'amount_to_pay': item.amount_to_pay,
            'sum_of_item_total_price': item.sum_of_item_total_price,
            'sum_of_igst_percentage': item.sum_of_igst_percentage,
            'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
            'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
            'sum_of_discount_amount': item.sum_of_discount_amount,
            'sum_of_price_after_discount': item.sum_of_price_after_discount,
            'transportation_details':transportation_details

        }

        return item_data

    def get_custom_user_details(self, custom_user):
        if custom_user:
            return {
                'id': custom_user.id,
            'username': custom_user.username,
            'email': custom_user.email,
            'first_name': custom_user.first_name,
            'last_name': custom_user.last_name,
            'full_name': custom_user.get_full_name(),
            'mobile_number': custom_user.mobile_number,
            'address': custom_user.address,
            'pin_code': custom_user.pin_code,
            'pan_number': custom_user.pan_number,
            'profile_pic': custom_user.profile_pic.url if custom_user.profile_pic else None,
            'company_name': custom_user.company_name,
            'company_email': custom_user.company_email,
            'company_address': custom_user.company_address,
            'shipping_address': custom_user.shipping_address,
            'billing_address': custom_user.billing_address,
            'company_phn_number': custom_user.company_phn_number,
            'company_gst_num': custom_user.company_gst_num,
            'company_cin_num': custom_user.company_cin_num,
            'company_logo': custom_user.company_logo.url if custom_user.company_logo else None,
            'role_id': custom_user.role_id.id,
            'created_date_time': custom_user.created_date_time,
            'updated_date_time': custom_user.updated_date_time,
            'status': custom_user.status,
            'location': custom_user.location,
            'reason': custom_user.reason,
            'partner_initial_update': custom_user.partner_initial_update,
            'gst_number': custom_user.gst_number,
            'category': custom_user.category.id if custom_user.category else None,
            'date_of_birth': custom_user.date_of_birth,
            'gender': custom_user.gender,
            'created_by': custom_user.created_by.id if custom_user.created_by else None,
            'invoice': custom_user.invoice.id if custom_user.invoice else None,
            'shipping_pincode': custom_user.shipping_pincode,
            'billing_pincode': custom_user.billing_pincode,
            'shipping_state': custom_user.shipping_state,
            'shipping_state_code': custom_user.shipping_state_code,
            'shipping_state_city': custom_user.shipping_state_city,
            'shipping_state_country': custom_user.shipping_state_country,
            'billing_state': custom_user.billing_state,
            'billing_state_code': custom_user.billing_state_code,
            'billing_state_city': custom_user.billing_state_city,
            'billing_state_country': custom_user.billing_state_country,
            'gstin_reg_type':custom_user.gstin_reg_type,

            }
        else:
            return {}

class ExculdeInvoiceSuperAdmin(APIView):
    def get(self, request, *args, **kwargs):
        try:
            add_items = AddItem.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(owner_id__role_id__role_name='Super_admin').exclude(invoice_status__invoice_status_name='Completed')

            custom_invoices = CustomInvoice.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(owner_id__role_id__role_name='Super_admin').exclude(invoice_status__invoice_status_name='Completed')

            response_data = []
            for add_item in add_items:
                response_data.append(self.get_item_details(add_item))

            for custom_invoice in custom_invoices:
                response_data.append(self.get_item_details(custom_invoice))
            
            response_data.sort(key=lambda x: x['updated_date_time'], reverse=True)
            return JsonResponse(response_data, safe=False)

        except (AddItem.DoesNotExist, CustomInvoice.DoesNotExist):
            return JsonResponse({'error': 'Data not found'}, status=404)

    def get_item_details(self, item):
        customer_details = self.get_custom_user_details(item.customer_id)
        owner_details = self.get_custom_user_details(item.owner_id)
        invoice_type_details = {
            'id': item.invoice_type_id.id,
            'name': item.invoice_type_id.invoice_type_name,
        }
        customer_category = {
            "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
            "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
        }

        item_data = {
            'id': item.id,
            'customer_details': customer_details,
            'owner_details': owner_details,
            # 'invoice_type_id': item.invoice_type_id.id,
            # 'invoice_type_name': item.invoice_type_id.invoice_type_name,
            # 'e_invoice_status': item.e_invoice_status,
            'dronedetails': item.dronedetails if hasattr(item, 'dronedetails') else [],
            "invoice_type_details": invoice_type_details,
            "customer_category":customer_category,
            'custom_item_details': item.custom_item_details if hasattr(item, 'custom_item_details') else [],
            'created_date_time': item.created_date_time,
            'updated_date_time': item.updated_date_time,
            'invoice_number': item.invoice_number,
            'signature': item.signature.url if item.signature else None,
            'invoice_payload': item.invoice_payload,
            'invoice_status': item.invoice_status.invoice_status_name,
            'ewaybill_payload': item.ewaybill_payload,
            'amount_to_pay': item.amount_to_pay,
            'sum_of_item_total_price': item.sum_of_item_total_price,
            'sum_of_igst_percentage': item.sum_of_igst_percentage,
            'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
            'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
            'sum_of_discount_amount': item.sum_of_discount_amount,
            'sum_of_price_after_discount': item.sum_of_price_after_discount,

        }

        return item_data

    def get_custom_user_details(self, custom_user):
        if custom_user:
            return {
                'id': custom_user.id,
            'username': custom_user.username,
            'email': custom_user.email,
            'first_name': custom_user.first_name,
            'last_name': custom_user.last_name,
            'full_name': custom_user.get_full_name(),
            'mobile_number': custom_user.mobile_number,
            'address': custom_user.address,
            'pin_code': custom_user.pin_code,
            'pan_number': custom_user.pan_number,
            'profile_pic': custom_user.profile_pic.url if custom_user.profile_pic else None,
            'company_name': custom_user.company_name,
            'company_email': custom_user.company_email,
            'company_address': custom_user.company_address,
            'shipping_address': custom_user.shipping_address,
            'billing_address': custom_user.billing_address,
            'company_phn_number': custom_user.company_phn_number,
            'company_gst_num': custom_user.company_gst_num,
            'company_cin_num': custom_user.company_cin_num,
            'company_logo': custom_user.company_logo.url if custom_user.company_logo else None,
            'role_id': custom_user.role_id.id,
            'created_date_time': custom_user.created_date_time,
            'updated_date_time': custom_user.updated_date_time,
            'status': custom_user.status,
            'location': custom_user.location,
            'reason': custom_user.reason,
            'partner_initial_update': custom_user.partner_initial_update,
            'gst_number': custom_user.gst_number,
            'category': custom_user.category.id if custom_user.category else None,
            'date_of_birth': custom_user.date_of_birth,
            'gender': custom_user.gender,
            'created_by': custom_user.created_by.id if custom_user.created_by else None,
            'invoice': custom_user.invoice.id if custom_user.invoice else None,
            'shipping_pincode': custom_user.shipping_pincode,
            'billing_pincode': custom_user.billing_pincode,
            'shipping_state': custom_user.shipping_state,
            'shipping_state_code': custom_user.shipping_state_code,
            'shipping_state_city': custom_user.shipping_state_city,
            'shipping_state_country': custom_user.shipping_state_country,
            'billing_state': custom_user.billing_state,
            'billing_state_code': custom_user.billing_state_code,
            'billing_state_city': custom_user.billing_state_city,
            'billing_state_country': custom_user.billing_state_country,
            'gstin_reg_type': custom_user.gstin_reg_type,
            }
        else:
            return {}
            
            
class GetByInvoiceNumber(View):
    def get(self, request, *args, **kwargs):
        try:
            invoice_number = self.kwargs.get('invoice_number')

            add_items = AddItem.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(invoice_number=invoice_number)

            custom_invoices = CustomInvoice.objects.select_related(
                'customer_id',
                'owner_id',
                'invoice_type_id',
                'invoice_status'
            ).filter(invoice_number=invoice_number)

            response_data = []

            for add_item in add_items:
                response_data = (self.get_item_details(add_item))

            for custom_invoice in custom_invoices:
                response_data = (self.get_item_details(custom_invoice))

            if response_data:
                return JsonResponse(response_data, safe=False)
            else:
                return JsonResponse({'error': 'Data not found'}, status=404)

        except (AddItem.DoesNotExist, CustomInvoice.DoesNotExist):
            return JsonResponse({'error': 'Data not found'}, status=404)

    def get_item_details(self, item):
        customer_details = self.get_custom_user_details(item.customer_id)
        owner_details = self.get_custom_user_details(item.owner_id)
        invoice_type_details = {
            'id': item.invoice_type_id.id,
            'name': item.invoice_type_id.invoice_type_name,
        }
        customer_category = {
            "category_id": item.customer_id.category.id if item.customer_id and item.customer_id.category else None,
            "category_name": item.customer_id.category.name if item.customer_id and item.customer_id.category else None,
        }

        item_data = {
            'id': item.id,
            'customer_details': customer_details,
            'owner_details': owner_details,
            'dronedetails': item.dronedetails if hasattr(item, 'dronedetails') else [],
            "invoice_type_details": invoice_type_details,
            "customer_category": customer_category,
            'custom_item_details': item.custom_item_details if hasattr(item, 'custom_item_details') else [],
            'created_date_time': item.created_date_time,
            'updated_date_time': item.updated_date_time,
            'invoice_number': item.invoice_number,
            'signature_url': item.signature.url if item.signature else None,
            'invoice_payload': item.invoice_payload,
            'invoice_status': item.invoice_status.invoice_status_name,
            'ewaybill': item.ewaybill_payload,
            'amount_to_pay': item.amount_to_pay,
            'sum_of_item_total_price': item.sum_of_item_total_price,
            'sum_of_igst_percentage': item.sum_of_igst_percentage,
            'sum_of_cgst_percentage': item.sum_of_cgst_percentage,
            'sum_of_sgst_percentage': item.sum_of_sgst_percentage,
            'sum_of_discount_amount': item.sum_of_discount_amount,
            'sum_of_price_after_discount': item.sum_of_price_after_discount,
        }
        invoice_number = self.kwargs.get('invoice_number')
        add_items = AddItem.objects.select_related(
            'customer_id',
            'owner_id',
            'invoice_type_id',
            'invoice_status'
        ).filter(invoice_number=invoice_number)

        custom_invoices = CustomInvoice.objects.select_related(
            'customer_id',
            'owner_id',
            'invoice_type_id',
            'invoice_status'
        ).filter(invoice_number=invoice_number)

        if add_items:

                    drone_details_with_info = []
                    for drone_detail in item.dronedetails:
                        drone_id = drone_detail.get('drone_id')
                        drone = Drone.objects.filter(id=drone_id).first()

                        drone_info = {
                            'drone_id': drone_id,
                            'drone_name': drone.drone_name if drone else 'Unknown Drone',
                            'drone_category': drone.drone_category.category_name if drone and drone.drone_category else 'Unknown Category',
                            'quantity': drone_detail.get('quantity'),
                            'price': drone_detail.get('price'),
                            'units':drone_detail.get('units'),
                            'serial_numbers': drone_detail.get('serial_numbers', []),
                            'hsn_number': drone_detail.get('hsn_number'),
                            'item_total_price': str(drone_detail.get('item_total_price')),
                            'remaining_quantity': drone_detail.get('remaining_quantity'),
                            'discount': drone_detail.get('discount', 0),
                            'igst': drone_detail.get('igst', 0),
                            'cgst': drone_detail.get('cgst', 0),
                            'sgst': drone_detail.get('sgst', 0),
                            'created_datetime': drone_detail.get('created_datetime', []),
                            'updated_datetime': drone_detail.get('updated_datetime', []),
                            'discount_amount': str(drone_detail.get('discount_amount', 0.0)),
                            'price_after_discount': str(drone_detail.get('price_after_discount', 0.0)),
                            'igst_percentage': str(drone_detail.get('igst_percentage', 0.0)),
                            'cgst_percentage': str(drone_detail.get('cgst_percentage', 0.0)),
                            'sgst_percentage': str(drone_detail.get('sgst_percentage', 0.0)),
                            'total': str(drone_detail.get('total', 0.0)),
                        }

                        drone_details_with_info.append(drone_info)

                    item_data['dronedetails'] = drone_details_with_info

        # elif custom_invoices:
        else:
            # return ("uuuuuuuuuuuuuuuuuuuuuuuuuuu")
            drone_details_with_info = []
            for custom_item_detail in item.custom_item_details:
                # drone_id = custom_item_detail.get('drone_id')
                # drone = Drone.objects.filter(id=drone_id).first()

                drone_info = {
                    'item_name': custom_item_detail.get('item_name'),
                    'quantity': custom_item_detail.get('quantity'),
                    'price': custom_item_detail.get('price'),
                    'units':custom_item_detail.get('units'),
                    'serial_numbers': custom_item_detail.get('serial_numbers', []),
                    'hsn_number': custom_item_detail.get('hsn_number'),
                    'item_total_price': str(custom_item_detail.get('item_total_price')),
                    'remaining_quantity': custom_item_detail.get('remaining_quantity'),
                    'discount': custom_item_detail.get('discount', 0),
                    'igst': custom_item_detail.get('igst', 0),
                    'cgst': custom_item_detail.get('cgst', 0),
                    'sgst': custom_item_detail.get('sgst', 0),
                    'created_datetime': custom_item_detail.get('created_datetime', []),
                    'updated_datetime': custom_item_detail.get('updated_datetime', []),
                    'discount_amount': str(custom_item_detail.get('discount_amount', 0.0)),
                    'price_after_discount': str(custom_item_detail.get('price_after_discount', 0.0)),
                    'igst_percentage': str(custom_item_detail.get('igst_percentage', 0.0)),
                    'cgst_percentage': str(custom_item_detail.get('cgst_percentage', 0.0)),
                    'sgst_percentage': str(custom_item_detail.get('sgst_percentage', 0.0)),
                    'total': str(custom_item_detail.get('total', 0.0)),
                }

                drone_details_with_info.append(drone_info)

            item_data['custom_item_details'] = drone_details_with_info


        # Fetch e_invoice_data
        e_invoice_data = None

        if isinstance(item, AddItem):
            e_invoice_data = EInvoice.objects.filter(invoice_number=item).values('api_response', 'data',
                                                                                 'e_waybill').first()
        elif isinstance(item, CustomInvoice):
            e_invoice_data = EInvoice.objects.filter(invoice_number_custominvoice=item).values('api_response', 'data',
                                                                                               'e_waybill').first()

        # Check if e_invoice_data is not None
        if e_invoice_data:
            # Parse JSON data if available
            api_response_data = json.loads(e_invoice_data['api_response']) if e_invoice_data['api_response'] else None

            # Convert 'data' field from string to dictionary
            data_dict = ast.literal_eval(e_invoice_data['data']) if e_invoice_data['data'] else None

            # Add EInvoice data to the item_data dictionary
            item_data['e_invoice_data'] = {
                'api_response': api_response_data,
                'data': data_dict,
            }

            # Convert 'e_waybill' field from string to dictionary
            try:
                e_waybill_dict = ast.literal_eval(e_invoice_data.get('e_waybill', '{}'))
            except ValueError:
                e_waybill_dict = {}

            # Add e_waybill outside e_invoice_data
            item_data['ewaybill'] = {
                'EwbNo': e_waybill_dict.get('EwbNo', None),
                'EwbDt': e_waybill_dict.get('EwbDt', None),
                'EwbValidTill': e_waybill_dict.get('EwbValidTill', None),
            }

        return item_data

    def get_custom_user_details(self, custom_user):
        if custom_user:
            category_name = custom_user.category.name if custom_user.category else None
            return {
                'id': custom_user.id,
                'username': custom_user.username,
                'email': custom_user.email,
                'first_name': custom_user.first_name,
                'last_name': custom_user.last_name,
                'full_name': custom_user.get_full_name(),
                'mobile_number': custom_user.mobile_number,
                'address': custom_user.address,
                'pin_code': custom_user.pin_code,
                'pan_number': custom_user.pan_number,
                'profile_pic': custom_user.profile_pic.url if custom_user.profile_pic else None,
                'company_name': custom_user.company_name,
                'company_email': custom_user.company_email,
                'company_address': custom_user.company_address,
                'shipping_address': custom_user.shipping_address,
                'billing_address': custom_user.billing_address,
                'company_phn_number': custom_user.company_phn_number,
                'company_gst_num': custom_user.company_gst_num,
                'company_cin_num': custom_user.company_cin_num,
                'company_logo': custom_user.company_logo.url if custom_user.company_logo else None,
                'role_id': custom_user.role_id.id,
                'created_date_time': custom_user.created_date_time,
                'updated_date_time': custom_user.updated_date_time,
                'status': custom_user.status,
                'location': custom_user.location,
                'reason': custom_user.reason,
                'partner_initial_update': custom_user.partner_initial_update,
                'gst_number': custom_user.gst_number,
                'category': custom_user.category.id if custom_user.category else None,
                'date_of_birth': custom_user.date_of_birth,
                'gender': custom_user.gender,
                'created_by': custom_user.created_by.id if custom_user.created_by else None,
                'invoice': custom_user.invoice.id if custom_user.invoice else None,
                'shipping_pincode': custom_user.shipping_pincode,
                'billing_pincode': custom_user.billing_pincode,
                'shipping_state': custom_user.shipping_state,
                'shipping_state_code': custom_user.shipping_state_code,
                'shipping_state_city': custom_user.shipping_state_city,
                'shipping_state_country': custom_user.shipping_state_country,
                'billing_state': custom_user.billing_state,
                'billing_state_code': custom_user.billing_state_code,
                'billing_state_city': custom_user.billing_state_city,
                'billing_state_country': custom_user.billing_state_country,
                'category_id':custom_user.category_id,
                'category_name':category_name,
                'gstin_reg_type':custom_user.gstin_reg_type,

            }
        else:
            return {}

class TransportationAPI(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user')
        invoice_number = data.get('invoice_number')
        distance = data.get('distance')
        transmode = data.get('transmode')
        transid = data.get('transid')
        transname = data.get('transname')
        transDocDt = data.get('transDocDt')
        transDocNo = data.get('transDocNo')
        vehNo = data.get('vehNo')
        vehType = data.get('vehType')

        if TransportationDetails.objects.filter(invoice_number=invoice_number).exists():
            return Response({'message': 'invoice_number is already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Assuming you have a User model and you can get the user object using user_id
            user = CustomUser.objects.get(pk=user_id)  # Adjust this based on your User model
            new_status = TransportationDetails.objects.create(
                invoice_number=invoice_number,
                user=user,
                distance=distance,
                transmode=transmode,
                transid=transid,
                transname=transname,
                transDocDt=transDocDt,
                transDocNo=transDocNo,
                vehNo=vehNo,
                vehType=vehType
            )
            return Response({'result': 'Transportation detail is created successfully!'}, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        invoice_number = request.query_params.get('invoice_number')
        user_id = request.query_params.get('id')
        if invoice_number:
            try:
                transportation_detail = TransportationDetails.objects.get(invoice_number=invoice_number)
                data = {
                    'id': transportation_detail.id,
                    'user': transportation_detail.user.id,  
                    'invoice_number': transportation_detail.invoice_number,
                    'distance': transportation_detail.distance,
                    'transmode': transportation_detail.transmode,
                    'transid': transportation_detail.transid,
                    'transname': transportation_detail.transname,
                    'transDocDt': transportation_detail.transDocDt,
                    'transDocNo': transportation_detail.transDocNo,
                    'vehNo': transportation_detail.vehNo,
                    'vehType': transportation_detail.vehType
                }
                return JsonResponse(data, status=status.HTTP_200_OK)
            except TransportationDetails.DoesNotExist:
                return JsonResponse({'message': 'Transportation detail not found'}, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            try:
                transportation_details = TransportationDetails.objects.filter(user_id=user_id)
                data = []
                for transportation_detail in transportation_details:
                    data.append({
                        'id': transportation_detail.id,
                        'user': transportation_detail.user.id,
                        'invoice_number': transportation_detail.invoice_number,
                        'distance': transportation_detail.distance,
                        'transmode': transportation_detail.transmode,
                        'transid': transportation_detail.transid,
                        'transname': transportation_detail.transname,
                        'transDocDt': transportation_detail.transDocDt,
                        'transDocNo': transportation_detail.transDocNo,
                        'vehNo': transportation_detail.vehNo,
                        'vehType': transportation_detail.vehType
                    })
                return JsonResponse(data, safe=False, status=status.HTTP_200_OK)  # Set safe=False here
            except TransportationDetails.DoesNotExist:
                return JsonResponse({'message': 'Transportation details for the user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            transportation_details = TransportationDetails.objects.all()
            data = []
            for transportation_detail in transportation_details:
                data.append({
                    'invoice_number': transportation_detail.invoice_number,
                    'distance': transportation_detail.distance,
                    'transmode': transportation_detail.transmode,
                    'transid': transportation_detail.transid,
                    'transname': transportation_detail.transname,
                    'transDocDt': transportation_detail.transDocDt,
                    'transDocNo': transportation_detail.transDocNo,
                    'vehNo': transportation_detail.vehNo,
                    'vehType': transportation_detail.vehType
                })
            return JsonResponse(data, safe=False, status=status.HTTP_200_OK)  # Set safe=False here

    def put(self, request, pk=None):
        if pk:
            data = request.data
            try:
                
                transportation_detail = TransportationDetails.objects.get(pk=pk)
                invoice_number = data.get('invoice_number')
                # invoice_number_custominvoice = data.get('invoice_number_custominvoice')
                distance = data.get('distance')
                transmode = data.get('transmode')
                transid = data.get('transid')
                transname = data.get('transname')
                transDocDt = data.get('transDocDt')
                transDocNo = data.get('transDocNo')
                vehNo = data.get('vehNo')
                vehType = data.get('vehType')

                transportation_detail.invoice_number = invoice_number
                # transportation_detail.invoice_number_custominvoice = invoice_number_custominvoice
                transportation_detail.distance = distance
                transportation_detail.transmode = transmode
                transportation_detail.transid = transid
                transportation_detail.transname = transname
                transportation_detail.transDocDt = transDocDt
                transportation_detail.transDocNo = transDocNo
                transportation_detail.vehNo = vehNo
                transportation_detail.vehType = vehType

                transportation_detail.save()

                return Response({'message': 'Transportation detail updated successfully'}, status=status.HTTP_200_OK)
            except TransportationDetails.DoesNotExist:
                return Response({'message': 'Transportation detail not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'Please provide a valid primary key (pk)'}, status=status.HTTP_400_BAD_REQUEST)


class UnitPriceListAPI(APIView):
    def post(self, request):
        data = request.data
        lable_name = data.get('lable_name')
        units = data.get('units')

        # Check if lable_name is already exists
        if UnitPriceList.objects.filter(lable_name__iexact=lable_name).exists():
            return Response({'message': 'Lable name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if units is already exists
        if UnitPriceList.objects.filter(units__iexact=units).exists():
            return Response({'message': 'Units already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # If lable_name and units are unique, create the UnitPriceList object
        unit_price_list = UnitPriceList.objects.create(
            lable_name=lable_name,
            units=units
        )

        return Response({'result': 'UnitPriceList is created successfully!'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        id = request.query_params.get('id')
        data = []
        unit_price_lists = UnitPriceList.objects.all()

        for unit_price_list in unit_price_lists:
            data.append({
                'id':unit_price_list.id,
                'lable_name': unit_price_list.lable_name,
                'units': unit_price_list.units
            })

        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No UnitPriceList found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        id = request.query_params.get('id')

        try:
            unit_price_list = UnitPriceList.objects.get(id=id)
            unit_price_list.delete()
            return Response({'message': 'UnitPriceList deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except UnitPriceList.DoesNotExist:
            return Response({'message': 'UnitPriceList does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            
            
            
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import base64


class CompanydetailsSuperAdminAPIView(APIView):
    def get_state_code(self, state_name):
        # Define a dictionary mapping state names to their codes
        state_code_mapping = {
            "Andaman and Nicobar Islands": "35",
            "Andhra Pradesh": "28",
            "Arunachal Pradesh": "12",
            "Assam": "18",
            "Bihar": "10",
            "Chandigarh": "04",
            "Chhattisgarh": "22",
            "Dadra and Nagar Haveli and Daman and Diu": "26",
            "Delhi": "07",
            "Goa": "30",
            "Gujarat": "24",
            "Haryana": "06",
            "Himachal Pradesh": "02",
            "Jharkhand": "20",
            "Karnataka": "29",
            "Kerala": "32",
            "Lakshadweep": "31",
            "Madhya Pradesh": "23",
            "Maharashtra": "27",
            "Manipur": "14",
            "Meghalaya": "17",
            "Mizoram": "15",
            "Nagaland": "13",
            "Odisha": "21",
            "Puducherry": "34",
            "Punjab": "03",
            "Rajasthan": "08",
            "Sikkim": "11",
            "Tamil Nadu": "33",
            "Telangana": "36",
            "Tripura": "16",
            "Uttar Pradesh": "09",
            "Uttarakhand": "05",
            "West Bengal": "19",
            "Jammu and Kashmir": "01",
            "Ladakh": "02",
        }

        # Retrieve the state code from the dictionary
        return state_code_mapping.get(state_name, '')

    def get_location_details(self, pin_code):
        geolocator = Nominatim(user_agent="amxcrm")
        location = geolocator.geocode(pin_code)

        if location:
            raw_data = location.raw
            print(raw_data, "Raw Data")

            display_name = raw_data.get('display_name', '')
            print(display_name, "Display Name")

            # Extracting information from display_name
            parts = display_name.split(', ')
            state = parts[-2]
            city = parts[-3]
            country = parts[-1]

            # Retrieve state code using the predefined mapping
            state_code = self.get_state_code(state)
            print(state_code, "State Code")

            return {
                'state': state,
                'state_code': state_code,
                'city': city,
                'country': country
            }

        return None

    def put(self, request, pk):

        data = request.data
        try:
            partner = CustomUser.objects.get(pk=pk)
            super_admin_role = Role.objects.filter(role_name="Super_admin").first()

            company_name = data.get('company_name')
            company_email = data.get('company_email')
            shipping_address = data.get('shipping_address')
            billing_address = data.get('billing_address')
            shipping_pincode = data.get('shipping_pincode')
            billing_pincode = data.get('billing_pincode')
            company_phn_number = data.get('company_phn_number')
            company_gst_num = data.get('company_gst_num')
            company_cin_num = data.get('company_cin_num')
            pan_number = data.get('pan_number')
            company_logo = request.FILES.get('company_logo')
            company_logo = data.get('company_logo')
            username = data.get('username')
            signature_data = data.get('user_signature')
            print('''''''''''''----------------------------------')

            partner.company_name = company_name
            partner.company_email = company_email
            partner.shipping_address = shipping_address
            partner.billing_address = billing_address
            partner.shipping_pincode = shipping_pincode
            partner.billing_pincode = billing_pincode
            partner.company_phn_number = company_phn_number
            partner.company_gst_num = company_gst_num
            partner.company_cin_num = company_cin_num
            partner.pan_number = pan_number

            shipping_location_details = self.get_location_details(shipping_pincode)
            if shipping_location_details:
                partner.shipping_state = shipping_location_details['state']
                partner.shipping_state_city = shipping_location_details['city']
                partner.shipping_state_country = shipping_location_details['country']
                partner.shipping_state_code = shipping_location_details['state_code']

            # Fetch and update billing location details
            billing_location_details = self.get_location_details(billing_pincode)
            if billing_location_details:
                partner.billing_state = billing_location_details['state']
                partner.billing_state_city = billing_location_details['city']
                partner.billing_state_country = billing_location_details['country']
                partner.billing_state_code = billing_location_details['state_code']

            if "company_logo" in request.data:
                print('00000000000000000-----------------------0000000000000000000')
                company_logo_base64 = request.data["company_logo"]
                converted_company_logo_base64 = convertBase64(company_logo_base64, 'companylogo', partner.username,
                                                              'company_logos')
                print('--------------------------------------------', converted_company_logo_base64)

                if converted_company_logo_base64:
                    converted_company_logo_base64 = converted_company_logo_base64.strip('"')

                    file_path = f"/company_logos/{partner.username}companylogo.png"
                    partner.company_logo.save(f"{partner.username}companylogo.png",
                                              ContentFile(converted_company_logo_base64), save=True)
                    partner.company_logo.name = file_path

            if signature_data:
                try:
                    format, imgstr = signature_data.split(';base64,')
                    ext = format.split('/')[-1]
                    signature_name = f'signature_{uuid.uuid4()}.{ext}'
                    data = ContentFile(base64.b64decode(imgstr), name=signature_name)
                    partner.user_signature.save(signature_name, data, save=True)
                except Exception as e:
                    print(f"Error saving signature image: {e}")

            partner.status = True
            partner.updated_date_time_company = timezone.now()
            partner.save()

            return Response({"message": "Company details for super admin is updated successfully"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
import qrcode
from weasyprint import HTML
class MyAPIView(APIView):
    def generate_qr_code(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Define the directory to save the QR code image
        save_dir = '/amx-crm/site/public/media/qrcode'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        qr_code_filename = "qr_code.png"
        qr_code_path = os.path.join(save_dir, qr_code_filename)  # Save the QR code image
        img.save(qr_code_path)

        # Adjust the path to start from '/media/qrcode'
        relative_path = os.path.relpath(qr_code_path, '/amx-crm/site/public/media')
        qr_code_url = '/media/' + relative_path

        return qr_code_url

    def get(self, request, invoice_number=None, *args, **kwargs):
        # Your HTML template path
        html_template_path = '/amx-crm/django/amx_crm/Crm_app/templates/email/pdf.html'
        base_url = 'https://amx-crm.thestorywallcafe.com'
        invoice_data = {}
        EwbNo = None  # Initialize EwbNo
        EwbDt = None  # Initialize EwbDt
        EwbValidTill = None
        qr_code_path=None

        # Check if invoice_number is provided
        if invoice_number:
            try:
                # Try to find the invoice_number in AddItem
                add_item = AddItem.objects.get(invoice_number=invoice_number)
                print(add_item, "addddddddddddddddddd")
                drone = add_item.dronedetails
                print('drone-----------------,,,,,,,,,,,,,,,,,-------------------------',drone)
                
                # Assuming `dronedetails` is a list of dictionaries
                if drone:
                    for drone_detail in drone:
                        invoice_data.update({
                            'cgst': drone_detail.get('cgst', None),
                            'igst': drone_detail.get('igst', None),
                            'sgst': drone_detail.get('sgst', None),
                            'price': drone_detail.get('price', None),
                            'total': drone_detail.get('total', None),
                            'units': drone_detail.get('units', None),
                            'discount': drone_detail.get('discount', None),
                            'drone_id': drone_detail.get('drone_id', None),
                            'quantity': drone_detail.get('quantity', None),
                            'hsn_number': drone_detail.get('hsn_number', None),
                            'serial_numbers': drone_detail.get('serial_numbers', None),
                            'cgst_percentage': drone_detail.get('cgst_percentage', None),
                            'discount_amount': drone_detail.get('discount_amount', None),
                            'igst_percentage': drone_detail.get('igst_percentage', None),
                            'sgst_percentage': drone_detail.get('sgst_percentage', None),
                            'created_datetime': drone_detail.get('created_datetime', None),
                            'item_total_price': drone_detail.get('item_total_price', None),
                            'updated_datetime': drone_detail.get('updated_datetime', None),
                            'price_after_discount': drone_detail.get('price_after_discount', None),
                            # Add other drone fields as needed
                        })
                        print('sheetal-----------------',invoice_data)

                if drone:
                    # Extracting the drone_id from the first item in the list
                    drone_id = drone[0].get('drone_id')
                    print('Drone ID:', drone_id)
                    
                    if drone_id:
                        # Query the Drone model to get the drone details using the drone_id
                        drone = Drone.objects.get(pk=drone_id)
                        
                        # Now you can access the drone name and category
                        drone_name = drone.drone_name
                        drone_category = drone.drone_category.category_name if drone.drone_category else None
                        
                        # Update your invoice_data dictionary with drone_name and drone_category
                        invoice_data.update({
                            'drone_name': drone_name,
                            'drone_category': drone_category
                        })
                        print('Updated invoice_data:', invoice_data)
                
                einvoice = add_item.einvoice_set.first()
                print('einvoice--------------------',einvoice)
                api_response = {}
                e_waybill = {}

                if einvoice:
                    if einvoice.api_response:
                        api_response = json.loads(einvoice.api_response)
                    if einvoice.e_waybill:
                        e_waybill = json.loads(einvoice.e_waybill)

                    ack_no = api_response.get('DecryptedData', {}).get('AckNo')
                    ack_dt = api_response.get('DecryptedData', {}).get('AckDt')
                    irn = api_response.get('DecryptedData', {}).get('Irn')
                    ewb_no = e_waybill.get('EwbNo')
                    ewb_dt = e_waybill.get('EwbDt')
                    ewb_valid_till = e_waybill.get('EwbValidTill')

                    api_response_str = einvoice.api_response
                    if api_response_str:
                        api_response = json.loads(api_response_str) 
                        decrypted_data = api_response.get('DecryptedData', {})
                        signed_qr_code = decrypted_data.get('SignedQRCode', '')

                        # Generate QR code
                        qr_code_path = self.generate_qr_code(signed_qr_code)

                        # Extract the URL part from the file path
                        qr_code_url = os.path.join(settings.MEDIA_URL, os.path.relpath(qr_code_path, settings.MEDIA_ROOT))

                        # Add QR code URL to invoice_data
                        invoice_data['qr_code_path'] = qr_code_url

                        # Add QR code path to invoice_data
                        invoice_data['qr_code_path'] = qr_code_path

                        e_waybill_str = einvoice.e_waybill
                        if e_waybill_str:
                            e_waybill = json.loads(e_waybill_str)
                            if e_waybill:
                                EwbNo = e_waybill.get('EwbNo')
                                EwbDt = e_waybill.get('EwbDt')
                                EwbValidTill = e_waybill.get('EwbValidTill')
                            else:
                                EwbNo = None
                                EwbDt = None
                                EwbValidTill = None


                invoice_data.update({
                        'invoice_id':add_item.id,
                        'customer_type_id': add_item.customer_type_id,
                        'customer_id': add_item.customer_id,
                        'owner_id': add_item.owner_id,
                        'invoice_type_id': add_item.invoice_type_id,
                        'e_invoice_status': add_item.e_invoice_status,
                        # 'custom_item_details': add_item.custom_item_details,
                        'created_date_time': add_item.created_date_time,
                        'updated_date_time': add_item.updated_date_time,
                        'invoice_number': add_item.invoice_number,
                        'signature': add_item.signature.url if add_item.signature else None,
                        'invoice_payload': add_item.invoice_payload,
                        'invoice_status': add_item.invoice_status,
                        'ewaybill_payload': add_item.ewaybill_payload,
                        'amount_to_pay': add_item.amount_to_pay,
                        'sum_of_item_total_price': add_item.sum_of_item_total_price,
                        'sum_of_igst_percentage': add_item.sum_of_igst_percentage,
                        'sum_of_cgst_percentage': add_item.sum_of_cgst_percentage,
                        'sum_of_sgst_percentage': add_item.sum_of_sgst_percentage,
                        'sum_of_discount_amount': add_item.sum_of_discount_amount,
                        'sum_of_price_after_discount': add_item.sum_of_price_after_discount,
                        'owner_id': add_item.owner_id.id,
                        'owner_username': add_item.owner_id.username,
                        'owner_email': add_item.owner_id.email,
                        'owner_first_name': add_item.owner_id.first_name,
                        'owner_last_name': add_item.owner_id.last_name,
                        'owner_mobile_number': add_item.owner_id.mobile_number,
                        'owner_address': add_item.owner_id.address,
                        'owner_pin_code': add_item.owner_id.pin_code,
                        'owner_pan_number': add_item.owner_id.pan_number,
                        'owner_profile_pic': add_item.owner_id.profile_pic.url if add_item.owner_id.profile_pic else None,
                        'owner_company_name': add_item.owner_id.company_name,
                        'owner_company_email': add_item.owner_id.company_email,
                        'owner_company_address': add_item.owner_id.company_address,
                        'owner_shipping_address': add_item.owner_id.shipping_address,
                        'owner_billing_address': add_item.owner_id.billing_address,
                        'owner_company_phn_number': add_item.owner_id.company_phn_number,
                        'owner_company_gst_num': add_item.owner_id.company_gst_num,
                        'owner_company_cin_num': add_item.owner_id.company_cin_num,
                        'owner_company_logo': add_item.owner_id.company_logo.url if add_item.owner_id.company_logo else None,
                        'owner_role_id': add_item.owner_id.role_id.id,
                        'owner_created_date_time': add_item.owner_id.created_date_time,
                        'owner_updated_date_time': add_item.owner_id.updated_date_time,
                        'owner_status': add_item.owner_id.status,
                        'owner_location': add_item.owner_id.location,
                        'owner_reason': add_item.owner_id.reason,
                        'owner_partner_initial_update': add_item.owner_id.partner_initial_update,
                        'owner_gst_number': add_item.owner_id.gst_number,
                        'owner_inventory_count': add_item.owner_id.inventory_count,
                        'owner_category': add_item.owner_id.category.id if add_item.owner_id.category else None,
                        'owner_date_of_birth': add_item.owner_id.date_of_birth,
                        'owner_gender': add_item.owner_id.gender,
                        'owner_created_by': add_item.owner_id.created_by.id if add_item.owner_id.created_by else None,
                        'owner_invoice': add_item.owner_id.invoice.id if add_item.owner_id.invoice else None,
                        'owner_state_name': add_item.owner_id.state_name,
                        'owner_state_code': add_item.owner_id.state_code,
                        'owner_shipping_pincode': add_item.owner_id.shipping_pincode,
                        'owner_billing_pincode': add_item.owner_id.billing_pincode,
                        'owner_shipping_state': add_item.owner_id.shipping_state,
                        'owner_shipping_state_code': add_item.owner_id.shipping_state_code,
                        'owner_shipping_state_city': add_item.owner_id.shipping_state_city,
                        'owner_shipping_state_country': add_item.owner_id.shipping_state_country,
                        'owner_billing_state': add_item.owner_id.billing_state,
                        'owner_billing_state_code': add_item.owner_id.billing_state_code,
                        'owner_billing_state_city': add_item.owner_id.billing_state_city,
                        'owner_billing_state_country': add_item.owner_id.billing_state_country,
                        'customer_id': add_item.customer_id.id,
                        'customer_username': add_item.customer_id.username,
                        'customer_email': add_item.customer_id.email,
                        'customer_first_name': add_item.customer_id.first_name,
                        'customer_last_name': add_item.customer_id.last_name,
                        'customer_mobile_number': add_item.customer_id.mobile_number,
                        'customer_address': add_item.customer_id.address,
                        'customer_pin_code': add_item.customer_id.pin_code,
                        'customer_pan_number': add_item.customer_id.pan_number,
                        'customer_profile_pic': add_item.customer_id.profile_pic.url if add_item.customer_id.profile_pic else None,
                        'customer_company_name': add_item.customer_id.company_name,
                        'customer_company_email': add_item.customer_id.company_email,
                        'customer_company_address': add_item.customer_id.company_address,
                        'customer_shipping_address': add_item.customer_id.shipping_address,
                        'customer_billing_address': add_item.customer_id.billing_address,
                        'customer_company_phn_number': add_item.customer_id.company_phn_number,
                        'customer_company_gst_num': add_item.customer_id.company_gst_num,
                        'customer_company_cin_num': add_item.customer_id.company_cin_num,
                        'customer_company_logo': add_item.customer_id.company_logo.url if add_item.customer_id.company_logo else None,
                        'customer_role_id': add_item.customer_id.role_id.id,
                        'customer_created_date_time': add_item.customer_id.created_date_time,
                        'customer_updated_date_time': add_item.customer_id.updated_date_time,
                        'customer_status': add_item.customer_id.status,
                        'customer_location': add_item.customer_id.location,
                        'customer_reason': add_item.customer_id.reason,
                        'customer_partner_initial_update': add_item.customer_id.partner_initial_update,
                        'customer_gst_number': add_item.customer_id.gst_number,
                        'customer_inventory_count': add_item.customer_id.inventory_count,
                        'customer_category': add_item.customer_id.category.id if add_item.customer_id.category else None,
                        'customer_date_of_birth': add_item.customer_id.date_of_birth,
                        'customer_gender': add_item.customer_id.gender,
                        'customer_created_by': add_item.customer_id.created_by.id if add_item.customer_id.created_by else None,
                        'customer_invoice': add_item.customer_id.invoice.id if add_item.customer_id.invoice else None,
                        'customer_state_name': add_item.customer_id.state_name,
                        'customer_state_code': add_item.customer_id.state_code,
                        'customer_shipping_pincode': add_item.customer_id.shipping_pincode,
                        'customer_billing_pincode': add_item.customer_id.billing_pincode,
                        'customer_shipping_state': add_item.customer_id.shipping_state,
                        'customer_shipping_state_code': add_item.customer_id.shipping_state_code,
                        'customer_shipping_state_city': add_item.customer_id.shipping_state_city,
                        'customer_shipping_state_country': add_item.customer_id.shipping_state_country,
                        'customer_billing_state': add_item.customer_id.billing_state,
                        'customer_billing_state_code': add_item.customer_id.billing_state_code,
                        'customer_billing_state_city': add_item.customer_id.billing_state_city,
                        'customer_billing_state_country': add_item.customer_id.billing_state_country,
                        'owner_user_signature': add_item.owner_id.user_signature.url if add_item.owner_id.user_signature else None,
                        'AckNo': api_response.get('DecryptedData', {}).get('AckNo'),
                        'AckDt': api_response.get('DecryptedData', {}).get('AckDt'),
                        'Irn': api_response.get('DecryptedData', {}).get('Irn'),
                        'qr_code_path':qr_code_path,
                        'EwbNo': EwbNo,
                        'EwbDt': EwbDt,
                        'EwbValidTill': EwbValidTill,

                })

                print('invoice_data--------------------------:', invoice_data)

                print('invoice_data--------------------------:', invoice_data)

            except AddItem.DoesNotExist:
                try:
                    custom_invoice = CustomInvoice.objects.get(invoice_number=invoice_number)
                    print(custom_invoice, "cccccccccccccccccccccccccc")
                    custom_invoice_details = custom_invoice.custom_item_details
                    print('custom_invoice_details----------------------', custom_invoice_details)
                    
                    einvoice = custom_invoice.einvoice_set.first()
                    print('einvoice--------------------', einvoice)

                    # Initialize empty dictionaries for api_response and e_waybill
                    api_response = {}
                    e_waybill = {}

                    if einvoice:
                        # Check if api_response and e_waybill are not None before loading JSON
                        if einvoice.api_response:
                            api_response = json.loads(einvoice.api_response)
                        if einvoice.e_waybill:
                            e_waybill = json.loads(einvoice.e_waybill)

                    # If found in CustomInvoice, fetch additional data
                    ack_no = api_response.get('DecryptedData', {}).get('AckNo')
                    ack_dt = api_response.get('DecryptedData', {}).get('AckDt')
                    irn = api_response.get('DecryptedData', {}).get('Irn')
                    ewb_no = e_waybill.get('EwbNo')
                    ewb_dt = e_waybill.get('EwbDt')
                    ewb_valid_till = e_waybill.get('EwbValidTill')
                    item_name = [item.get('item_name') for item in custom_invoice_details]
                    hsn_number = [item.get('hsn_number') for item in custom_invoice_details]
                    cgst_percentage = [item.get('cgst_percentage') for item in custom_invoice_details]
                    sgst_percentage = [item.get('sgst_percentage') for item in custom_invoice_details]
                    igst_percentage = [item.get('igst_percentage') for item in custom_invoice_details]
                    quantity = [item.get('quantity') for item in custom_invoice_details]
                    price = [item.get('price') for item in custom_invoice_details]
                    discount = [item.get('discount') for item in custom_invoice_details]
                    price_after_discount = [item.get('price_after_discount') for item in custom_invoice_details]

                    invoice_data = {

                        'customer_type_id': custom_invoice.customer_type_id,
                    'item_name':item_name,
                    'hsn_number':hsn_number,
                    'cgst_percentage':cgst_percentage,
                    'sgst_percentage':sgst_percentage,
                    'igst_percentage':igst_percentage,
                    'quantity':quantity,
                    'price':price,
                    'discount':discount,
                    'price_after_discount':price_after_discount,
                    'customer_id': custom_invoice.customer_id,  
                    'owner_id': custom_invoice.owner_id,
                    'invoice_type_id': custom_invoice.invoice_type_id,
                    'e_invoice_status': custom_invoice.e_invoice_status,
                    'custom_item_details': custom_invoice.custom_item_details,
                    'created_date_time': custom_invoice.created_date_time,
                    'updated_date_time': custom_invoice.updated_date_time,
                    'invoice_number': custom_invoice.invoice_number,
                    'signature': custom_invoice.signature.url if custom_invoice.signature else None,
                    'invoice_payload': custom_invoice.invoice_payload,
                    'invoice_status': custom_invoice.invoice_status,
                    'ewaybill_payload': custom_invoice.ewaybill_payload,
                    'amount_to_pay': custom_invoice.amount_to_pay,
                    'sum_of_item_total_price': custom_invoice.sum_of_item_total_price,
                    'sum_of_igst_percentage': custom_invoice.sum_of_igst_percentage,
                    'sum_of_cgst_percentage': custom_invoice.sum_of_cgst_percentage,
                    'sum_of_sgst_percentage': custom_invoice.sum_of_sgst_percentage,
                    'sum_of_discount_amount': custom_invoice.sum_of_discount_amount,
                    'sum_of_price_after_discount': custom_invoice.sum_of_price_after_discount,
                    'owner_id': custom_invoice.owner_id.id,
                    'owner_username': custom_invoice.owner_id.username,
                    'owner_email': custom_invoice.owner_id.email,
                    'owner_first_name': custom_invoice.owner_id.first_name,
                    'owner_last_name': custom_invoice.owner_id.last_name,
                    'owner_mobile_number': custom_invoice.owner_id.mobile_number,
                    'owner_address': custom_invoice.owner_id.address,
                    'owner_pin_code': custom_invoice.owner_id.pin_code,
                    'owner_pan_number': custom_invoice.owner_id.pan_number,
                    'owner_profile_pic': custom_invoice.owner_id.profile_pic.url if custom_invoice.owner_id.profile_pic else None,
                    'owner_company_name': custom_invoice.owner_id.company_name,
                    'owner_company_email': custom_invoice.owner_id.company_email,
                    'owner_company_address': custom_invoice.owner_id.company_address,
                    'owner_shipping_address': custom_invoice.owner_id.shipping_address,
                    'owner_billing_address': custom_invoice.owner_id.billing_address,
                    'owner_company_phn_number': custom_invoice.owner_id.company_phn_number,
                    'owner_company_gst_num': custom_invoice.owner_id.company_gst_num,
                    'owner_company_cin_num': custom_invoice.owner_id.company_cin_num,
                    'owner_company_logo': custom_invoice.owner_id.company_logo.url if custom_invoice.owner_id.company_logo else None,
                    'owner_role_id': custom_invoice.owner_id.role_id.id,
                    'owner_created_date_time': custom_invoice.owner_id.created_date_time,
                    'owner_updated_date_time': custom_invoice.owner_id.updated_date_time,
                    'owner_status': custom_invoice.owner_id.status,
                    'owner_location': custom_invoice.owner_id.location,
                    'owner_reason': custom_invoice.owner_id.reason,
                    'owner_partner_initial_update': custom_invoice.owner_id.partner_initial_update,
                    'owner_gst_number': custom_invoice.owner_id.gst_number,
                    'owner_inventory_count': custom_invoice.owner_id.inventory_count,
                    'owner_category': custom_invoice.owner_id.category.id if custom_invoice.owner_id.category else None,
                    'owner_date_of_birth': custom_invoice.owner_id.date_of_birth,
                    'owner_gender': custom_invoice.owner_id.gender,
                    'owner_created_by': custom_invoice.owner_id.created_by.id if custom_invoice.owner_id.created_by else None,
                    'owner_invoice': custom_invoice.owner_id.invoice.id if custom_invoice.owner_id.invoice else None,
                    'owner_state_name': custom_invoice.owner_id.state_name,
                    'owner_state_code': custom_invoice.owner_id.state_code,
                    'owner_shipping_pincode': custom_invoice.owner_id.shipping_pincode,
                    'owner_billing_pincode': custom_invoice.owner_id.billing_pincode,
                    'owner_shipping_state': custom_invoice.owner_id.shipping_state,
                    'owner_shipping_state_code': custom_invoice.owner_id.shipping_state_code,
                    'owner_shipping_state_city': custom_invoice.owner_id.shipping_state_city,
                    'owner_shipping_state_country': custom_invoice.owner_id.shipping_state_country,
                    'owner_billing_state': custom_invoice.owner_id.billing_state,
                    'owner_billing_state_code': custom_invoice.owner_id.billing_state_code,
                    'owner_billing_state_city': custom_invoice.owner_id.billing_state_city,
                    'owner_billing_state_country': custom_invoice.owner_id.billing_state_country,
                    'customer_id': custom_invoice.customer_id.id,
                    'customer_username': custom_invoice.customer_id.username,
                    'customer_email': custom_invoice.customer_id.email,
                    'customer_first_name': custom_invoice.customer_id.first_name,
                    'customer_last_name': custom_invoice.customer_id.last_name,
                    'customer_mobile_number': custom_invoice.customer_id.mobile_number,
                    'customer_address': custom_invoice.customer_id.address,
                    'customer_pin_code': custom_invoice.customer_id.pin_code,
                    'customer_pan_number': custom_invoice.customer_id.pan_number,
                    'customer_profile_pic': custom_invoice.customer_id.profile_pic.url if custom_invoice.customer_id.profile_pic else None,
                    'customer_company_name': custom_invoice.customer_id.company_name,
                    'customer_company_email': custom_invoice.customer_id.company_email,
                    'customer_company_address': custom_invoice.customer_id.company_address,
                    'customer_shipping_address': custom_invoice.customer_id.shipping_address,
                    'customer_billing_address': custom_invoice.customer_id.billing_address,
                    'customer_company_phn_number': custom_invoice.customer_id.company_phn_number,
                    'customer_company_gst_num': custom_invoice.customer_id.company_gst_num,
                    'customer_company_cin_num': custom_invoice.customer_id.company_cin_num,
                    'customer_company_logo': custom_invoice.customer_id.company_logo.url if custom_invoice.customer_id.company_logo else None,
                    'customer_role_id': custom_invoice.customer_id.role_id.id,
                    'customer_created_date_time': custom_invoice.customer_id.created_date_time,
                    'customer_updated_date_time': custom_invoice.customer_id.updated_date_time,
                    'customer_status': custom_invoice.customer_id.status,
                    'customer_location': custom_invoice.customer_id.location,
                    'customer_reason': custom_invoice.customer_id.reason,
                    'customer_partner_initial_update': custom_invoice.customer_id.partner_initial_update,
                    'customer_gst_number': custom_invoice.customer_id.gst_number,
                    'customer_inventory_count': custom_invoice.customer_id.inventory_count,
                    'customer_category': custom_invoice.customer_id.category.id if custom_invoice.customer_id.category else None,
                    'customer_date_of_birth': custom_invoice.customer_id.date_of_birth,
                    'customer_gender': custom_invoice.customer_id.gender,
                    'customer_created_by': custom_invoice.customer_id.created_by.id if custom_invoice.customer_id.created_by else None,
                    'customer_invoice': custom_invoice.customer_id.invoice.id if custom_invoice.customer_id.invoice else None,
                    'customer_state_name': custom_invoice.customer_id.state_name,
                    'customer_state_code': custom_invoice.customer_id.state_code,
                    'customer_shipping_pincode': custom_invoice.customer_id.shipping_pincode,
                    'customer_billing_pincode': custom_invoice.customer_id.billing_pincode,
                    'customer_shipping_state': custom_invoice.customer_id.shipping_state,
                    'customer_shipping_state_code': custom_invoice.customer_id.shipping_state_code,
                    'customer_shipping_state_city': custom_invoice.customer_id.shipping_state_city,
                    'customer_shipping_state_country': custom_invoice.customer_id.shipping_state_country,
                    'customer_billing_state': custom_invoice.customer_id.billing_state,
                    'customer_billing_state_code': custom_invoice.customer_id.billing_state_code,
                    'customer_billing_state_city': custom_invoice.customer_id.billing_state_city,
                    'customer_billing_state_country': custom_invoice.customer_id.billing_state_country,


                        # Include other customer details as needed
                    'owner_user_signature': custom_invoice.owner_id.user_signature.url if custom_invoice.owner_id.user_signature else None,
                    
                    'AckNo': ack_no,
                    'AckDt': ack_dt,
                    'Irn': irn,
                    'EwbNo': ewb_no,
                    'EwbDt': ewb_dt,
                    'EwbValidTill': ewb_valid_till,
                    }
                    print('invoice_data----------------------,',invoice_data)

                except CustomInvoice.DoesNotExist:
                    # If not found in CustomInvoice, raise Http404
                    raise Http404("Invoice not found for the given invoice_number")
        else:
            # If no invoice_number is provided, use default data
            invoice_data = {
                'default_data': 'This is default data',
            }

        # Render HTML content from the template with additional data
        html_content = render_to_string(html_template_path, {'invoice_data': invoice_data})

        # Generate PDF from HTML content
        pdf_file = HTML(string=html_content).write_pdf()

        # Set the Content-Disposition header to trigger download
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice_number}.pdf"'

        return response
