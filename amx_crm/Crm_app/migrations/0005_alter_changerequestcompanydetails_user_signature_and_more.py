# Generated by Django 4.2.8 on 2024-03-14 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm_app', '0004_alter_changerequestcompanydetails_user_signature_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changerequestcompanydetails',
            name='user_signature',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_signature',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
