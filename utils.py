from html import escape


def html_escape(value) -> str:
    return escape(str(value), quote=False)
