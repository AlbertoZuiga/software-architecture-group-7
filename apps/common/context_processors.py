def navbar_links(_request):
    """
    Context processor that provides navigation links for the navbar.
    Args:
        _request: The HTTP request object (unused)
    Returns:
        dict: Context dictionary containing navigation links
    """
    return {
        "links": {
            "Home": "/",
            "Books": "/books/",
            "Authors": "/authors/",
        }
    }
