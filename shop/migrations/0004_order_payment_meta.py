from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_card_brand',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_card_last4',
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
