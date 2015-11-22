"""Core URL configuration."""

from django.contrib import admin
from django.conf.urls import patterns, include, url
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('public.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
