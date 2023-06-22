from django.contrib import admin
from django.urls import path, include


api = [
    path('', include('users.urls')),
    path('', include('api.urls')),
    path('', include('recipes.urls')),
]

urlpatterns = [
    path('api/', include(api)),
    path('admin/', admin.site.urls),
]
