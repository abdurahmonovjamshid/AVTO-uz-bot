from django.db import models


class TgUser(models.Model):
    telegram_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    step = models.IntegerField(default=0)

    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Car(models.Model):
    owner = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    complate = models.BooleanField(default=False)

    delete = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.model} ({self.year})"


class CarImage(models.Model):
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='images')
    image_link = models.CharField(max_length=100)

    def __str__(self):
        return f"Image for {self.car.name} {self.car.model} ({self.car.year})"


class Search(models.Model):
    text = models.CharField(max_length=250)
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE)
    currnet_page = models.IntegerField(default=1)

    complate = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
