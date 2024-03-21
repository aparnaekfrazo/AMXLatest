
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.role_name



class InvoiceType(models.Model):
    invoice_type_name=models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

class CustomerCategory(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    email_altr = models.EmailField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=10,  null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pin_code = models.CharField(max_length=255, null=True, blank=True)
    pan_number = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    company_phn_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    company_gst_num = models.CharField(max_length=255, null=True, blank=True)
    company_cin_num = models.CharField(max_length=255, null=True, blank=True)
    company_logo = models.ImageField(null=True, blank=True)
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True,null=True)
    status = models.BooleanField(null=True, blank=True, default=False)
    company_email = models.EmailField(null=True, blank=True)
    updated_date_time_company = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time_company = models.DateTimeField(auto_now_add=True,null=True)
    location = models.TextField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    partner_initial_update = models.BooleanField(null=True, blank=True, default=False)
    gst_number = models.CharField(max_length=255, null=True, blank=True)
    inventory_count = models.IntegerField(null=True,blank=True,default=0)
    category = models.ForeignKey(CustomerCategory, on_delete=models.PROTECT, null=True, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.ForeignKey(InvoiceType, on_delete=models.PROTECT, null=True, blank=True)
    state_name = models.CharField(max_length=50, null=True, blank=True)
    state_code = models.CharField(max_length=50, null=True, blank=True) 
    shipping_pincode = models.CharField(max_length=50, null=True, blank=True)
    billing_pincode = models.CharField(max_length=50, null=True, blank=True)
    shipping_state = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_code = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_city = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_country = models.CharField(max_length=50, null=True, blank=True)
    billing_state = models.CharField(max_length=50, null=True, blank=True)
    billing_state_code = models.CharField(max_length=50, null=True, blank=True)
    billing_state_city = models.CharField(max_length=50, null=True, blank=True)
    billing_state_country = models.CharField(max_length=50, null=True, blank=True)
    #user_signature = models.ImageField(upload_to='user_signatures/',blank=True, null=True)
    user_signature = models.ImageField(blank=True, null=True)
    gstin_reg_type = models.CharField(max_length=10, null=True, blank=True)




    groups = None
    user_permissions = None

    def __str__(self):
        return str(self.username)

class CustomizablePrice(models.Model):
    custom_amount = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    def _str_(self):
        return str(self.custom_amount)

class DroneCategory(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    colour = models.CharField(max_length=255, default=None,null=True,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.category_name


class UnitPriceList(models.Model):
    lable_name=models.CharField(max_length=255, null=True, blank=True)
    units=models.CharField(max_length=255, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

class Drone(models.Model):
    drone_name = models.CharField(max_length=50, null=True, blank=True)
    # drone_category = models.ForeignKey(DroneCategory, on_delete=models.SET_NULL, null=True, blank=True)
    drone_category = models.ForeignKey(DroneCategory, on_delete=models.PROTECT, null=True, blank=True)
    units = models.ForeignKey(UnitPriceList, on_delete=models.PROTECT, null=True, blank=True)
    drone_specification = models.CharField(max_length=50, null=True, blank=True)
    market_price = models.CharField(max_length=100, null=True, blank=True)
    our_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    hsn_number=models.CharField(max_length=100, null=True, blank=True)
    igstvalue = models.CharField(max_length=100, null=True, blank=True)
    sgstvalue = models.CharField(max_length=100, null=True, blank=True)
    cgstvalue = models.CharField(max_length=100, null=True, blank=True)
    thumbnail_image = models.ImageField(blank=True, null=True)
    drone_sub_images = models.JSONField(null=True, blank=True)
    sales_status = models.BooleanField(default=False, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True,null=True)
    quantity_available = models.IntegerField(null=True, blank=True)
    custom_price = models.ForeignKey(CustomizablePrice, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return self.drone_name


class Payment_gateways(models.Model):
    payment_gateway_price=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

class Partner_slot(models.Model):
    slot_price=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

class PaymentLinks(models.Model):
    payment_link_price=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

class Slot_batch_range(models.Model):
    minimum_slot_size=models.CharField(max_length=50, null=True, blank=True)
    maximum_slot_size=models.CharField(max_length=50, null=True, blank=True)
    description=models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)


class ChangeRequestCompanyDetails(models.Model):
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    company_phn_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    company_gst_num = models.CharField(max_length=255, null=True, blank=True)
    company_cin_num = models.CharField(max_length=255, null=True, blank=True)
    email_altr = models.EmailField(max_length=255, blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    status = models.BooleanField( default=False)
    approved = models.BooleanField( default=False)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    pin_code=models.CharField(max_length=50, null=True, blank=True)
    address=models.CharField(max_length=50, null=True, blank=True)
    shipping_pincode = models.CharField(max_length=50, null=True, blank=True)
    billing_pincode = models.CharField(max_length=50, null=True, blank=True)
    shipping_state = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_code = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_city = models.CharField(max_length=50, null=True, blank=True)
    shipping_state_country = models.CharField(max_length=50, null=True, blank=True)
    billing_state = models.CharField(max_length=50, null=True, blank=True)
    billing_state_code = models.CharField(max_length=50, null=True, blank=True)
    billing_state_city = models.CharField(max_length=50, null=True, blank=True)
    billing_state_country = models.CharField(max_length=50, null=True, blank=True)
    #user_signature = models.ImageField(upload_to='user_signatures/',blank=True, null=True)
    user_signature = models.ImageField(blank=True, null=True)

    #def __str__(self):
        #return self.company_name

class PaymentStatus(models.Model):
    name=models.CharField(max_length=50,null=True,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    status = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.company_name


class DroneSales(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    drone_id = models.ForeignKey(Drone, on_delete=models.PROTECT, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    custom_price = models.ForeignKey(CustomizablePrice, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    checked = models.BooleanField(null=True,blank=True,default=False)


class Status(models.Model):
    status_name = models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.status_name

class InvoiceStatus(models.Model):
    invoice_status_name = models.CharField(max_length=255, default=None,null=True,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True,null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)



class Order(models.Model): 
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    order_status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    drone_id = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True)
    quantity = models.IntegerField(null=True,blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)


class AuthToken(models.Model):
    client_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    auth_token = models.CharField(max_length=100)
    sek = models.CharField(max_length=100)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return f"Auth Token for {self.user_name}"

class AddItem(models.Model):
    customer_type_id = models.ForeignKey(CustomerCategory, on_delete=models.SET_NULL, null=True, blank=True)
    customer_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_items')
    owner_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='owner_items')
    invoice_type_id = models.ForeignKey(InvoiceType, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_status = models.ForeignKey(InvoiceStatus, on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    e_invoice_status = models.BooleanField(null=True, blank=True, default=False)
    ewaybill_status = models.BooleanField(null=True, blank=True, default=False)
    dronedetails = models.JSONField(null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    igst = models.FloatField(default=0, null=True, blank=True)
    sgst = models.FloatField(default=0, null=True, blank=True)
    cgst = models.FloatField(default=0, null=True, blank=True)
    utgst = models.FloatField(default=0, null=True, blank=True)
    discount_amount = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)
    total_price_with_additional_percentages = models.FloatField(default=0, null=True, blank=True)
    igst_amount = models.FloatField(default=0, null=True, blank=True)
    sgst_amount = models.FloatField(default=0, null=True, blank=True)
    cgst_amount = models.FloatField(default=0, null=True, blank=True)
    utgst_amount = models.FloatField(default=0, null=True, blank=True)
    total_price_after_discount = models.FloatField(default=0, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    signature = models.ImageField(blank=True, null=True)
    invoice_payload=models.JSONField(null=True, blank=True)
    invoice_status = models.ForeignKey(InvoiceStatus, on_delete=models.SET_NULL, null=True, blank=True)
    ewaybill_payload = models.JSONField(null=True, blank=True)
    amount_to_pay = models.FloatField(default=0, null=True, blank=True)
    sum_of_item_total_price = models.FloatField(default=0, null=True, blank=True)
    sum_of_igst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_cgst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_sgst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_discount_amount = models.FloatField(default=0, null=True, blank=True)
    sum_of_price_after_discount = models.FloatField(default=0, null=True, blank=True)
     
    def __str__(self):
        return self.invoice_number


class GstRateValues(models.Model):
    gstrates= models.FloatField(default=0, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    

class DroneOwnership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_id = models.CharField(max_length=255, unique=True,null=True,blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} owns {self.quantity} {self.drone.drone_name}"


class CustomInvoice(models.Model):
    customer_type_id = models.ForeignKey(CustomerCategory, on_delete=models.SET_NULL, null=True, blank=True)
    customer_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_product_items')
    owner_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='owner_product_items')
    invoice_type_id = models.ForeignKey(InvoiceType, on_delete=models.SET_NULL, null=True, blank=True)
    e_invoice_status = models.BooleanField(null=True, blank=True, default=False)
    custom_item_details = models.JSONField(null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    signature = models.ImageField(blank=True, null=True)
    invoice_payload = models.JSONField(null=True, blank=True)
    invoice_status = models.ForeignKey(InvoiceStatus, on_delete=models.SET_NULL, null=True, blank=True)
    ewaybill_payload = models.JSONField(null=True, blank=True)
    amount_to_pay = models.FloatField(default=0, null=True, blank=True)
    sum_of_item_total_price = models.FloatField(default=0, null=True, blank=True)
    sum_of_igst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_cgst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_sgst_percentage = models.FloatField(default=0, null=True, blank=True)
    sum_of_discount_amount = models.FloatField(default=0, null=True, blank=True)
    sum_of_price_after_discount = models.FloatField(default=0, null=True, blank=True)
    ewaybill_status = models.BooleanField(null=True, blank=True, default=False)
    def __str__(self):
        return self.invoice_number

class EInvoice(models.Model):
    invoice_number=models.ForeignKey(AddItem, on_delete=models.PROTECT, null=True, blank=True)
    invoice_number_custominvoice=models.ForeignKey(CustomInvoice, on_delete=models.PROTECT, null=True, blank=True)
    api_response=models.TextField(null=True, blank=True)
    data=models.TextField(null=True, blank=True)
    e_waybill=models.TextField(null=True, blank=True)



class TransportationDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True, blank=True)
    invoice_number=models.CharField(max_length=50, null=True, blank=True)
    # invoice_number_custominvoice=models.ForeignKey(CustomInvoice, on_delete=models.PROTECT, null=True, blank=True)
    distance = models.CharField(max_length=50, null=True, blank=True)
    transmode = models.CharField(max_length=50, null=True, blank=True)
    transid = models.CharField(max_length=50, null=True, blank=True)
    transname = models.CharField(max_length=50, null=True, blank=True)
    transDocDt = models.CharField(max_length=50, null=True, blank=True)
    transDocNo = models.CharField(max_length=50, null=True, blank=True)
    vehNo = models.CharField(max_length=50, null=True, blank=True)
    vehType = models.CharField(max_length=50, null=True, blank=True)
    created_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
