from abc import ABC, abstractmethod
from functools import partial
import json


class Parameter(ABC):
    def __init__(self, name: str, type: str, description: str, required: bool):
        assert type in ["string", "number", "boolean", "object", "array", "enum"]

        self.name = name
        self.type = type
        self.description = description
        self.required = required


class BaseAction(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        parameters: list[Parameter],
        callback: callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.callback = callback

    def format_action_str(self):
        """Returns a json string of format:
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
        """
        # Format parameters
        parameters = {"type": "object", "properties": {}, "required": []}
        for parameter in self.parameters:
            parameters["properties"][parameter.name] = {
                "type": parameter.type,
                "description": parameter.description,
            }
            if parameter.required:
                parameters["required"].append(parameter.name)
        # Format action
        action = {
            "name": self.name,
            "description": self.description,
            "parameters": parameters,
        }
        return json.dumps(action)
    
    @abstractmethod
    def partial_run(self, *args, **kwargs):
        pass



class ClickButtonAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "click_button",
        description: str = "Clicks a button on the page",
        parameters: list[Parameter] = [
            Parameter(
                name="button_id",
                type="string",
                description="The id of the button to click",
                required=True,
            )
        ],
    ):
        super().__init__(name, description, parameters, callback)


    def partial_run(self, button_id:str):
        return partial(self.callback, button_id=button_id)


class ClickLinkAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "click_link",
        description: str = "Clicks a link on the page",
        parameters: list[Parameter] = [
            Parameter(
                name="link_id",
                type="string",
                description="The id of the link to click",
                required=True,
            )
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, link_id:str):
        return partial(self.callback, link_id=link_id)


class FillFormAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "fill_form",
        description: str = "Fills a form on the page",
        parameters: list[Parameter] = [
            Parameter(
                name="form_id",
                type="string",
                description="The id of the form to fill",
                required=True,
            ),
            Parameter(
                name="data",
                type="object",
                description="The data to fill the form with",
                required=True,
            ),
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, form_id:str, data:dict):
        return partial(self.callback, form_id=form_id, data=data)


class SubmitFormAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "submit_form",
        description: str = "Submits a form on the page",
        parameters: list[Parameter] = [
            Parameter(
                name="form_id",
                type="string",
                description="The id of the form to submit",
                required=True,
            )
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, form_id:str):
        return partial(self.callback, form_id=form_id)


class NavigateToUrlAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "navigate_to_url",
        description: str = "Navigates to a url",
        parameters: list[Parameter] = [
            Parameter(
                name="url",
                type="string",
                description="The url to navigate to",
                required=True,
            )
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, url:str):
        return partial(self.callback, url=url)


class AskUserAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "ask_user",
        description: str = "Asks the user a question",
        parameters: list[Parameter] = [
            Parameter(
                name="question",
                type="string",
                description="The question to ask the user",
                required=True,
            )
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, question:str):
        return partial(self.callback, question=question)


class WriteToFileAction(BaseAction):
    def __init__(
        self,
        callback: callable,
        name: str = "write_to_file",
        description: str = "Writes to a file",
        parameters: list[Parameter] = [
            Parameter(
                name="file_path",
                type="string",
                description="The path to the file to write to",
                required=True,
            ),
            Parameter(
                name="data",
                type="string",
                description="The data to write to the file",
                required=True,
            ),
        ],
    ):
        super().__init__(name, description, parameters, callback)

    def partial_run(self, file_path:str, data:str):
        return partial(self.callback, file_path=file_path, data=data)