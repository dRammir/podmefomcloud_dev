from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiResponse
from django.contrib.auth.models import User
from .models import Track, Like
from .serializers import TrackSerializer, UserSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Вход в систему",
        description="Аутентификация пользователя и получение токенов",
        tags=['Аутентификация'],
        request={
            'application/json': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string', 'example': 'admin', 'description': 'Имя пользователя'},
                    'password': {'type': 'string', 'example': 'admin123', 'description': 'Пароль'},
                }
            }
        },
        responses={
            200: {
                'description': 'Токены успешно получены',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'access': {'type': 'string', 'description': 'JWT токен доступа'},
                            'refresh': {'type': 'string', 'description': 'JWT токен для обновления'},
                        }
                    }
                }
            },
            401: {'description': 'Неверные учетные данные'}
        }
    )
)
class LoginView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Обновление токена",
        description="Обновляет access токен (refresh токен не меняется)",
        tags=['Аутентификация'],
        request={
            'application/json': {
                'type': 'object',
                'required': ['refresh'],
                'properties': {
                    'refresh': {'type': 'string', 'description': 'Refresh токен'},
                }
            }
        },
        responses={
            200: {
                'description': 'Новый access токен',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'access': {'type': 'string', 'description': 'Новый JWT токен доступа'},
                        }
                    }
                }
            },
            401: {'description': 'Неверный refresh токен'}
        }
    )
)
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh токен обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
            })
        except Exception:
            return Response(
                {'error': 'Неверный или истёкший refresh токен'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@extend_schema_view(
    post=extend_schema(
        summary="Регистрация",
        description="Создание нового аккаунта пользователя",
        tags=['Аутентификация'],
        request={
            'application/json': {
                'type': 'object',
                'required': ['username', 'email', 'password'],
                'properties': {
                    'username': {'type': 'string', 'example': 'podmefom', 'description': 'Имя пользователя'},
                    'email': {'type': 'string', 'example': 'user@mail.com', 'description': 'Email'},
                    'password': {'type': 'string', 'example': 'securepass123', 'description': 'Пароль'},
                }
            }
        },
        responses={
            201: {
                'description': 'Пользователь создан',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'user': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'username': {'type': 'string'},
                                    'email': {'type': 'string'},
                                }
                            },
                            'tokens': {
                                'type': 'object',
                                'properties': {
                                    'access': {'type': 'string'},
                                    'refresh': {'type': 'string'},
                                }
                            }
                        }
                    }
                }
            },
            400: {'description': 'Ошибка валидации'}
        }
    )
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response(
                {'error': 'Username, email и password обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Пользователь с таким username уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        summary="Выход из системы",
        description="Аннулирует refresh токен",
        tags=['Аутентификация'],
        request={
            'application/json': {
                'type': 'object',
                'required': ['refresh'],
                'properties': {
                    'refresh': {'type': 'string', 'description': 'Refresh токен'},
                }
            }
        },
        responses={
            200: {'description': 'Успешный выход'},
            400: {'description': 'Ошибка'}
        }
    )
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Успешный выход'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Неверный токен'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Профиль пользователя",
        description="Получить данные текущего авторизованного пользователя",
        tags=['Аутентификация'],
        responses={
            200: {
                'description': 'Данные пользователя',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'bio': {'type': 'string'},
                            'date_joined': {'type': 'string', 'format': 'date-time'},
                        }
                    }
                }
            },
            401: {'description': 'Неавторизованный доступ'}
        }
    ),
    patch=extend_schema(
        summary="Обновить профиль",
        description="Обновить данные профиля (bio)",
        tags=['Аутентификация'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'bio': {'type': 'string', 'description': 'О себе'},
                }
            }
        },
        responses={
            200: {
                'description': 'Профиль обновлён',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'bio': {'type': 'string'},
                        }
                    }
                }
            },
            401: {'description': 'Неавторизованный доступ'}
        }
    )
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        bio = request.data.get('bio')
        if bio is not None:
            user.bio = bio
            user.save()
        return Response(UserSerializer(user).data)


@extend_schema_view(
    get=extend_schema(
        summary="Мои треки",
        description="Возвращает все треки текущего пользователя (включая pending/rejected)",
        tags=['Треки'],
        responses={
            200: TrackSerializer(many=True),
            401: {'description': 'Неавторизованный доступ'}
        }
    )
)
class MyTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tracks = Track.objects.filter(artist=request.user).order_by('-created_at')
        serializer = TrackSerializer(tracks, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Список треков",
        description="Возвращает одобренные треки. Админы видят все.",
        tags=['Треки'],
        responses={
            200: TrackSerializer(many=True),
        }
    ),
    create=extend_schema(
        summary="Создать трек",
        description="Загрузить новый трек. После создания отправляется на модерацию.",
        tags=['Треки'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'required': ['title', 'audio', 'cover'],
                'properties': {
                    'title': {'type': 'string', 'description': 'Название трека'},
                    'audio': {'type': 'string', 'format': 'binary', 'description': 'Аудио файл'},
                    'cover': {'type': 'string', 'format': 'binary', 'description': 'Обложка трека'},
                    'description': {'type': 'string', 'description': 'Описание'},
                    'category': {'type': 'string', 'enum': ['track', 'beat'], 'description': 'Категория'},
                }
            }
        },
        responses={
            201: TrackSerializer,
            400: {'description': 'Ошибка валидации'},
            401: {'description': 'Неавторизованный доступ'}
        }
    ),
    retrieve=extend_schema(
        summary="Детали трека",
        description="Получить информацию о конкретном треке",
        tags=['Треки'],
        responses={
            200: TrackSerializer,
            404: {'description': 'Трек не найден'}
        }
    ),
    destroy=extend_schema(
        summary="Удалить трек",
        description="Удалить свой трек",
        tags=['Треки'],
        responses={
            204: {'description': 'Трек удалён'},
            401: {'description': 'Неавторизованный доступ'},
            403: {'description': 'Можно удалять только свои треки'}
        }
    ),
)
class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.filter(status='approved')
    serializer_class = TrackSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ['get', 'post', 'delete', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Track.objects.all()
        return Track.objects.filter(status='approved')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(artist=self.request.user)

    def perform_destroy(self, instance):
        if instance.artist != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Вы можете удалять только свои треки")
        instance.delete()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method == 'DELETE':
            if obj.artist != request.user and not request.user.is_staff:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Вы можете удалять только свои треки")

    @extend_schema(
        summary="Лайкнуть трек",
        description="Поставить или убрать лайк",
        tags=['Треки'],
        request=None,
        responses={
            200: {
                'description': 'Результат',
                'content': {
                    'application/json': {
                        'type': 'object',
                        'properties': {
                            'liked': {'type': 'boolean', 'description': 'Лайкнут ли трек'},
                            'likes_count': {'type': 'integer', 'description': 'Количество лайков'}
                        }
                    }
                }
            },
            400: {'description': 'Можно лайкать только одобренные треки'},
            401: {'description': 'Неавторизованный доступ'}
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        track = self.get_object()
        if track.status != 'approved':
            return Response(
                {'error': 'Можно лайкать только одобренные треки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        like, created = Like.objects.get_or_create(user=request.user, track=track)
        if not created:
            like.delete()
            track.likes_count = max(0, track.likes_count - 1)
            track.save()
            return Response({'liked': False, 'likes_count': track.likes_count})

        track.likes_count += 1
        track.save()
        return Response({'liked': True, 'likes_count': track.likes_count})

