# Generated by Django 4.2.8 on 2024-02-22 05:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Crm_app', '0029_remove_einvoice_e_waybill_payload'),
    ]

    operations = [
        migrations.AddField(
            model_name='einvoice',
            name='invoice_number_custominvoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Crm_app.custominvoice'),
        ),
    ]
