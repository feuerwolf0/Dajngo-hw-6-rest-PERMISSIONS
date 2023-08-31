from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Advertisement
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )
    is_favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'draft', 'created_at', 'is_favorite')

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        def get_count_opened_adv(user):
            # Возвращает количество открытых объявлений пользователя
            objects = Advertisement.objects.filter(
                creator=user,
                status='OPEN'
            )
            return len(objects)

        if self.context['request'].method == 'POST':

            if get_count_opened_adv(self.context['request'].user) >= 10:
                raise ValidationError('Одновременно открытых объявлений может быть не больше 10')

        if self.context['request'].method == 'PATCH' or self.context['request'].method == 'PUT':
            # Если пользователь хочет обновить статус объявления на статус открыто

            update_status = data.get('status', None)
            if update_status == 'OPEN':
                if get_count_opened_adv(self.context['request'].user) >= 10:
                    raise ValidationError('Одновременно открытых объявлений может быть не больше 10')

        return data


