from selenium import webdriver

from html_parsers import parse_buttons, parse_forms, parse_links, parse_text
from src.html_models import HtmlButton, HtmlForm, HtmlLink, HtmlText
from src.actions import (
    AskUserAction,
    ClickButtonAction,
    ClickLinkAction,
    FillFormAction,
    NavigateToUrlAction,
    SubmitFormAction,
    WriteToFileAction,
)
from src.llm import llm_get_action


class WebAgent:
    def __init__(
        self, goal: str, start_url: str, prompt_path: str = "prompts/select_action.md"
    ):
        self.goal = goal
        self.start_url = start_url
        self.driver = webdriver.Chrome()
        self.actions = [
            ClickButtonAction(callback=self._click_button),
            ClickLinkAction(callback=self._click_link),
            FillFormAction(callback=self._fill_form),
            SubmitFormAction(callback=self._submit_form),
            NavigateToUrlAction(callback=self._navigate_to_url),
            AskUserAction(callback=self._ask_user),
            WriteToFileAction(callback=self._write_to_file),
        ]

        with open(prompt_path, "r") as f:
            self.prompt = f.read()

    def run(self, task: str):
        """
        1. Open browser using selenium
        2. Navigate to start_url if provided else use construct search term
        3. Extract html in a structured format:
            - Links
            - Buttons
            - Forms
            - Text
        4. Process extracted data using an LLM
        5. Take action
        """
        while True:
            self._navigate_to_url(self.start_url)
            parsed_html = self._extract_html_data()
            action = self._choose_action(parsed_html, task)
            print("Selected action: ", action)
            result = action()

    def _choose_action(
        self,
        parsed_html: dict[str, list[HtmlLink | HtmlButton | HtmlForm | HtmlText]],
        task: str,
    ):
        action_fn = llm_get_action(
            [
                {
                    "role": "user",
                    "content": self.prompt.format(
                        task=task,
                        links="\n".join([link.text for link in parsed_html["links"]]),
                        buttons="\n".join([btn.text for btn in parsed_html["buttons"]]),
                        forms="\n".join(
                            [
                                f"id: {form.id}, text: {form.text}"
                                for form in parsed_html["forms"]
                            ]
                        ),
                        text=parsed_html["text"],
                    ),
                }
            ],
            self.actions,
        )
        return action_fn

    def _navigate_to_url(self, url: str):
        self.driver.get(url)

    def _click_button(self, button_id: str):
        self.driver.find_element_by_id(button_id).click()

    def _click_link(self, link_id: str):
        self.driver.find_element_by_id(link_id).click()

    def _fill_form(self, form_id: str, data: dict):
        self.driver.find_element_by_id(form_id).send_keys(data)

    def _submit_form(self, form_id: str):
        self.driver.find_element_by_id(form_id).submit()

    def _ask_user(self, question: str):
        return input(question)

    def _write_to_file(self, file_path: str, data: str):
        with open(file_path, "w") as f:
            f.write(data)

    def _extract_html_data(
        self,
    ) -> dict[str, list[HtmlLink | HtmlButton | HtmlForm | HtmlText]]:
        page_src = self.driver.page_source
        links = parse_links(page_src)
        buttons = parse_buttons(page_src)
        forms = parse_forms(page_src)
        text = parse_text(page_src)

        return {
            "links": links,
            "buttons": buttons,
            "forms": forms,
            "text": text,
        }
