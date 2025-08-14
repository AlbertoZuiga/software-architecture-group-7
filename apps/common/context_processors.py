def navbar_links(request):
    return {
        "links": {
            "Home": "/",
            "Books": "/books/",
            "Authors": "/authors/",
        }
    }
