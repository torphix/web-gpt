import bs4

from src.html_models import HtmlButton, HtmlForm, HtmlLink, HtmlText


def parse_links(
    html: str,
    ignore_tags: ["<script>", "<style>", "<head>", "<meta>", "<link>"],
) -> list[HtmlLink]:
    # Parses html and returns a list of links on the page
    soup = bs4.BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    return [HtmlLink(link["href"], link.text) for link in links]


def parse_buttons(
    html: str,
    ignore_tags: ["<script>", "<style>", "<head>", "<meta>", "<link>"],
) -> list[HtmlButton]:
    # Parses html and returns a list of buttons on the page
    soup = bs4.BeautifulSoup(html, "html.parser")
    buttons = soup.find_all("button")
    return [HtmlLink(button["id"], button.text) for button in buttons]


def parse_forms(
    html: str,
    ignore_tags: ["<script>", "<style>", "<head>", "<meta>", "<link>"],
) -> list[HtmlForm]:
    # Parses html and returns a list of forms on the page
    soup = bs4.BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")
    return [HtmlLink(form["id"], form.text) for form in forms]


def parse_text(
    html: str,
    ignore_tags: [
        "<script>",
        "<style>",
        "<head>",
        "<meta>",
        "<link>",
        "<nav>",
        "<footer>",
        "<header>",
        "<aside>",
    ],
) -> list[HtmlText]:
    # Parses html and returns a list of text on the page
    soup = bs4.BeautifulSoup(html, "html.parser")
    # Remove ignored tags
    for tag in ignore_tags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()
    # Parse text in tags
    text = soup.find_all("span")
    text = soup.find_all("p")
    text += soup.find_all("h1")
    text += soup.find_all("h2")
    text += soup.find_all("h3")
    text += soup.find_all("h4")
    text += soup.find_all("h5")
    text += soup.find_all("h6")
    # Parse text in divs
    divs = soup.find_all("div")
    for div in divs:
        if div.text:
            text.append(div)
    return [HtmlLink(text["id"], text.text) for text in text]
