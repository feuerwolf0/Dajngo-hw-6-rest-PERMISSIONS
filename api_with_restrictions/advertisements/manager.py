from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Exists
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite, AdvertisementDraftChoices


class ManageFavorite:
    @action(
        detail=False,
        methods=['get'],
        url_path='favorites',
        permission_classes=[IsAuthenticated(),]
    )
    def favorites(self, request):
        # Выбираю только опубликованные объекты
        queryset = self.get_queryset().filter(is_favorite=True, draft=AdvertisementDraftChoices.NO)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['get'],
        url_path='favorite',
        permission_classes=[IsAuthenticated(), ]
    )
    def favorite(self, request, pk):
        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)

        if instance.creator == request.user:
            raise ValidationError('Вы не можете добавить собственное объявление в избранные')

        # Если объект - черновик, вызываю ошибку
        if instance.draft == AdvertisementDraftChoices.YES:
            raise Http404

        favorite_obj, created = Favorite.objects.get_or_create(
            owner=request.user, content_type=content_type, object_id=instance.id
        )

        if created:
            return Response({'message': 'Объявление добавлено в избранное'},
                            status=status.HTTP_201_CREATED)
        else:
            favorite_obj.delete()
            return Response({'message': 'Объявление удалено из избранного'},
                            status=status.HTTP_200_OK)

    def annotate_qs_is_favorite_field(self, queryset):
        if self.request.user.is_authenticated:
            is_favorite_subquery = Favorite.objects.filter(
                object_id=OuterRef('pk'),
                owner=self.request.user,
                content_type=ContentType.objects.get_for_model(queryset.model)
            )
            queryset = queryset.annotate(is_favorite=Exists(is_favorite_subquery))

        return queryset
