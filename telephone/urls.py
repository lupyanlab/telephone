from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from grunt import views as grunt_views
from inspector import views as inspect_views
from ratings import views as ratings_views


urlpatterns = patterns(
    '',

    # app views
    url(r'^$', grunt_views.GameListView.as_view(), name='games_list'),
    url(r'^new/$', grunt_views.NewGameView.as_view(), name='new_game'),

    # gameplay views
    url(r'^(?P<pk>\d+)/$', grunt_views.PlayGameView.as_view(), name='play'),
    url(r'^(?P<pk>\d+)/accept$', grunt_views.accept, name='accept'),
    url(r'^(?P<pk>\d+)/mic_check', grunt_views.mic_check, name='mic_check'),

    # inspect views
    url(r'^(?P<pk>\d+)/inspect/$', inspect_views.InspectView.as_view(),
        name='inspect'),
    url(r'^(?P<pk>\d+)/message_data$', inspect_views.message_data,
        name='message_data'),
    url(r'^messages/(?P<pk>\d+)/sprout$', inspect_views.sprout, name='sprout'),
    url(r'^messages/(?P<pk>\d+)/close$', inspect_views.close, name='close'),
    url(r'^messages/(?P<pk>\d+)/upload/$',
        inspect_views.UploadMessageView.as_view(),
        name='upload'),
    url(r'^messages/download/$', inspect_views.download, name='download'),

    # survey views
    url(r'^surveys/$', ratings_views.SurveyList.as_view(), name='survey_list'),
    url(r'^surveys/new/$', ratings_views.NewSurveyView.as_view(),
        name='new_survey'),
    url(r'^surveys/(?P<pk>\d+)/$', ratings_views.TakeSurveyView.as_view(),
        name='take_survey'),
    url(r'^surveys/(?P<pk>\d+)/inspect/$',
        ratings_views.InspectSurveyView.as_view(), name='inspect_survey'),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
