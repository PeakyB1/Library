# Generated by Django 5.1.4 on 2025-03-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0003_alter_issueofbooks_reader_delete_reader'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='fb2file',
            field=models.FileField(null=True, upload_to=None, verbose_name='Файл книги'),
        ),
    ]
