from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
from markdown2 import Markdown
import random

from . import util

class NewTaskForm(forms.Form):
    query = forms.CharField(label="Search")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": NewTaskForm()
    })

def title(request, title):
    markdowner = Markdown()
    if title not in util.list_entries():
        return render(request, "encyclopedia/error.html")
    entry = util.get_entry(title)
    print(f"entry", entry)
    convert_entry = markdowner.convert(entry)
    print(f"convert_entry", convert_entry)
    return render(request, "encyclopedia/title.html", {
        "entries": convert_entry,
        "title": title,
        "form": NewTaskForm()
    })

def edit(request, title):
    if request.method == "POST":
        data = request.POST.copy()
        title = data.get('title')
        content = data.get('content')
        util.save_entry(title, content) 
        return HttpResponseRedirect(reverse('title', kwargs={
                    'title': title
                })) 
        
    entry = util.get_entry(title)
    print(f"entry =", entry)
    return render(request, "encyclopedia/edit.html", {
        "entries": entry,
        "title": title,
        "form": NewTaskForm()
    })

    

def search(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            print(f"Query = ",query)
            if util.get_entry(query) is not None: ## directly to that entry page.
                return HttpResponseRedirect(reverse('title', kwargs={
                    'title': query
                    # "form": NewTaskForm()
                }))
            else: ## Search result page
                entries = util.list_entries()
                filterq = []
                print(f"entries = ", entries)
                for entry in entries:
                    if query in entry:
                        filterq.append(entry)
                        print(f"Entry", entry, "have substring of ", query)
                print(f"Filterq = ", filterq)
                return render(request, "encyclopedia/search.html", {
                    "entries": filterq,
                    "form": NewTaskForm(),
                    "query": query
                })

    return render(request, "encyclopedia/search.html", {
        "entries": util.list_entries(),
        "form": NewTaskForm()
    })


def new(request):
    if request.method == "POST":
        data = request.POST.copy()
        title = data.get('title')
        content = data.get('content')
        print(f"Title = ", title, "content = ", content)
        entries = util.list_entries()
        for entry in entries:
            if entry == title:
                return render(request, "encyclopedia/new.html", {
                    "mes": "This entry is already exists."
                })
        util.save_entry(title, content)    
        return render(request, "encyclopedia/title.html", {
            "entries": util.get_entry(title),
            "title": title,
            "form": NewTaskForm()
        })
    
    return render(request, "encyclopedia/new.html", {
        "form": NewTaskForm()
    })

def rand(request):
    entries = util.list_entries()
    rand = random.choice(entries)

    return HttpResponseRedirect(reverse('title', kwargs={
                    'title': rand
                })) 
