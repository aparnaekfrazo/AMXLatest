# Generated by Django 4.2.8 on 2024-03-19 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm_app', '0005_alter_changerequestcompanydetails_user_signature_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='gstin_reg_type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
