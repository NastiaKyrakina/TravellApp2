"""TravellApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns

from Authentication.views import ajax_load_countries
from HouseSearch.views import house_search_page

from UserProfile.views import about_page

urlpatterns = i18n_patterns(
    path('', house_search_page),
    path('admin/', admin.site.urls),
    path('user/', include('UserProfile.urls')),
    path('reg/', include('Authentication.urls')),
    path('chat/', include('Chat.urls')),
    path('house/', include('HouseSearch.urls')),
    path('load_countries/', ajax_load_countries, name='load_countries'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('about/', about_page, name='about_page'),
)


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + staticfiles_urlpatterns()
