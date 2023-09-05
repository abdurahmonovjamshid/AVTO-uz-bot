from django.contrib import admin

from .models import Car, CarImage, TgUser, Search


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    inlines = [CarImageInline]


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    pass
