from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # to dynamically create pages for every possible entry
    path("<str:entry_name>", views.entry, name="entry")
    # path("search", views.search, name="search")
]
