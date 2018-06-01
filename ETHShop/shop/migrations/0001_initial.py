# Generated by Django 2.0 on 2018-06-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=64)),
                ('etherum_address', models.CharField(max_length=40)),
                ('receipt', models.CharField(max_length=130)),
                ('receipt_value', models.IntegerField()),
                ('expires', models.DateTimeField()),
            ],
        ),
    ]
