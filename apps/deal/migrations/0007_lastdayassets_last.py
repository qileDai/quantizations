# Generated by Django 2.2.4 on 2019-09-10 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0006_auto_20190910_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='lastdayassets',
            name='last',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=18),
        ),
    ]