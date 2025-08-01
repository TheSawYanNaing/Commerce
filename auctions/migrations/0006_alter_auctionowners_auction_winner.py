# Generated by Django 5.2.4 on 2025-07-30 10:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bids_bidprice_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionowners',
            name='auction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='auctions.auctions'),
        ),
        migrations.CreateModel(
            name='Winner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='winner', to='auctions.auctions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
