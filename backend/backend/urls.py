from django.contrib import admin
from django.urls import path, include


api = [
    path('', include('api.urls')),
]

urlpatterns = [
    path('api/', include(api)),
    path('admin/', admin.site.urls),
]
