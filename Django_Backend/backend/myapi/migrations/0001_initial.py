# Generated by Django 5.0.2 on 2024-03-12 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='createCustomerServiceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('top', models.CharField(choices=[('dress', 'dress'), ('t-shirt', 'tShirt'), ('jacket', 'jacket'), ('top', 'top'), ('long-sleeve', 'longSleeve')], max_length=20)),
                ('pant', models.CharField(choices=[('short', 'short'), ('skirt', 'skirt'), ('trouser', 'trouser')], max_length=20)),
                ('time', models.DateField()),
                ('owner', models.EmailField(max_length=254)),
                ('location', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='predictImageServiceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('gender', models.CharField(blank=True, max_length=100, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('owner', models.EmailField(max_length=254)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
    ]
