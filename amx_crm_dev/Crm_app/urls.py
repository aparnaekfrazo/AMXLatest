from django.urls import path
from .views import *

urlpatterns = [
    path('roles/', RoleAPIView.as_view(), name='role-list'),
    path('roles/<int:pk>/', RoleAPIView.as_view(), name='role-detail'),
    path('partners/', PartnerAPIView.as_view(), name='partner-list'),
    path('partners/<int:pk>/', PartnerAPIView.as_view(), name='partner-detail'),
    path('changepassword/', ChangePasswordAPI.as_view(), name='changepassword'),
    path('forgotpassword/', ForgotPasswordAPIView.as_view(), name='changepassword'),
    path('resetpassword/', ResetpasswordAPI.as_view(), name='resetpassword'),
    path('partners-profile-edit-superadmin/<int:pk>/', PartnerProfileUpdateForSuperAdminAPIView.as_view(),
         name='partner-update'),
    path('partners-company-edit-superadmin/<int:pk>/', PartnerCompanyUpdateForSuperAdminAPIView.as_view(),
         name='partner-update'),

    path('partner-login/', LoginAPIView.as_view(), name='partner-login'),
    path('drone-category/', DroneCategoryAPIView.as_view(), name='drone-category-list'),
    path('drone-category/<int:pk>/', DroneCategoryAPIView.as_view(), name='drone-category-detail'),
    path('drones/', DroneAPIView.as_view(), name='drone-list'),
    path('drones/update-sales-status/', SalesStatusAPIview.as_view(), name='drone-list'),
    path('drones/<int:pk>/', DroneAPIView.as_view(), name='drone-detail'),
    path('email/', SendBulkEmail.as_view(), name='send bulk email'),

    path('company-details/<int:pk>/', CompanydetailsAPIView.as_view(), name='send '),
    path('company-details/<int:pk>/approve/', CompanydetailsAPIView.as_view(), {'action': 'approve'},
         name='approve_request'),
    path('company-details/<int:pk>/reject/', CompanydetailsAPIView.as_view(), {'action': 'reject'},
         name='reject_request'),
    path('approved/<int:id>', approveRequest),
    path('rejected/<int:id>', RejectRequest),

    path('dronesalespayment/', DroneSalesPaymentAPI.as_view(), name='dronesales'),
    path('dronesalespayment/<int:pk>', DroneSalesPaymentAPI.as_view(), name='dronesales'),
    path('partener_slot/', Partner_slotAPI.as_view(), name='partener_slot'),
    path('partener_slot/<int:pk>', Partner_slotAPI.as_view(), name='partener_slot'),
    path('paymentlink/', PaymentLinksAPI.as_view(), name='paymentlink'),
    path('paymentlink/<int:pk>', PaymentLinksAPI.as_view(), name='paymentlink'),
    path('slot_batch_range/', Slot_batch_rangeAPI.as_view(), name='slot_batch_range'),
    path('slot_batch_range/<int:pk>', Slot_batch_rangeAPI.as_view(), name='slot_batch_range'),
    path('addtocart/<int:pk>', AddToCart.as_view(), name='AddTocart'),
    path('addtocart/', AddToCart.as_view(), name='AddTocart'),
    path('dronecount/<int:pk>', DroneCountAPI.as_view(), name='dronecount'),
    path('status/', StatusAPI.as_view(), name='status'),
    path('status/<int:pk>', StatusAPI.as_view(), name='status'),
    path('paymentstatus/', PaymentStatusAPI.as_view(), name='PaymentStatus'),
    path('paymentstatus/<int:pk>', PaymentStatusAPI.as_view(), name='PaymentStatus'),
    path('create_order/', CreateOrderAPI.as_view(), name='create_order'),
    path('mydrones/', MydronesAPI.as_view(), name='mydrones'),
    path('customize/', CustomizablePriceAPIView.as_view(), name='customizing the price of order'),
    path('pay/', razorpay_payment, name='razorpay_payment'),
    path('customize/', CustomizablePriceAPIView.as_view(), name='customizing the price of order'),

    path('razorpay/<int:drone_sale_id>/', razorpay_payment, name='razorpay_payment'),
    path('pay/', razorpay_payment, name='razorpay_payment'),
    path('checkout/', checkout, name='checkout'),
    path('paymenthandler/', paymenthandler, name='paymenthandler'),
    path('track_order/', track_order, name='track_order'),
    path('track_order-status/', OrderStatusView.as_view(), name='order-status'),
    path('order-status/<int:super_admin_id>/', OrderStatusView.as_view(), name='order-status'),
    path('getdashboard/', GetdashbordAPI.as_view(), name='Get Dashboard'),
    path('getcompany_deatil/', GetCompanyDetailAPI.as_view(), name='Get company details'),
    path('get_partner_and_company_details/<int:pk>', CompanyAndPartnerDetailsAPIView.as_view(), name='Get_partner_and_company_details'),
#     path('getslaescount/', GetsalesCountAPI.as_view(), name='Get Sales Count'),
     
    path('invoice_type/', InvoiceTypeAPI.as_view(), name='invoice-type'),
    path('invoice_type/<int:pk>', InvoiceTypeAPI.as_view(), name='invoice-type'),
    path('create-customer/', CustomerCreateAPIView.as_view(), name='create-customer'),
    path('create-customer/<int:partner_id>/', CustomerCreateAPIView.as_view(), name='get customer'),
    path('categories/', CustomerCategoryAPI.as_view(), name='category-list'),
    path('categories/<int:category_id>/', CustomerCategoryAPI.as_view(), name='category-detail'),
    path('getpartnerdrone/', GetPartnerDronesAPI.as_view(), name='getdrone'),
    path('auth_token/',AuthAPIView.as_view(),name='Auth-Token'),
    path('company_details/<str:params>/',GetCompanyDetailsAPIView.as_view(),name='Company_details'),
    path('additem/',AddItemAPI.as_view(),name='Add-item'),
    path('additem/<int:item_id>/', AddItemAPI.as_view(), name='update item with id'),
    path('items/<int:item_id>/delete-drones/', AddItemAPI.as_view(), name='delete item with id'),
    path('get-item/<int:item_id>/', AddItemAPI.as_view(), name='get_item_api'),
    path('get-item/', AddItemAPI.as_view(), name='getall_item_api'),
    path('add-discount/<int:item_id>/', AddDiscountAPI.as_view(), name='add_discount_api'),
    path('create-customer-individual/', CustomerCreateIndividualAPIView.as_view(), name='create-customer'),
    path('create-customer-individual/<int:customer_id>/', CustomerCreateIndividualAPIView.as_view(), name='update,delete-customer-individual'),
    path('create-customer-orginization/', CustomerCreateOrginizationAPIView.as_view(), name='create-customer'),
    path('create-customer-orginization/<int:customer_id>/', CustomerCreateOrginizationAPIView.as_view(), name='update,delete-customer-orginization'),
    path('custom_invoice/', CustomInvoiceTypeAPI.as_view(), name='CustomInvoiceType'),
    path('custom_invoice/<int:pk>', CustomInvoiceTypeAPI.as_view(), name='CustomInvoiceTypeAPI'), 
    path('mydronesid/', MydronespartnerAPI.as_view(), name='mydrones'),   
    path('get-item/<int:user_id>/', GetItemDetailsAPI.as_view(), name='get_item_details'),
    path('items-by-partner/', PartnerAddedItems.as_view(), name='To see the items added by partner'),
    path('myapi/', MyApiView.as_view(), name='my api'),
    path('superadmin-get-all/<int:super_admin_id>/', SuperAdminGetAllView.as_view(), name='superadmin-get-all'),
    path('myinvoice-history/<int:owner_id>/', GetItemsByOwnerIdView.as_view(), name='item-list'),
    path('statecode/', StateCodeAPI.as_view(), name='State code'),
    path('invoice_status/', InvoiceStatusAPI.as_view(), name='Invoice Status'),
    path('invoice_status/<int:pk>', InvoiceStatusAPI.as_view(), name='Invoice Status'), 
    path('eway-bill/', EwayBill.as_view(), name='To generate Eway bill'),
    path('e-invoice-history/<int:owner_id>/', InvoiceHistoy.as_view(), name='invoice histoy with status as completed'),
    path('e-invoice-history/<path:invoice_number>/', InvoiceHistoy.as_view(), name='invoice_history_completed'),
    path('gstrates/', GstRateValuesAPI.as_view(), name='slot_batch_range'),
    path('gstrates/<int:pk>', GstRateValuesAPI.as_view(), name='slot_batch_range'),
    
    path('add-custom-item/', AddCustomItemAPI.as_view(), name='Add-item'),
    path('add-custom-item/<int:item_id>/', AddCustomItemAPI.as_view(), name='update custom invoice item with id'),
    path('add-signature/<int:item_id>/', AddCustomInvoiceSignature.as_view(), name='add_signature_and update _api'),
    path('admin-e-invoice-history/', ALLinvoiceForSuperAdmin.as_view(), name='combined-list with status complered for superadmin'),
    path('admin-invoice-history/', ExculdeInvoiceSuperAdmin.as_view(), name='combined-list with out completed status'),
    path('get-invoice/<path:invoice_number>/',GetByInvoiceNumber.as_view(),name = 'get invoice of both drone and custom'),
    path('tansportation_deatils/', TransportationAPI.as_view(), name='Transportation details'),
    path('tansportation_deatils/<int:pk>', TransportationAPI.as_view(), name='Transportation details'),
    path('unit_price_lists/', UnitPriceListAPI.as_view(), name='UnitPriceListAPI details'),
    path('com-admin/<int:pk>/', CompanydetailsSuperAdminAPIView.as_view(), name='updating company details of super admin'),
    path('get-pdf/<str:invoice_number>/', MyAPIView.as_view(), name='get-pdf'),
    path('filter/', FilterForSuperadmin.as_view(), name='filtering option for superadmin'),
    path('invoice/<int:user_id>/', InvoiceHistoyFilter.as_view(), name='filtering option for partner'),
        path('superadminall/<int:super_admin_id>/',SuperAdminGetAllViewwithoutpagination.as_view(),name='get all users created by superadmin'),
    path('getcustomer/<int:partner_id>/', CustomerGet.as_view(), name='get customer '),
    path('getcustomer/', CustomerGet.as_view(), name='get all customers '),
    path('batchsizes/', BatchSizeAPI.as_view(), name='batchsize-list'),
    path('batchsizes/<int:pk>/', BatchSizeAPI.as_view(), name='batchsize-detail'),
    path('batchtypes/', BatchTypeAPI.as_view(), name='batchtype_list'),
    path('batchtypes/<int:pk>/', BatchTypeAPI.as_view(), name='batchtype_detail'),
    path('slotstatuses/', SlotStatusAPI.as_view(), name='slotstatus_list'),
    path('slotstatuses/<int:pk>/', SlotStatusAPI.as_view(), name='slotstatus_detail'),
    path('slotbookingprice/', SlotBookingPriceAPI.as_view(), name='slotbookingprice_list'),
    path('slotbookingprice/<int:pk>/', SlotBookingPriceAPI.as_view(), name='slotbookingprice_detail'),
    path('all-tranning-master/', GetAllTraningMaster.as_view(), name='GetAllTraningMaster'),
    path('initiate_payment/', initiate_payment, name='initiate_payment'),
    path('handle_payment_success/', handle_payment_success, name='handle_payment_success'),
    path('slots/', SlotListView.as_view(), name='slot-list'),
    path('slots-by-date/<int:user_id>/', UserSlotList.as_view(), name='user-slot-list'),
    path('slots-with-students/<int:user_id>/', SlotsWithStudents.as_view(), name='slots_with_students'),
    path('slots-without-students/<int:user_id>/', SlotsWithoutStudents.as_view(), name='slots_without_students'),
    path('add-students/', StudentCreateAPIView.as_view(), name='Adding students to slot'),
    path('update-students/', StudentCreateAPIView.as_view(), name='update_students'),
    path('slots-students/<int:user_id>/', SlotListStudents.as_view(), name='filter and get of slots with students'),
    path('slot-by-id/<int:slot_id>/', SlotDetailsAPIView.as_view(), name='slot_details'),
    path('get-datas-to-swap/<int:slot_id>/', SlotsWithSameBatchSizeAPIView.as_view(),
         name='slots_with_same_batch_size'),
    path('swap/', SlotSwapAPIView.as_view(), name='slot-swap'),
    path('payurl/', PayUrlAPI.as_view(), name='payurl_list'),
    path('payurl/<int:pk>/', PayUrlAPI.as_view(), name='payurl_detail'),
    path('matching-slots/<int:slot_id>/', MatchingSlotsAPIView.as_view(), name='matching_slots'),
    path('move-students/', MoveStudentsAPIView.as_view(), name='move_students'),
    path('payment-link-status/', PaymentLinkStatusAPI.as_view()),
    path('payment-link-status/<int:pk>/', PaymentLinkStatusAPI.as_view()),
    path('generate-payment-links/', generate_payment_links_view, name='generate_payment_links'),
    path('payment-details/<str:order_id>/', payment_details_view, name='payment_details'),
    path('check-payment-status/<int:student_id>/', CheckPaymentStatusView.as_view(), name='check_payment_status'),
    path('filter-data/<int:user_id>/', FilterData.as_view(), name='filter_data'),
    path('getcalendar/', getcalendarAPI.as_view()),
    path('update-invoice-status/<str:invoice_number>/', UpdateInvoiceStatusView.as_view(),
         name='update-invoice-status'),
    path('getdashboard/', GetdashbordAPI.as_view(), name='Get Dashboard'),
    path('delete-invoice/<path:invoice_number>/', DeleteInvoice.as_view(), name='delete-invoice'),
    path('drone-orders-graph/', GetDroneOrdersGraph.as_view()),

]

