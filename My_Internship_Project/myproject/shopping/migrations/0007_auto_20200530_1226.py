# Generated by Django 3.0.6 on 2020-05-30 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0006_auto_20200530_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='', upload_to='shop/images'),
        ),
    ]
