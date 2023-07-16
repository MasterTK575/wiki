from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    # path("search", views.search, name="search"),
    path("createpage", views.create_page, name="create_page"),
    # to dynamically create pages for every possible entry
    # if you don't include the prefix pages/, then views.entry will get called on every url!
    path("pages/<str:entry_name>", views.entry, name="entry")
]
