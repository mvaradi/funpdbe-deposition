from django.conf.urls import url
from funpdbe_deposition import views

urlpatterns = [
    url(r'^entries/$', views.EntryList.as_view()),
    url(r'^entries/resource/(?P<resource>[A-Za-z0-9\-]+)/$', views.EntryListByResource.as_view()),
    url(r'^entries/resource/(?P<resource>[A-Za-z0-9\-]+)/(?P<pdb_id>[A-Za-z0-9]+)/$', views.EntryDetailByResource.as_view()),
    url(r'^entries/pdb/(?P<pdb_id>[A-Za-z0-9]+)/$', views.EntryListByPdb.as_view())
]