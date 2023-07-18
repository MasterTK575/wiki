from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import re
import random
from markdown2 import Markdown

from . import util


# this form is no longer needed
""" 
class NewSearchForm(forms.Form):
    search_input = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))
"""


class NewCreatePageForm(forms.Form):
    title = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Title'}))
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={'placeholder': 'Enter you content here'}))


class NewEditPageForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={'placeholder': 'Enter you content here'}))


def error_page(request, error_code, error_message):
    return render(request, "encyclopedia/error.html", {
        "error_code": error_code,
        "error_message": error_message
    })


def index(request):
    entries = util.list_entries()

    # if POST, then search was submitted
    if request.method == "POST":
        """
        changed the search form to be static, this is the old dynamic way
        form = NewSearchForm(request.POST)
        if form.is_valid():
            search_input = form.cleaned_data["search_input"]
        """
        search_input = request.POST.get("search_input")

        # if input is not valid, go to error page
        if not search_input or len(search_input) > 100:
            return error_page(request, "Your search request", "Not a valid input")
            """
            return render(request, "encyclopedia/error.html", {
                "error_code": "Your search request",
                "error_message": "Error: Not a valid input"
            })
            """

        # redirect to entry if page exists
        if util.get_entry(search_input):
            for entry in entries:
                if entry.casefold() == search_input.casefold():
                    return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': entry}))

        # no direct match
        else:
            potential_entries = []
            pattern = re.compile(search_input, re.IGNORECASE)
            for entry in entries:
                # look through all entries, if there is a match add it to the list
                if pattern.search(entry):
                    potential_entries.append(entry)

            return render(request, "encyclopedia/index.html", {
                "title": "No direct results for your search: " + search_input + ". Did you mean:",
                "entries": potential_entries
            })

    # if GET just render homepage
    else:
        return render(request, "encyclopedia/index.html", {
            "title": "All Pages",
            "entries": entries
        })


def entry(request, entry_name):

    # ERROR: Entry always gets called!!! - fixed with changed url

    # check if entry exists
    realentry = util.get_entry(entry_name)
    # if the entry exists, render the page
    if realentry:
        markdowner = Markdown()
        entry_html = markdowner.convert(realentry)
        entries = util.list_entries()
        # to get the actual file name with correct capitalization
        for entry in entries:
            if entry.casefold() == entry_name.casefold():
                return render(request, "encyclopedia/entry.html", {
                    "entry_name": entry,
                    "entry": entry_html
                })

    else:
        return error_page(request, entry_name, f"No page with the name {entry_name} exists!")
        """ 
        return render(request, "encyclopedia/error.html", {
            "error_code": entry_name,
            "error_message": "No such entry exists!",
        })
        """


def edit_page(request, entry_name):
    # if POST, page was edited
    if request.method == "POST":
        form = NewEditPageForm(request.POST)
        if form.is_valid():
            content_updated = form.cleaned_data["content"]
            util.save_entry(entry_name, content_updated)
            return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': entry_name}))

    # if GET, display edit page
    else:
        realentry = util.get_entry(entry_name)
        if realentry:
            EditForm = NewEditPageForm(
                initial={"content": realentry})
            return render(request, "encyclopedia/editpage.html", {
                "entry_name": entry_name,
                "editpageform": EditForm
            })
        else:
            return error_page(request, entry_name, f"No page with the name {entry_name} exists!")


def create_page(request):

    # if POST, commit form input
    if request.method == "POST":
        form = NewCreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # if page already exists, don't commit
            if util.get_entry(title):
                return error_page(request, "Page already exists", f"Page with the title {title} already exists in our database!")
            # if page doesn't exist, commit to db
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': title}))

        # if input is invalid
        else:
            return error_page(request, "Not a valid input", "Please check your input and submit again!")

    # if GET, just show page
    else:
        return render(request, "encyclopedia/createpage.html", {
            "newpageform": NewCreatePageForm()
        })


# get a random number between 0 and amount of entries, then choose entry based on that number
def random_page(request):
    entries = util.list_entries()
    number = random.randint(0, len(entries)-1)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': entries[number]}))
