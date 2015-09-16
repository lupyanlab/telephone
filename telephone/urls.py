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
    url(r'^new_game/$', grunt_views.NewGameView.as_view(), name='new_game'),
    url(r'^(?P<pk>\d+)/add_chain/', grunt_views.AddChainView.as_view(),
        name='add_chain'),

    # gameplay views
    url(r'^(?P<pk>\d+)/$', grunt_views.TelephoneView.as_view(), name='play'),
    url(r'^(?P<pk>\d+)/switchboard$', grunt_views.SwitchboardView.as_view(), name='switchboard'),
    url(r'^(?P<pk>\d+)/accept$', grunt_views.accept, name='accept'),

    # inspect views
    url(r'^(?P<pk>\d+)/inspect/$', inspect_views.InspectView.as_view(),
        name='inspect'),
    url(r'^(?P<pk>\d+)/inspect/data$', inspect_views.MessageTreeAPIView,
        name='tree'),

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
