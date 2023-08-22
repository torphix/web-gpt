import openai
import tiktoken
from typing import Generator

from src.actions import BaseAction
from src.html_models import FunctionResponse

available_models = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-32k",
]

input_token_costs = {
    "gpt-3.5-turbo": 0.0015 / 1000,
    "gpt-3.5-turbo-16k": 0.003 / 1000,
    "gpt-4": 0.03 / 1000,
    "gpt-4-32k": 0.06 / 1000,
}

output_token_costs = {
    "gpt-3.5-turbo": 0.002 / 1000,
    "gpt-3.5-turbo-16k": 0.004 / 1000,
    "gpt-4": 0.06 / 1000,
    "gpt-4-32k": 0.12 / 1000,
}


max_context_len = {
    "gpt-3.5-turbo": 4080,
    "gpt-3.5-turbo-16k": 16000,
    "gpt-4": 8000,
    "gpt-4-32k": 16000,
}


def create_chat_completion(
    messages: list[dict[str, str]],
    model: str,
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> Generator:
    if max_tokens is None:
        input_tokens_len = sum(
            [
                len(tiktoken.encoding_for_model(model).encode(message["content"]))
                - 2  # this is for assistant / user
                for message in messages
            ]
        )
        max_tokens = max_context_len[model] - input_tokens_len
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in response:
        chunk_message = chunk["choices"][0]["delta"]
        if chunk_message:
            content = chunk_message.get("content")
            if content:
                yield content


def llm_get_action(
    messages: list[dict[str, str]],
    actions: list[BaseAction],
    model: str = "gpt-3.5-turbo-0613",
    temperature: float = 0.5,
    max_tokens: int = None,
) -> callable | str:
    # Format actions
    functions = [action.format_action_str() for action in actions]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        temperature=temperature,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: Get the selected function call
    if response_message.get("function_call"):
        selected_fn = [
            function
            for function in functions
            if function.name == response_message["function_call"]
        ][0]
        return selected_fn.partial_run(**response_message["parameters"])
    else:
        return response_message["text"]
