from django.db import models
from django.contrib.auth.models import User
CATEGORY_CHOICES = [
    ('เครื่องดื่ม','เครื่องดื่ม'),
    ('ขนม','ขนม'),
    ('อาหารแห้ง','อาหารแห้ง'),
    ('เครื่องปรุง','เครื่องปรุง'),
    ('อื่นๆ','อื่นๆ'),
]
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='อื่นๆ')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
class Sale(models.Model):
    PAYMENT_METHODS = [('cash','เงินสด'),('qr','QR Code')]
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Sale #{self.id} - {self.total} บาท"
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    def line_total(self):
        return self.price * self.quantity
