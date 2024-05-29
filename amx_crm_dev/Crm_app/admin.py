from django.contrib import admin
from .models import *



@admin.register(Role)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_name', 'created_date_time', 'updated_date_time']

@admin.register(CustomerCategory)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_date_time', 'updated_date_time']

@admin.register(CustomUser)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'email_altr','status', 'username', 'mobile_number', 'company_address','partner_initial_update',
                    'address', 'pin_code', 'pan_number', 'profile_pic', 'password', 'company_name', 'shipping_address','billing_address','gst_number','gender','date_of_birth',
                    'company_gst_num', 'company_cin_num', 'company_logo', 'role_id', 'created_date_time', 'updated_date_time', 'location','inventory_count','created_by','invoice']

@admin.register(DroneCategory)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name','colour','created_date_time', 'updated_date_time']

@admin.register(Drone)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'drone_name', 'drone_category', 'drone_specification','hsn_number','igstvalue','cgstvalue','sgstvalue','market_price', 'our_price', 'thumbnail_image','drone_sub_images',
                    'sales_status', 'created_date_time', 'updated_date_time', 'quantity_available']

@admin.register(Payment_gateways)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','payment_gateway_price','description','created_date_time', 'updated_date_time']

@admin.register(ChangeRequestCompanyDetails)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'company_name','created_date_time', 'updated_date_time']

@admin.register(Partner_slot)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','slot_price','description','created_date_time', 'updated_date_time']

@admin.register(PaymentLinks)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','payment_link_price','description','created_date_time', 'updated_date_time']

@admin.register(Slot_batch_range)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','minimum_slot_size','maximum_slot_size','description','created_date_time', 'updated_date_time']

@admin.register(DroneSales)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'drone_id','user','role','quantity','created_date_time', 'updated_date_time','checked','custom_price']

@admin.register(Order)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','amount','order_status','order_id','drone_id','user_id','quantity','created_date_time', 'updated_date_time','payment_id','razorpay_signature']

@admin.register(Status)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','status_name','created_date_time', 'updated_date_time']

@admin.register(PaymentStatus)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','name','created_date_time', 'updated_date_time']

@admin.register(CustomizablePrice)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','custom_amount','description','created_date_time', 'updated_date_time']

@admin.register(InvoiceType)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','invoice_type_name','created_date_time', 'updated_date_time']

@admin.register(AuthToken)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','client_id','user_name', 'auth_token','sek','token_expiry']

@admin.register(AddItem)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','customer_type_id','customer_id','owner_id','invoice_status','invoice_type_id','sum_of_discount_amount',
                    'amount_to_pay','sum_of_sgst_percentage','sum_of_igst_percentage','sum_of_cgst_percentage','ewaybill_status','transportation_details',
                    'sum_of_item_total_price','e_invoice_status','dronedetails','invoice_number','signature',
                    'created_date_time','updated_date_time','ewaybill_payload']
                    
@admin.register(EInvoice)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','api_response','invoice_number','data','e_waybill','invoice_number_custominvoice']

@admin.register(DroneOwnership)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'drone', 'quantity','order_id','created_date_time','updated_date_time']

@admin.register(InvoiceStatus)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','invoice_status_name','created_date_time', 'updated_date_time']

@admin.register(GstRateValues)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','gstrates','created_date_time','updated_date_time']

@admin.register(UnitPriceList)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','lable_name','units','created_date_time','updated_date_time']
    
@admin.register(CustomInvoice)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','customer_type_id','customer_id','owner_id','invoice_status','invoice_type_id','sum_of_discount_amount',
                    'amount_to_pay','sum_of_price_after_discount','sum_of_sgst_percentage','sum_of_igst_percentage','sum_of_cgst_percentage',
                    'sum_of_item_total_price','e_invoice_status','custom_item_details','invoice_number','signature',
                    'created_date_time','updated_date_time','ewaybill_payload']

@admin.register(TransportationDetails)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','invoice_number','distance','transmode','transid','transname',
    'transDocDt','transDocNo','vehNo',
    'vehType','created_date_time','updated_date_time']
    
@admin.register(Batchsize)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','minimum','maximum','description','batch_type','created_date_time','updated_date_time']

@admin.register(Batchtype)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','name','created_date_time','updated_date_time']

@admin.register(SlotStatus)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','slot_status','days_in_advance','created_date_time','updated_date_time']
    
@admin.register(SlotBookingPrice)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','slot_booking_price','description','created_date_time','updated_date_time']

@admin.register(SlotOrder)
class SlotOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'amount', 'order_status', 'order_id', 'user_id',
                    'created_date_time', 'updated_date_time', 'payment_id', 'razorpay_signature',
                    'batch_name', 'slot_date', 'batch_size', 'batch_type']
@admin.register(Slot)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','user_id','batch_name','slot_date','batch_size','batch_type',
                    'created_date_time','updated_date_time']

@admin.register(Student)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','slot_id','student_name','student_age','student_mobile',
                    'student_email','student_adhar','payment_url','stupayment_status',
                    'order_id','razorpay_payment_id','razorpay_signature',
                    'created_date_time','updated_date_time','testemail']

@admin.register(SlotStudentRelation)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','slot','slot_id','student','student_id','created_date_time']

    def slot_id(self, obj):
        return obj.slot.id if obj.slot else None

    def student_id(self, obj):
        return obj.student.id if obj.student else None

@admin.register(PayUrl)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','payment_link_price','batch_type','description',
                    'created_date_time','updated_date_time']

@admin.register(PaymentLinkStatus)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id','payment_status_name','created_date_time','updated_date_time']


