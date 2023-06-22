from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User
from users.pagination import UsersPagination
from users.permissions import IsRetrieveAuthenticatedOrReadOnly
from users.serializers import FollowSerializer


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsRetrieveAuthenticatedOrReadOnly,)
    pagination_class = UsersPagination

    def list(self, request, *args, **kwargs):
        paginator = self.paginate_queryset(
            self.queryset.order_by('-date_joined')
        )
        serializer = self.get_serializer(paginator, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        follows = Follow.objects.filter(following=request.user)
        followers = User.objects.filter(
            id__in=follows.values('user')
        ).order_by('-follower__created')
        paginator = self.paginate_queryset(followers)
        serializer = FollowSerializer(
            paginator, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        follower = request.user
        following = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=following, following=follower)
        if request.method == 'POST':
            if follower == following or follow:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow = Follow(user=following, following=follower)
            follow.save()
            serializer = FollowSerializer(
                following, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not follow:
            return Response(
                {'errors': 'Ошибка отписки'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
