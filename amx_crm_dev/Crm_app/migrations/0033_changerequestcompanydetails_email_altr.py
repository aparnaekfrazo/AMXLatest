# Generated by Django 4.2.8 on 2024-02-23 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm_app', '0032_remove_transportationdetails_invoice_number_custominvoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='changerequestcompanydetails',
            name='email_altr',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
