from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username    = None
    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []
    objects         = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name  = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#6366f1")  # couleur hex pour le dashboard

    def __str__(self):
        return self.name

    class Meta:
        ordering            = ["name"]
        verbose_name_plural = "categories"


class Product(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category  = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    name      = models.CharField(max_length=255)
    quantity  = models.PositiveIntegerField(default=0)
    min_alert = models.PositiveIntegerField(default=5)   # seuil d'alerte rupture
    price     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_alert

    class Meta:
        ordering = ["name"]


class StockMovement(models.Model):
    ENTRY = "entry"
    EXIT  = "exit"
    TYPE_CHOICES = [
        (ENTRY, "Entrée"),
        (EXIT,  "Sortie"),
    ]

    product  = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    type     = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    note     = models.CharField(max_length=255, blank=True)
    date     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} — {self.product.name} ({self.quantity})"

    class Meta:
        ordering = ["-date"]