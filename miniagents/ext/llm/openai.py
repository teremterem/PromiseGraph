# pylint: disable=duplicate-code
"""
This module integrates OpenAI language models with MiniAgents.
"""

import logging
import typing
from functools import partial
from pprint import pformat
from typing import AsyncIterator, Any, Optional

from miniagents.ext.llm.llm_common import message_to_llm_dict, LangModelMessage
from miniagents.miniagents import (
    miniagent,
    MiniAgent,
    MiniAgents,
    InteractionContext,
)

if typing.TYPE_CHECKING:
    import openai as openai_original

logger = logging.getLogger(__name__)


class OpenAIMessage(LangModelMessage):
    """
    A message generated by an OpenAI model.
    """


def create_openai_agent(
    async_client: Optional["openai_original.AsyncOpenAI"] = None,
    assistant_reply_metadata: Optional[dict[str, Any]] = None,
    mini_agent_kwargs: Optional[dict[str, Any]] = None,
    **static_openai_kwargs,
) -> MiniAgent:
    """
    Create an MiniAgent for OpenAI models (see MiniAgent class definition and docstring for usage details).
    """
    if not async_client:
        # pylint: disable=import-outside-toplevel
        # noinspection PyShadowingNames
        import openai as openai_original

        async_client = openai_original.AsyncOpenAI()

    return miniagent(
        partial(
            _openai_func,
            async_client=async_client,
            global_reply_metadata=assistant_reply_metadata,
            **static_openai_kwargs,
        ),
        alias="OPENAI_AGENT",
        **(mini_agent_kwargs or {}),
    )


async def _openai_func(
    ctx: InteractionContext,
    async_client: "openai_original.AsyncOpenAI",
    global_reply_metadata: Optional[dict[str, Any]],
    reply_metadata: Optional[dict[str, Any]] = None,
    stream: Optional[bool] = None,
    system: Optional[str] = None,
    n: int = 1,
    **kwargs,
) -> None:
    """
    Run text generation with OpenAI.
    """
    global_reply_metadata = global_reply_metadata or {}
    reply_metadata = reply_metadata or {}
    if stream is None:
        stream = MiniAgents.get_current().stream_llm_tokens_by_default

    if n != 1:
        raise ValueError("Only n=1 is supported by MiniAgents for AsyncOpenAI().chat.completions.create()")

    async def message_token_producer(metadata_so_far: dict[str, Any]) -> AsyncIterator[str]:
        metadata_so_far.update(global_reply_metadata)
        metadata_so_far.update(reply_metadata)
        collected_messages = await ctx.messages.acollect_messages()

        if system is None:
            message_dicts = []
        else:
            message_dicts = [
                {
                    "role": "system",
                    "content": system,
                },
            ]
        message_dicts.extend(message_to_llm_dict(msg) for msg in collected_messages)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SENDING TO OPENAI:\n\n%s\n", pformat(message_dicts))

        openai_response = await async_client.chat.completions.create(messages=message_dicts, stream=stream, **kwargs)
        if stream:
            metadata_so_far["openai"] = {}
            async for chunk in openai_response:
                if len(chunk.choices) != 1:  # TODO Oleksandr: do I really need to check it for every token ?
                    raise RuntimeError(
                        f"exactly one Choice was expected from OpenAI, "
                        f"but {len(openai_response.choices)} were returned instead"
                    )
                token = chunk.choices[0].delta.content
                if token:
                    yield token

                metadata_so_far["role"] = chunk.choices[0].delta.role or metadata_so_far["role"]
                _merge_openai_dicts(
                    metadata_so_far,
                    chunk.model_dump(exclude={"choices": {0: {"index": ..., "delta": {"content": ..., "role": ...}}}}),
                )
        else:
            if len(openai_response.choices) != 1:
                raise RuntimeError(
                    f"exactly one Choice was expected from OpenAI, "
                    f"but {len(openai_response.choices)} were returned instead"
                )
            yield openai_response.choices[0].message.content  # yield the whole text as one "piece"

            metadata_so_far["role"] = openai_response.choices[0].message.role
            metadata_so_far.update(
                openai_response.model_dump(
                    exclude={"choices": {0: {"index": ..., "message": {"content": ..., "role": ...}}}}
                )
            )

    ctx.reply(
        OpenAIMessage.promise(
            schedule_immediately=True,  # TODO Oleksandr: should this be customizable ?
            message_token_producer=message_token_producer,
        )
    )


def _merge_openai_dicts(destination_dict: dict[str, Any], dict_to_merge: dict[str, Any]) -> None:
    """
    Merge the dict_to_merge into the destination_dict.
    """
    for key, value in dict_to_merge.items():
        if value is not None:
            existing_value = destination_dict.get(key)
            if isinstance(existing_value, dict):
                _merge_openai_dicts(existing_value, value)
            elif isinstance(existing_value, list):
                if key == "choices":
                    if not existing_value:
                        destination_dict[key] = [{}]  # we only expect a single choice in our implementation
                    _merge_openai_dicts(destination_dict[key][0], value[0])
                else:
                    destination_dict[key].extend(value)
            else:
                destination_dict[key] = value
