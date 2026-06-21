# Rework templates: single-entry contacts, service-only master templates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_contacttemplate_address_detail_and_more'),
    ]

    operations = [
        # ContactTemplate: convert to single-entry format
        migrations.RemoveField(
            model_name='contacttemplate',
            name='template_type',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='sender_name',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='sender_phone',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='sender_email',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='sender_address',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='sender_address_detail',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='recipient_name',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='recipient_phone',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='recipient_email',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='recipient_address',
        ),
        migrations.RemoveField(
            model_name='contacttemplate',
            name='recipient_address_detail',
        ),
        migrations.AddField(
            model_name='contacttemplate',
            name='contact_name',
            field=models.CharField(default='', max_length=255, verbose_name='Contact name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contacttemplate',
            name='contact_phone',
            field=models.CharField(default='', max_length=20, verbose_name='Contact phone'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contacttemplate',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Contact email'),
        ),
        migrations.AddField(
            model_name='contacttemplate',
            name='city',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='geo.city',
                verbose_name='City',
            ),
        ),
        migrations.AddField(
            model_name='contacttemplate',
            name='address_detail',
            field=models.CharField(blank=True, max_length=500, verbose_name='Address detail'),
        ),

        # MasterTemplate: remove route/cargo fields, keep only service + addons
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='from_city',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='to_city',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='sender_name',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='sender_phone',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='sender_email',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='sender_address_detail',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='recipient_name',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='recipient_phone',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='recipient_email',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='recipient_address_detail',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='weight',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='length',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='width',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='height',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='cargo_description',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='declared_value',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='is_fragile',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='is_dangerous',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='is_temperature_sensitive',
        ),
        migrations.RemoveField(
            model_name='deliverytemplate',
            name='total_price',
        ),
    ]
