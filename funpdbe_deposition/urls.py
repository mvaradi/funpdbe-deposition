from django.conf.urls import url
from funpdbe_deposition import views

urlpatterns = [
    url(r'^entries/$', views.EntryList.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]