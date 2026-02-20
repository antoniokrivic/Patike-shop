from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0004_order_payment_meta'),
	]

	operations = [
		migrations.AlterField(
			model_name='order',
			name='order_number',
			field=models.CharField(max_length=20),
		),
	]
