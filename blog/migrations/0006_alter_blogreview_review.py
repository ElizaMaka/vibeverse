# Generated by Django 4.2.7 on 2024-09-29 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_blogimage_blog_blog_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogreview',
            name='review',
            field=models.TextField(blank=True, null=True),
        ),
    ]
