# pylint: disable=duplicate-code
"""
This module integrates OpenAI language models with MiniAgents.
"""

import logging
import typing
from functools import cache
from pprint import pformat
from typing import AsyncIterator, Any, Optional

from miniagents.ext.llm.llm_common import message_to_llm_dict, AssistantMessage
from miniagents.miniagents import (
    miniagent,
    MiniAgents,
    InteractionContext,
)

if typing.TYPE_CHECKING:
    import openai as openai_original

logger = logging.getLogger(__name__)


class OpenAIMessage(AssistantMessage):
    """
    A message generated by an OpenAI model.
    """


@miniagent
async def openai_agent(
    ctx: InteractionContext,
    model: str,
    stream: Optional[bool] = None,
    system: Optional[str] = None,
    n: int = 1,
    async_client: Optional["openai_original.AsyncOpenAI"] = None,
    reply_metadata: Optional[dict[str, Any]] = None,
    **kwargs,
) -> None:
    """
    An agent that represents Large Language Models by OpenAI.
    """
    if not async_client:
        async_client = _default_openai_client()

    if stream is None:
        stream = MiniAgents.get_current().stream_llm_tokens_by_default

    if n != 1:
        raise ValueError("Only n=1 is supported by MiniAgents for AsyncOpenAI().chat.completions.create()")

    async def message_token_streamer(metadata_so_far: dict[str, Any]) -> AsyncIterator[str]:
        if system is None:
            message_dicts = []
        else:
            message_dicts = [
                {
                    "role": "system",
                    "content": system,
                },
            ]
        message_dicts.extend(message_to_llm_dict(msg) for msg in await ctx.messages)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SENDING TO OPENAI:\n\n%s\n", pformat(message_dicts))

        openai_response = await async_client.chat.completions.create(
            messages=message_dicts, model=model, stream=stream, **kwargs
        )
        if stream:
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
            start_asap=True,  # TODO Oleksandr: should this be customizable ?
            message_token_streamer=message_token_streamer,
            # preliminary metadata:
            model=model,
            agent_alias=ctx.this_agent.alias,
            **(reply_metadata or {}),
        )
    )


@cache
def _default_openai_client() -> "openai_original.AsyncOpenAI":
    # pylint: disable=import-outside-toplevel
    # noinspection PyShadowingNames
    import openai as openai_original

    return openai_original.AsyncOpenAI()


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
