from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from podmefomcloudapp.views import (
    TrackViewSet, RegisterView, LogoutView, ProfileView, MyTracksView,
    LoginView, TokenRefreshView, LikedTracksView
)

router = DefaultRouter()
router.register(r'tracks', TrackViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth endpoints
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/auth/profile/', ProfileView.as_view(), name='auth_profile'),
    
    # User tracks
    path('api/my-tracks/', MyTracksView.as_view(), name='my_tracks'),
    path('api/liked-tracks/', LikedTracksView.as_view(), name='liked_tracks'),
    
    # API routes
    path('api/', include(router.urls)),
    
    # Swagger/OpenAPI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger.json', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
