# Generated by Django 4.2.8 on 2024-03-14 08:10

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(blank=True, max_length=255, null=True)),
                ('e_invoice_status', models.BooleanField(blank=True, default=False, null=True)),
                ('ewaybill_status', models.BooleanField(blank=True, default=False, null=True)),
                ('dronedetails', models.JSONField(blank=True, null=True)),
                ('discount', models.FloatField(blank=True, default=0, null=True)),
                ('igst', models.FloatField(blank=True, default=0, null=True)),
                ('sgst', models.FloatField(blank=True, default=0, null=True)),
                ('cgst', models.FloatField(blank=True, default=0, null=True)),
                ('utgst', models.FloatField(blank=True, default=0, null=True)),
                ('discount_amount', models.FloatField(blank=True, default=0, null=True)),
                ('total_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_price_with_additional_percentages', models.FloatField(blank=True, default=0, null=True)),
                ('igst_amount', models.FloatField(blank=True, default=0, null=True)),
                ('sgst_amount', models.FloatField(blank=True, default=0, null=True)),
                ('cgst_amount', models.FloatField(blank=True, default=0, null=True)),
                ('utgst_amount', models.FloatField(blank=True, default=0, null=True)),
                ('total_price_after_discount', models.FloatField(blank=True, default=0, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=50, null=True)),
                ('signature', models.ImageField(blank=True, null=True, upload_to='')),
                ('invoice_payload', models.JSONField(blank=True, null=True)),
                ('ewaybill_payload', models.JSONField(blank=True, null=True)),
                ('amount_to_pay', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_item_total_price', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_igst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_cgst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_sgst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_discount_amount', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_price_after_discount', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
                ('auth_token', models.CharField(max_length=100)),
                ('sek', models.CharField(max_length=100)),
                ('token_expiry', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ChangeRequestCompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('shipping_address', models.TextField(blank=True, null=True)),
                ('billing_address', models.TextField(blank=True, null=True)),
                ('company_phn_number', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('company_gst_num', models.CharField(blank=True, max_length=255, null=True)),
                ('company_cin_num', models.CharField(blank=True, max_length=255, null=True)),
                ('email_altr', models.EmailField(blank=True, max_length=255, null=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('pan_number', models.CharField(blank=True, max_length=10, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('pin_code', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_pincode', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_pincode', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_code', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_city', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_country', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_code', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_city', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_country', models.CharField(blank=True, max_length=50, null=True)),
                ('user_signature', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('e_invoice_status', models.BooleanField(blank=True, default=False, null=True)),
                ('custom_item_details', models.JSONField(blank=True, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=50, null=True)),
                ('signature', models.ImageField(blank=True, null=True, upload_to='')),
                ('invoice_payload', models.JSONField(blank=True, null=True)),
                ('ewaybill_payload', models.JSONField(blank=True, null=True)),
                ('amount_to_pay', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_item_total_price', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_igst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_cgst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_sgst_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_discount_amount', models.FloatField(blank=True, default=0, null=True)),
                ('sum_of_price_after_discount', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomizablePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=50, null=True)),
                ('email_altr', models.EmailField(blank=True, max_length=255, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('mobile_number', models.CharField(blank=True, max_length=10, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('pin_code', models.CharField(blank=True, max_length=255, null=True)),
                ('pan_number', models.CharField(blank=True, max_length=255, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('password', models.CharField(blank=True, max_length=100, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_address', models.CharField(blank=True, max_length=255, null=True)),
                ('shipping_address', models.TextField(blank=True, null=True)),
                ('billing_address', models.TextField(blank=True, null=True)),
                ('company_phn_number', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('company_gst_num', models.CharField(blank=True, max_length=255, null=True)),
                ('company_cin_num', models.CharField(blank=True, max_length=255, null=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.BooleanField(blank=True, default=False, null=True)),
                ('company_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('updated_date_time_company', models.DateTimeField(auto_now_add=True, null=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('partner_initial_update', models.BooleanField(blank=True, default=False, null=True)),
                ('gst_number', models.CharField(blank=True, max_length=255, null=True)),
                ('inventory_count', models.IntegerField(blank=True, default=0, null=True)),
                ('date_of_birth', models.DateTimeField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=50, null=True)),
                ('state_name', models.CharField(blank=True, max_length=50, null=True)),
                ('state_code', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_pincode', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_pincode', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_code', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_city', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_state_country', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_code', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_city', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state_country', models.CharField(blank=True, max_length=50, null=True)),
                ('user_signature', models.ImageField(blank=True, null=True, upload_to='')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.customercategory')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.customuser')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Drone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drone_name', models.CharField(blank=True, max_length=50, null=True)),
                ('drone_specification', models.CharField(blank=True, max_length=50, null=True)),
                ('market_price', models.CharField(blank=True, max_length=100, null=True)),
                ('our_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('hsn_number', models.CharField(blank=True, max_length=100, null=True)),
                ('igstvalue', models.CharField(blank=True, max_length=100, null=True)),
                ('sgstvalue', models.CharField(blank=True, max_length=100, null=True)),
                ('cgstvalue', models.CharField(blank=True, max_length=100, null=True)),
                ('thumbnail_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('drone_sub_images', models.JSONField(blank=True, null=True)),
                ('sales_status', models.BooleanField(blank=True, default=False, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('quantity_available', models.IntegerField(blank=True, null=True)),
                ('custom_price', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customizableprice')),
            ],
        ),
        migrations.CreateModel(
            name='DroneCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50, unique=True)),
                ('colour', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GstRateValues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gstrates', models.FloatField(blank=True, default=0, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_status_name', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_type_name', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Partner_slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_price', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment_gateways',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_gateway_price', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentLinks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_link_price', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.BooleanField(default=False)),
                ('approved', models.BooleanField(default=False)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=50, unique=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Slot_batch_range',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_slot_size', models.CharField(blank=True, max_length=50, null=True)),
                ('maximum_slot_size', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnitPriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lable_name', models.CharField(blank=True, max_length=255, null=True)),
                ('units', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransportationDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(blank=True, max_length=50, null=True)),
                ('distance', models.CharField(blank=True, max_length=50, null=True)),
                ('transmode', models.CharField(blank=True, max_length=50, null=True)),
                ('transid', models.CharField(blank=True, max_length=50, null=True)),
                ('transname', models.CharField(blank=True, max_length=50, null=True)),
                ('transDocDt', models.CharField(blank=True, max_length=50, null=True)),
                ('transDocNo', models.CharField(blank=True, max_length=50, null=True)),
                ('vehNo', models.CharField(blank=True, max_length=50, null=True)),
                ('vehType', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('order_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=255, null=True)),
                ('drone_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.drone')),
                ('order_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.status')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.role')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='EInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_response', models.TextField(blank=True, null=True)),
                ('data', models.TextField(blank=True, null=True)),
                ('e_waybill', models.TextField(blank=True, null=True)),
                ('invoice_number', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.additem')),
                ('invoice_number_custominvoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.custominvoice')),
            ],
        ),
        migrations.CreateModel(
            name='DroneSales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('checked', models.BooleanField(blank=True, default=False, null=True)),
                ('custom_price', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customizableprice')),
                ('drone_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.drone')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.role')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='DroneOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('order_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('drone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Crm_app.drone')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Crm_app.customuser')),
            ],
        ),
        migrations.AddField(
            model_name='drone',
            name='drone_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.dronecategory'),
        ),
        migrations.AddField(
            model_name='drone',
            name='units',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.unitpricelist'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.invoicetype'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='role_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.role'),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='customer_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_product_items', to='Crm_app.customuser'),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='customer_type_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customercategory'),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='invoice_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.invoicestatus'),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='invoice_type_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.invoicetype'),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='owner_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner_product_items', to='Crm_app.customuser'),
        ),
        migrations.AddField(
            model_name='additem',
            name='customer_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_items', to='Crm_app.customuser'),
        ),
        migrations.AddField(
            model_name='additem',
            name='customer_type_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.customercategory'),
        ),
        migrations.AddField(
            model_name='additem',
            name='invoice_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.invoicestatus'),
        ),
        migrations.AddField(
            model_name='additem',
            name='invoice_type_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Crm_app.invoicetype'),
        ),
        migrations.AddField(
            model_name='additem',
            name='owner_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner_items', to='Crm_app.customuser'),
        ),
    ]
