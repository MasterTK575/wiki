from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util


# letting django render the form
class NewSearchForm(forms.Form):
    search_input = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))


def index(request):
    # if submitted search
    if request.method == "POST":
        form = NewSearchForm(request.POST)
        if form.is_valid():
            search_input = form.cleaned_data["search_input"]

            # redirect to entry if page exists
            if util.get_entry(search_input):
                return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': search_input}))

            # no entry page matches search
            else:
                return

        # if input is not valid, go to error page
        else:
            return render(request, "encyclopedia/error.html", {
                "entry_name": "Your search request",
                "message": "Error: Not a valid input"
            })

    # else just render homepage
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "searchform": NewSearchForm()
        })


def entry(request, entry_name):
    # change behaviour based on request method...

    # check if entry exists
    realentry = util.get_entry(entry_name)
    # if the entry exists, render the page
    if realentry:
        return render(request, "encyclopedia/entry.html", {
            "entry_name": entry_name,
            "entry": realentry
        })

    else:
        return render(request, "encyclopedia/error.html", {
            "entry_name": entry_name,
            "message": "No such entry exists!"
        })
