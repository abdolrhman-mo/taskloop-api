from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path, include

# Swagger setup
schema_view = get_schema_view(
    openapi.Info(
        title="TaskLoop API",
        default_version='v1',
        description="API documentation for the Task Sharing App",
        contact=openapi.Contact(email="abdelrhmanlearn@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authapi.urls')),
    path('api/sessions/', include('core.urls')),

    # Swagger and ReDoc
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
