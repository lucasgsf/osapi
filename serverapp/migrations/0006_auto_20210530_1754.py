# Generated by Django 3.2.3 on 2021-05-30 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverapp', '0005_alter_acao_idcalculo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='acao',
            name='IDCalculo',
        ),
        migrations.RemoveField(
            model_name='calculoacao',
            name='ID',
        ),
        migrations.AddField(
            model_name='calculoacao',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]