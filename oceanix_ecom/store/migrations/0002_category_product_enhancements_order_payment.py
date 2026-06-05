# Generated migration for OCEANIX enhancements

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('icon', models.CharField(default='fa-box', help_text='Font Awesome icon class', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cod', 'Cash on Delivery'),
                    ('upi', 'UPI (GPay / PhonePe / Paytm)'),
                    ('card', 'Credit / Debit Card'),
                    ('netbanking', 'Net Banking'),
                    ('wallet', 'Wallet'),
                ],
                default='cod',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products',
                to='store.category',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_percent',
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(99),
                ],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='highlights',
            field=models.TextField(
                blank=True,
                help_text='Enter one highlight per line (shown as bullet points)',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='mrp',
            field=models.DecimalField(
                blank=True, decimal_places=2,
                help_text='Maximum retail price (for showing discount)',
                max_digits=10, null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(
                decimal_places=1, default=4.0, max_digits=2,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(5),
                ],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='review_count',
            field=models.IntegerField(
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
