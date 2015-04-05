from urllib.parse import unquote

def unquote_twice(st):
    return unquote(unquote(st))
