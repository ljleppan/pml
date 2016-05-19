from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^populate_db$', views.populate_db, name='populate_db'),
    url(r'^learn$', views.learn, name='learn'),
]
