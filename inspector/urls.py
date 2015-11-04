from __future__ import unicode_literals

from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'messages', views.MessageViewSet)
router.register(r'games', views.GameViewSet)


urlpatterns = [
    url(r'', include(router.urls)),
]
