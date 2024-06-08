# pylint: disable=duplicate-code
"""
This module integrates Anthropic language models with MiniAgents.
"""

import logging
import typing
from pprint import pformat
from typing import AsyncIterator, Any, Optional

from anthropic import NOT_GIVEN

from miniagents.ext.llm.llm_common import message_to_llm_dict, AssistantMessage
from miniagents.miniagents import (
    miniagent,
    MiniAgent,
    MiniAgents,
    InteractionContext,
)

if typing.TYPE_CHECKING:
    import anthropic as anthropic_original

logger = logging.getLogger(__name__)


class AnthropicMessage(AssistantMessage):
    """
    A message generated by an Anthropic model.
    """


def create_anthropic_agent(
    async_client: Optional["anthropic_original.AsyncAnthropic"] = None,
    reply_metadata: Optional[dict[str, Any]] = None,
    alias: str = "ANTHROPIC_AGENT",
    **mini_agent_kwargs,
) -> MiniAgent:
    """
    Create an MiniAgent for Anthropic models (see MiniAgent class definition and docstring for usage details).
    """
    if not async_client:
        # pylint: disable=import-outside-toplevel
        # noinspection PyShadowingNames
        import anthropic as anthropic_original

        async_client = anthropic_original.AsyncAnthropic()

    return miniagent(
        _anthropic_func,
        async_client=async_client,
        global_reply_metadata=reply_metadata,
        alias=alias,
        **mini_agent_kwargs,
    )


async def _anthropic_func(
    ctx: InteractionContext,
    async_client: "anthropic_original.AsyncAnthropic",
    global_reply_metadata: Optional[dict[str, Any]],
    reply_metadata: Optional[dict[str, Any]] = None,
    stream: Optional[bool] = None,
    system: Optional[str] = None,
    fake_first_user_message: str = "/start",
    message_delimiter_for_same_role: str = "\n\n",
    **kwargs,
) -> None:
    """
    Run text generation with Anthropic.
    """
    if stream is None:
        stream = MiniAgents.get_current().stream_llm_tokens_by_default

    async def message_token_streamer(metadata_so_far: dict[str, Any]) -> AsyncIterator[str]:
        resolved_messages = await ctx.messages.aresolve_messages()

        message_dicts = [message_to_llm_dict(msg) for msg in resolved_messages]
        message_dicts = _fix_message_dicts(
            message_dicts,
            fake_first_user_message=fake_first_user_message,
            message_delimiter_for_same_role=message_delimiter_for_same_role,
        )

        if message_dicts and message_dicts[-1]["role"] == "system":
            # let's strip away the system message at the end
            system_message_dict = message_dicts.pop()
            system_combined = (
                system_message_dict["content"]
                if system is None
                else f"{system}{message_delimiter_for_same_role}{system_message_dict['content']}"
            )
        else:
            system_combined = system

        if system_combined is None:
            system_combined = NOT_GIVEN

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "SENDING TO ANTHROPIC:\n\n%s\nSYSTEM:\n%s\n", pformat(message_dicts), pformat(system_combined)
            )

        if stream:
            # pylint: disable=not-async-context-manager
            async with async_client.messages.stream(
                messages=message_dicts, system=system_combined, **kwargs
            ) as response:
                async for token in response.text_stream:
                    yield token
                anthropic_final_message = await response.get_final_message()
        else:
            anthropic_final_message = await async_client.messages.create(
                messages=message_dicts, stream=False, system=system_combined, **kwargs
            )
            if len(anthropic_final_message.content) != 1:
                raise RuntimeError(
                    f"exactly one TextBlock was expected from Anthropic, "
                    f"but {len(anthropic_final_message.content)} were returned instead"
                )
            yield anthropic_final_message.content[0].text  # yield the whole text as one "piece"

        metadata_so_far.update(anthropic_final_message.model_dump(exclude={"content"}))

    ctx.reply(
        AnthropicMessage.promise(
            start_asap=True,  # TODO Oleksandr: should this be customizable ?
            message_token_streamer=message_token_streamer,
            # preliminary metadata:
            agent_alias=ctx.this_agent.alias,
            **(global_reply_metadata or {}),
            **(reply_metadata or {}),
        )
    )


def _fix_message_dicts(
    message_dicts: list[dict[str, Any]], fake_first_user_message: str, message_delimiter_for_same_role: str
) -> list[dict[str, Any]]:
    if not message_dicts:
        return []

    # let's put all the system messages at the end (they will be stripped away)
    non_system_message_dicts = [message_dict for message_dict in message_dicts if message_dict["role"] != "system"]
    system_message_dicts = [message_dict for message_dict in message_dicts if message_dict["role"] == "system"]
    message_dicts = non_system_message_dicts + system_message_dicts

    fixed_message_dicts = []
    if message_dicts[0]["role"] != "user":
        # Anthropic requires the first message to come from the user (system messages don't count - their content
        # will go into a separate, `system` parameter of the API call)
        fixed_message_dicts.append({"role": "user", "content": fake_first_user_message})

    # if multiple messages with the same role are sent in a row, they should be concatenated
    for message_dict in message_dicts:
        if fixed_message_dicts and message_dict["role"] == fixed_message_dicts[-1]["role"]:
            fixed_message_dicts[-1]["content"] += message_delimiter_for_same_role + message_dict["content"]
        else:
            fixed_message_dicts.append(message_dict)

    return fixed_message_dicts
