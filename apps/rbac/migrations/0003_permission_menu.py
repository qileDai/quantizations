# Generated by Django 2.2.3 on 2019-10-22 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0002_role_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu'),
        ),
    ]