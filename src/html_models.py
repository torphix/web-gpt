from dataclasses import dataclass


@dataclass
class HtmlLink:
    url: str
    text: str


@dataclass
class HtmlButton:
    id: str
    text: str


@dataclass
class HtmlForm:
    id: str
    text: str


@dataclass
class HtmlText:
    text: str


