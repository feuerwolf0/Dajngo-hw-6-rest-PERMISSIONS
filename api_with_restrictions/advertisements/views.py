from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import AdvertisementFilter
from .manager import ManageFavorite
from .models import Advertisement, AdvertisementDraftChoices
from .permissions import IsOwner
from .serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet, ManageFavorite):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    def get_queryset(self):
        base_queryset = Advertisement.objects.all()
        # Если пользователь авторизован
        if self.request.user.is_authenticated:
            # Если пользователь админ - получаю все объявления
            if self.request.user.is_superuser:
                queryset = base_queryset
            # Иначе получаю все объявления автора и опубликованные объявления
            else:
                queryset = base_queryset.filter(
                    Q(creator=self.request.user,
                      draft=AdvertisementDraftChoices.YES)
                    |
                    Q(draft=AdvertisementDraftChoices.NO)
                    )
        # Если пользователь аноним - получаю все опубликованные объявления
        else:
            queryset = base_queryset.filter(draft=AdvertisementDraftChoices.NO)

        # Применяю фильтрацию
        queryset = self.filter_queryset(queryset)
        # Добавляю аннотацию в виде дополнитеьного поля "в избранном"
        queryset = self.annotate_qs_is_favorite_field(queryset)
        return queryset

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return []

