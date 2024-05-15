"""
TODO Oleksandr: docstring
"""

from typing import Any

from miniagents.messages import Message


class LangModelMessage(Message):
    """
    A message generated by a language model.
    """

    role: str


def message_to_llm_dict(message: Message) -> dict[str, Any]:
    """
    TODO Oleksandr: docstring
    """
    # TODO Oleksandr: introduce a lambda function to derive roles from messages ?
    try:
        role = message.role
    except AttributeError:
        role = "user"

    return {
        "role": role,
        "content": str(message),
    }
