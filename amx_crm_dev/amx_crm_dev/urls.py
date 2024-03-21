"""
URL configuration for amx_crm_dev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.urls import re_path as url
# from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve


from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Crm_app.urls')),
    # Redirect URLs that don't start with 'static/' or 'media/' to 'static/' URLs
    url(r'^(?!/?static/|/?media/)(?P<path>.*)$', RedirectView.as_view(url='/static/%(path)s', permanent=False)),
] 

# Serve media files from MEDIA_ROOT at MEDIA_URL
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add a catch-all URL pattern to serve index.html for frontend routes
urlpatterns += [
    url(r'^.*', serve, kwargs={'path': 'index.html'}),
]

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('Crm_app.urls')),
#     # path('home/', TemplateView.as_view(template_name = 'home.html'), name = 'home'),

#     url(r'^(?!/?static/)(?!/?media/)(?P<path>.\..)$',
#     RedirectView.as_view(url='/static/%(path)s', permanent=False)),

# ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+[url(r'^.*', serve,kwargs={'path': 'index.html'})]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
