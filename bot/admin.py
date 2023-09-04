from django.contrib import admin

from .models import Car, TgUser, CarImage

# Register your models here.

@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    pass

@admin.register(Car) 
class CarAdmin(admin.ModelAdmin):
    pass


@admin.register(CarImage) 
class CarImageAdmin(admin.ModelAdmin):
    pass