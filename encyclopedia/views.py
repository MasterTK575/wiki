from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import re

from . import util


# letting django render the forms
class NewSearchForm(forms.Form):
    search_input = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))


class NewCreatePageForm(forms.Form):
    title = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Title'}))
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={'placeholder': 'Enter you content here'}))


def index(request):
    entries = util.list_entries()

    # if POST, then search was submitted
    if request.method == "POST":
        form = NewSearchForm(request.POST)
        if form.is_valid():
            search_input = form.cleaned_data["search_input"]
            # redirect to entry if page exists
            if util.get_entry(search_input):
                return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': search_input}))

            # no direct match
            else:
                potential_entries = []
                pattern = re.compile(search_input, re.IGNORECASE)
                for entry in entries:
                    # print(pattern.search(entry))
                    # look through all entries, if there is a match add it to the list
                    if pattern.search(entry):
                        potential_entries.append(entry)

                return render(request, "encyclopedia/index.html", {
                    "title": "No results for your search: " + search_input + ". Did you mean:",
                    "entries": potential_entries,
                    "searchform": NewSearchForm()
                })

        # if input is not valid, go to error page
        else:
            return render(request, "encyclopedia/error.html", {
                "error_code": "Your search request",
                "error_message": "Error: Not a valid input",
                "searchform": NewSearchForm()
            })

    # if GET just render homepage
    return render(request, "encyclopedia/index.html", {
        "title": "All Pages",
        "entries": entries,
        "searchform": NewSearchForm()
    })


def entry(request, entry_name):

    # ERROR: Entry always gets called!!! - fixed with changed url
    # print("this gets called")

    # check if entry exists
    realentry = util.get_entry(entry_name)
    # if the entry exists, render the page
    if realentry:
        return render(request, "encyclopedia/entry.html", {
            "entry_name": entry_name,
            "entry": realentry,
            "searchform": NewSearchForm()
        })

    else:
        return render(request, "encyclopedia/error.html", {
            "error_code": entry_name,
            "error_message": "No such entry exists!",
            "searchform": NewSearchForm()
        })


def create_page(request):

    # if POST, commit form input
    if request.method == "POST":
        form = NewCreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # if page already exists, don't commit
            if util.get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "error_code": "Page already exists",
                    "error_message": "Page with same title already exsits in our database!",
                    "searchform": NewSearchForm()
                })
            # if page doesn't exist, commit to db
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': title}))

        # if input is invalid
        else:
            return render(request, "encyclopedia/error.html", {
                "error_code": "Not a valid input",
                "error_message": "Please check your input and submit again!",
                "searchform": NewSearchForm()
            })

    # if GET, just show page
    else:
        return render(request, "encyclopedia/createpage.html", {
            "newpageform": NewCreatePageForm(),
            "searchform": NewSearchForm()
        })
