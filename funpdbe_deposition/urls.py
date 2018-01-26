from django.conf.urls import url
from funpdbe_deposition import views

urlpatterns = [
    url(r'^entries/$', views.EntryList.as_view()),
    url(r'^entries/(?P<resource>[A-Za-z0-9]+)/$', views.EntryListByResource.as_view()),
    url(r'^entries/(?P<resource>[A-Za-z0-9]+)/(?P<pdb_id>[A-Za-z0-9]{4})$', views.EntryDetailByResource.as_view()),
    url(r'^entry/(?P<pdb_id>[A-Za-z0-9]{4})/$', views.EntryDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]