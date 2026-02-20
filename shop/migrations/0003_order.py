from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=20, unique=True)),
                ('size', models.CharField(max_length=5)),
                ('color', models.CharField(max_length=20)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('currency', models.CharField(default='EUR', max_length=10)),
                ('full_name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=10)),
                ('delivery_method', models.CharField(max_length=30)),
                ('payment_method', models.CharField(max_length=30)),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('received', 'Zaprimljena'), ('processing', 'U obradi'), ('shipped', 'Poslana'), ('delivered', 'Dostavljena'), ('cancelled', 'Otkazana')], default='received', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='shop.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
