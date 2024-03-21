from rest_framework import serializers
from .models import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

class CustomUserSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    invoice_name = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = "__all__"

    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            return self.context['request'].build_absolute_uri(obj.profile_pic.url)
        return None

    def company_logo_url(self, obj):
        if obj.company_logo:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_invoice_name(self, obj):
        return obj.invoice.invoice_type_name if obj.invoice else None

    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            return self.context['request'].build_absolute_uri(obj.profile_pic.url)
        return None

    def company_logo_url(self, obj):
        if obj.company_logo:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None

class DroneSerializer(serializers.ModelSerializer):
    drone_category__category_name = serializers.SerializerMethodField()
    drone_category_id = serializers.SerializerMethodField()

    class Meta:
        model = Drone
        fields = "__all__"

    def get_drone_category__category_name(self, obj):
        return obj.drone_category.category_name if obj.drone_category else None
    def get_drone_category_id(self, obj):
        return obj.drone_category.id if obj.drone_category else None

class DroneCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneCategory
        fields = "__all__"

# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()
    drone_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = "__all__"

    def get_status_name(self, obj):
        return obj.order_status.status_name if obj.order_status else None
    def get_username(self, obj):
        return obj.user_id.username if obj.user_id else None
    def get_drone_name(self, obj):
        return obj.drone_id.drone_name if obj.drone_id else None
    def get_category_name(self, obj):
        return obj.drone_id.drone_category.category_name if obj.drone_id else None


class CustomerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategory
        fields = '__all__'
            
            
            
# class OrderSerializer(serializers.ModelSerializer):
#     status_name = serializers.SerializerMethodField()
#     drone_name = serializers.SerializerMethodField()
#     category_name = serializers.SerializerMethodField()
#     username = serializers.SerializerMethodField()
#     quantity = serializers.SerializerMethodField()

#     class Meta:
#         model = Order
#         fields = [
#             "id", "amount", "order_status", "order_id", "drone_id", "user_id", "created_date_time",
#             "updated_date_time", "payment_id", "razorpay_signature", "status_name", "drone_name",
#             "category_name", "username", "quantity"
#         ]

#     def get_status_name(self, obj):
#         return obj.order_status.status_name if obj.order_status else None

#     def get_username(self, obj):
#         return obj.user_id.username if obj.user_id else None

#     def get_drone_name(self, obj):
#         return obj.drone_id.drone_name if obj.drone_id else None

#     def get_category_name(self, obj):
#         return obj.drone_id.drone_category.category_name if obj.drone_id else None

#     def get_quantity(self, obj):
#         # Fetch quantity from DroneSales
#         drone_sales_entries = DroneSales.objects.filter(drone_id=obj.drone_id, user=obj.user_id)
#         drone_sales_quantity = drone_sales_entries[0].quantity if drone_sales_entries.exists() else 0

#         # Return a dictionary with both quantities
#         return {'drone_sales_quantity': drone_sales_quantity, 'order_quantity': obj.quantity}
