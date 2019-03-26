from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


def image_folder(instance, filename):
    filename = instance.slug + '.' + filename.split('.')[1]
    return '{0}/{1}'.format(instance.slug, filename)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=image_folder)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    available = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    def __str__(self):
        return self.title


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    item_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return "Cart item for product {0}".format(self.product.title)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def add_to_cart(self, product_slug):
        cart = self
        product = Product.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product, item_total=product.price)
        new_cart_total = 0.00
        for item in cart.items.all():
            new_cart_total += float(item.item_total)
        cart.items.add(new_item)
        cart.cart_total = new_cart_total
        cart.save()

    def remove_from_cart(self, product_slug):
        cart = self
        product = Product.objects.get(slug=product_slug)
        for cart_item in cart.items.all():
            if cart_item.product == product:
                cart.items.remove(cart_item)
                cart.save()

    def change_qty(self, qty, item_id):
        cart = self
        cart_item = CartItem.objects.get(id=int(item_id))
        cart_item.qty = int(qty)
        cart_item.item_total = int(qty) * Decimal(cart_item.product.price)
        cart_item.save()
        new_cart_total = 0.00
        for item in cart.items.all():
            new_cart_total += float(item.item_total)
        cart.cart_total = new_cart_total
        cart.save()

    def __str__(self):
        return str(self.id)


ORDER_STATUS_CHOICES = (
    ('accepted for processing', 'accepted for processing'),
    ('processing', 'processing'),
    ('paid', 'paid')
)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ForeignKey(Cart, on_delete=models.CASCADE, default="")
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    buying_type = models.CharField(max_length=40,
                                   choices=(('Self-delivery', 'Self-delivery'), ('Delivery', 'Delivery')),
                                   default='Self-delivery')
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_CHOICES[0][0])

    def __str__(self):
        return 'Order #{0}'.format(str(self.id))


class MiddlwareNotification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    subscriber = models.CharField(max_length=40)

    def subscribe(self, product_slug, email):
        subscriber = self
        product = Product.objects.get(slug=product_slug)
        subscriber.product = product
        subscriber.subscriber = email
        subscriber.save()

    @staticmethod
    def notify_all_subs():

        subs = MiddlwareNotification.objects.all()

        for item in subs:
            if item.product.available:
                subject = 'Your item has arrived!'
                message = 'Item: {0} now available in our store!'.format(item.product.title)
                email_from = settings.EMAIL_HOST_USER
                send_mail(subject, message, email_from, [item.subscriber])
                sub = MiddlwareNotification.objects.get(id=item.id)
                sub.delete()


class Cupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code
