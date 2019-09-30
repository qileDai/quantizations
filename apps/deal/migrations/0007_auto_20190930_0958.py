# Generated by Django 2.2.3 on 2019-09-30 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0006_auto_20190927_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='robot',
            name='run_status',
            field=models.SmallIntegerField(choices=[(0, '禁止'), (1, '运行')], default=0),
        ),
        migrations.AlterField(
            model_name='robot',
            name='protection',
            field=models.SmallIntegerField(choices=[(1, '保护'), (0, '解除')], default=2),
        ),
        migrations.AlterField(
            model_name='robot',
            name='status',
            field=models.SmallIntegerField(choices=[(1, '运行中'), (0, '已停止'), (2, '运行中(保护)'), (3, '停止中(保护)')], default=0),
        ),
    ]