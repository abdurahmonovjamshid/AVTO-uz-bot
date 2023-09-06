from django import forms
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Car, CarImage, Search, TgUser


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('__str__',
                    'seen_count', 'likes_count', 'dislikes_count', 'created_at')

    readonly_fields = ('seen_count', 'likes_count', 'dislikes_count')

    list_filter = ('model', 'year')
    search_fields = ('name', 'model', 'year', 'description', 'price')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            seen_count=Count('seen'),
            likes_count=Count('likes'),
            dislikes_count=Count('dislikes')
        )
        return queryset

    def seen_count(self, obj):
        return obj.seen_count
    seen_count.admin_order_field = 'seen_count'
    seen_count.short_description = 'Seen Count'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes Count'
    likes_count.admin_order_field = 'likes_count'

    def dislikes_count(self, obj):
        return obj.dislikes.count()
    dislikes_count.short_description = 'Dislikes Count'
    dislikes_count.admin_order_field = 'dislikes_count'

    change_form_template = 'admin/car_change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['car'] = self.get_object(request, object_id)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    fieldsets = (
        ('General Infos', {
            'fields': ('owner', 'name', 'model', 'year', 'price')
        }),
        ('Additional Details', {
            'fields': ('description', 'contact_number', 'created_at')
        }),
        ('Status', {
            'fields': ('complate',)
        })
    )

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'car_count')
    readonly_fields = ('car_count',)

    actions = ['sort_by_car_count']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(car_count=Count('car'))
        return queryset

    def car_count(self, obj):
        return obj.car_set.count()
    car_count.short_description = 'Car Count'
    car_count.admin_order_field = 'car_count'

    def sort_by_car_count(self, request, queryset):
        queryset = queryset.annotate(
            car_count=Count('car')).order_by('-car_count')
        self.message_user(request, 'Sorted by Car Count')
        return queryset
    sort_by_car_count.short_description = 'Sort by Car Count'

    fieldsets = (
        ("User Information", {
            'fields': ('telegram_id', 'first_name', 'last_name', 'username'),
        }),
        ('Bot Information', {
            'fields': ('is_bot', 'language_code'),
        }),
        ('Additional Information', {
            'fields': ('created_at', 'step', 'deleted'),
        }),
    )

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    def has_change_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False
