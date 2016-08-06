from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^cards/$', views.cards_index, name='cards_index'),
    url(r'^cards/(?P<card_type>[\D]+)$', views.cards_index, name='cards_index'),
    url(r'^cards/(?P<id>[0-9]+)$', views.cards_show, name='cards_show'),

    url(r'^mechanics/$', views.mechanics_index, name='mechanics_index'),
    url(r'^mechanics/(?P<id>[0-9]+)$', views.mechanics_show, name='mechanics_show'),

    url(r'^create/$', views.create_random_card, name='create_random_card'),

    url(r'^populate_db$', views.populate_db, name='populate_db'),
    url(r'^learn$', views.learn, name='learn'),
]
