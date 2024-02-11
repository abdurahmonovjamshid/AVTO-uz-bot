from rest_framework import serializers
from .models import CarImage, Car, TgUser
from rest_framework.exceptions import ValidationError


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image_link', 'telegraph']


class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True)
    owner_telegram_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Car
        fields = ['owner_telegram_id', 'name', 'model', 'year', 'price',
                  'description', 'contact_number', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        owner_telegram_id = validated_data.pop('owner_telegram_id')

        if not images_data:
            raise ValidationError('At least one image must be provided')

        try:
            owner = TgUser.objects.get(telegram_id=owner_telegram_id)
        except TgUser.DoesNotExist:
            raise ValidationError('Invalid owner telegram_id')

        validated_data['owner'] = owner
        validated_data['post'] = True
        validated_data['complate'] = True
        car = Car.objects.create(**validated_data)
        for image_data in images_data:
            CarImage.objects.create(car=car, **image_data)
        return car