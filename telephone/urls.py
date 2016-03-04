from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from grunt import views as grunt_views
from inspector import views as inspect_views
from ratings import views as ratings_views
from transcribe import views as transcribe_views


urlpatterns = patterns(
    '',

    # app views
    url(r'^$', grunt_views.GameListView.as_view(), name='games_list'),
    url(r'^new_game/$', grunt_views.NewGameView.as_view(), name='new_game'),
    url(r'^(?P<pk>\d+)/new_chains/', grunt_views.new_chains_view,
        name='new_chains'),

    # gameplay views
    url(r'^(?P<pk>\d+)/$', grunt_views.TelephoneView.as_view(), name='play'),
    url(r'^(?P<pk>\d+)/switchboard$', grunt_views.SwitchboardView.as_view(),
        name='switchboard'),
    url(r'^(?P<pk>\d+)/accept$', grunt_views.accept, name='accept'),

    # inspector views
    url(r'^(?P<pk>\d+)/inspect/$', inspect_views.InspectView.as_view(),
        name='inspect'),
    url(r'inspect/api/', include('inspector.urls')),

    # survey views
    url(r'^surveys/$', ratings_views.SurveyList.as_view(), name='survey_list'),
    url(r'^surveys/new/$', ratings_views.NewSurveyView.as_view(),
        name='new_survey'),
    url(r'^surveys/(?P<pk>\d+)/$', ratings_views.TakeSurveyView.as_view(),
        name='take_survey'),
    url(r'^surveys/(?P<pk>\d+)/inspect/$',
        ratings_views.InspectSurveyView.as_view(), name='inspect_survey'),

    # transcribe views
    url(r'^surveys/transcribe/', include([
        url(r'^$', transcribe_views.TranscriptionSurveyList.as_view(),
            name='transcribe_list'),
        url(r'^new/$', transcribe_views.NewSurveyView.as_view(),
            name='new_transcribe'),
        url(r'^(?P<pk>\d+)/$', transcribe_views.TakeSurveyView.as_view(),
            name='transcribe_messages'),
    ])),

    # admin site
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
