# MiniAgents

⚠️ ATTENTION! THIS README IS WORK IN PROGRESS (autogenerated with `Claude 3 Opus` and `GPT 4o` and not corrected yet) ⚠️

---

Why does this framework exist at all? What is the problem it solves? What is the motivation behind it?
TODO Oleksandr: explain the motivation behind the framework

---

TODO AI: generate pseudo-FAQ

---

MiniAgents is a Python framework for building agent-based systems. It provides a simple and intuitive way to define agents and their interactions.

MiniAgents is a Python framework designed to facilitate the creation and management of agents that interact with language models (LLMs) and other services. It provides a structured way to define, call, and manage agents, making it easier to build complex systems that rely on asynchronous interactions and streaming data.

## Features

- **Agent Management**: Define and manage agents using simple decorators.
- **Agent Management**: Easily create, manage, and chain multiple agents.
- Manage chat history and persist messages
- **Chat History**: Manage chat history with support for in-memory and markdown file storage.
- Flexible chat history management, including in-memory and Markdown-based persistence
- **Asynchronous Interaction**: Support for asynchronous interactions with agents.
- **Streaming**: Stream data token by token or message by message.
- Asynchronous and parallel execution of agents
- Define agents as simple Python functions decorated with `@miniagent`
- Agents can interact with each other by sending and receiving messages
- Agents can send and receive messages asynchronously
- Agents can run in parallel and communicate with each other
- Agents can be composed to create more complex agents
- Agents can be chained together to form complex interaction flows
- Promises and async iterators are used extensively to enable non-blocking communication
- Pass messages between agents using `MessageType` objects
- Integrate with OpenAI and Anthropic LLMs using `create_openai_agent` and `create_anthropic_agent`
- Extensible architecture allows integration with various LLM providers (OpenAI, Anthropic, etc.)
- **LLM Integration**: Seamlessly integrate with popular LLMs like OpenAI and Anthropic.
- **Message Handling**: Robust message handling with support for nested messages and promises.
- Supports streaming of messages and tokens for efficient processing
- Utilities for working with message sequences (joining, splitting, etc.)
- **Utilities**: A set of utility functions to facilitate common tasks like dialog loops and message joining.
- Utilities for common interaction patterns like dialog loops and agent chaining
- Stream tokens from LLMs piece-by-piece using `StreamedPromise`
- Flatten nested message sequences with `MessageSequence`
- Promises and async iterators used extensively to enable non-blocking execution
- **Immutable Messages**: Ensures that messages are immutable, making the system more predictable and easier to debug.
- Immutable messages for predictable and reproducible agent behavior
- Immutable message passing via `Frozen` pydantic models
- Frozen data structures for immutable agent state and message metadata
- Immutable message and agent state for reproducibility
- Built on top of the `Promising` library for managing asynchronous operations
- Asynchronous promise-based programming model with `Promise` and `StreamedPromise`
- Hooks to persist messages as they are sent/received
- Typing with Pydantic for validation and serialization of messages

## Installation

```bash
pip install miniagents
```

## Usage

Here's a simple example of how to define an agent:

```python
from miniagents import miniagent, InteractionContext

@miniagent
async def my_agent(ctx: InteractionContext):
    async for message in ctx.messages:
        ctx.reply(f"You said: {message}")
```

And here's how to initiate an interaction with the agent:

```python
from miniagents import MiniAgents

async with MiniAgents():
    reply = await my_agent.inquire("Hello!")
    print(reply)  # prints "You said: Hello!"
```

For more advanced usage, check out the [examples](examples/) directory.

## Usage

Here's a simple example of defining agents and having them interact:

```python
from miniagents import miniagent, MiniAgents, InteractionContext

@miniagent
async def agent1(ctx: InteractionContext):
    ctx.reply("Hello from Agent 1!")

@miniagent
async def agent2(ctx: InteractionContext):
    message = await ctx.messages.aresolve_messages()
    ctx.reply(f"Agent 2 received: {message[0].text}")

async def main():
    async with MiniAgents():
        agent2_replies = agent2.inquire(agent1.inquire())
        print(await agent2_replies.aresolve_messages())

asyncio.run(main())
```

This will output:
```
(Message(text='Agent 2 received: Hello from Agent 1!'),)
```

For more advanced usage, including integration with LLMs, see the documentation and examples.

### Basic Example

Here's a basic example of how to create and run a simple agent using MiniAgents:

```python
import asyncio
from miniagents.miniagents import MiniAgents, miniagent, InteractionContext

@miniagent
async def simple_agent(ctx: InteractionContext) -> None:
    print("Agent is running")
    ctx.reply("Hello from the agent!")

async def main() -> None:
    async with MiniAgents():
        await simple_agent.inquire()

if __name__ == "__main__":
    asyncio.run(main())
```

### Define an Agent

You can define an agent using the `@miniagent` decorator. An agent is essentially an asynchronous function that interacts with a context.

```python
from miniagents.miniagents import miniagent, InteractionContext

@miniagent
async def my_agent(ctx: InteractionContext) -> None:
    ctx.reply("Hello, I am an agent!")
```

### Run an Agent

To run an agent, you need to create an instance of `MiniAgents` and use the `inquire` method to send messages to the agent.

```python
from miniagents.miniagents import MiniAgents

async def main():
    async with MiniAgents():
        replies = my_agent.inquire()
        async for reply in replies:
            print(await reply)

import asyncio
asyncio.run(main())
```

### Integrate with LLMs

MiniAgents provides built-in support for OpenAI and Anthropic language models. You can create agents for these models using the provided functions.

```python
from miniagents.ext.llm.openai import create_openai_agent
from miniagents.messages import Message

openai_agent = create_openai_agent(model="gpt-3.5-turbo")

async def main():
    async with MiniAgents():
        replies = openai_agent.inquire(
            Message(text="Hello, how are you?", role="user"),
            system="You are a helpful assistant.",
            max_tokens=50,
            temperature=0.7,
        )
        async for reply in replies:
            print(await reply)

import asyncio
asyncio.run(main())
```

## Basic Usage

Here's a simple example of using MiniAgents to create a dialog between a user and an AI assistant powered by OpenAI's GPT-3.5-turbo model:

```python
from miniagents.ext.llm.openai import create_openai_agent
from miniagents.ext.console_user_agent import create_console_user_agent
from miniagents.utils import adialog_loop

async def main():
    user_agent = create_console_user_agent()
    assistant_agent = create_openai_agent(model="gpt-3.5-turbo")

    await adialog_loop(user_agent, assistant_agent)

asyncio.run(main())
```

This will start an interactive dialog where the user can chat with the AI assistant in the console.

In this example:

1. We create a user agent using `create_console_user_agent()`, which reads user input from the console and writes back to the console.
2. We create an assistant agent using `create_openai_agent()`, specifying the OpenAI model to use (e.g., "gpt-3.5-turbo").
3. We start a dialog loop using `adialog_loop()`, passing the user agent and assistant agent as arguments.
4. The dialog loop runs asynchronously within the `MiniAgents` context, allowing the agents to interact and exchange messages.

### Basic Example

Here's a simple example of a conversation using the MiniAgents framework:

```python
import logging
from dotenv import load_dotenv
from miniagents.ext.chat_history_md import ChatHistoryMD
from miniagents.ext.console_user_agent import create_console_user_agent
from miniagents.ext.llm.openai import create_openai_agent
from miniagents.miniagents import MiniAgents
from miniagents.utils import adialog_loop

load_dotenv()

async def amain() -> None:
    chat_history = ChatHistoryMD("CHAT.md")
    try:
        print()
        await adialog_loop(
            user_agent=create_console_user_agent(chat_history=chat_history),
            assistant_agent=create_openai_agent(model="gpt-4o-2024-05-13"),
        )
    except KeyboardInterrupt:
        print()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    MiniAgents().run(amain())
```

### Integrating with OpenAI

To create an agent that interacts with OpenAI, you can use the `create_openai_agent` function:

```python
from miniagents.ext.llm.openai import create_openai_agent

openai_agent = create_openai_agent()

# Running the OpenAI agent
mini_agents.run(openai_agent.inquire("Hello, OpenAI!"))
```

### Integrating with Anthropic

Similarly, you can create an agent that interacts with Anthropic:

```python
from miniagents.ext.llm.anthropic import create_anthropic_agent

anthropic_agent = create_anthropic_agent()

# Running the Anthropic agent
mini_agents.run(anthropic_agent.inquire("Hello, Anthropic!"))
```

### Integrating with OpenAI

You can create an agent that interacts with OpenAI's GPT models:

```python
from dotenv import load_dotenv
from miniagents.ext.llm.openai import create_openai_agent
from miniagents.miniagents import MiniAgents

load_dotenv()

llm_agent = create_openai_agent(model="gpt-4o-2024-05-13")

async def main() -> None:
    async with MiniAgents():
        reply_sequence = llm_agent.inquire("How are you today?", max_tokens=1000, temperature=0.0)
        async for msg_promise in reply_sequence:
            async for token in msg_promise:
                print(token, end="", flush=True)
            print()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Example

For more advanced usage, you can define multiple agents and manage their interactions:

```python
from miniagents.miniagents import MiniAgents, miniagent, InteractionContext
from miniagents.promising.sentinels import AWAIT
from miniagents.utils import achain_loop

@miniagent
async def user_agent(ctx: InteractionContext) -> None:
    async for msg_promise in ctx.messages:
        async for token in msg_promise:
            print(token, end="", flush=True)
        print()
    ctx.reply(input("USER: "))

@miniagent
async def assistant_agent(ctx: InteractionContext) -> None:
    async for msg_promise in ctx.messages:
        async for token in msg_promise:
            print(token, end="", flush=True)
        print()
    ctx.reply("Hello, how can I assist you?")

async def amain() -> None:
    await achain_loop([user_agent, AWAIT, assistant_agent])

if __name__ == "__main__":
    MiniAgents().run(amain())
```

TODO Oleksandr: explain why AWAIT is used in the example above

### Advanced Example with Multiple Agents

You can create more complex interactions involving multiple agents:

```python
import asyncio
from miniagents.miniagents import MiniAgents, miniagent, InteractionContext

@miniagent
async def agent1(ctx: InteractionContext) -> None:
    print("Agent 1 is running")
    ctx.reply("Message from Agent 1")

@miniagent
async def agent2(ctx: InteractionContext) -> None:
    print("Agent 2 is running")
    ctx.reply("Message from Agent 2")

@miniagent
async def aggregator_agent(ctx: InteractionContext) -> None:
    ctx.reply([agent1.inquire(), agent2.inquire()])

async def main() -> None:
    async with MiniAgents():
        await aggregator_agent.inquire()

if __name__ == "__main__":
    asyncio.run(main())
```

### Message Handling

MiniAgents provides a structured way to handle messages using the `Message` class and its derivatives.

```python
from miniagents.messages import Message

class CustomMessage(Message):
    custom_field: str

message = CustomMessage(text="Hello", custom_field="Custom Value")
print(message.text)  # Output: Hello
print(message.custom_field)  # Output: Custom Value
```

### Handling Messages

MiniAgents provides a structured way to handle messages. You can define different types of messages such as `UserMessage`, `SystemMessage`, and `AssistantMessage`:

```python
from miniagents.ext.llm.llm_common import UserMessage, SystemMessage, AssistantMessage

user_message = UserMessage(text="Hello!")
system_message = SystemMessage(text="System message")
assistant_message = AssistantMessage(text="Assistant message")
```

TODO Oleksandr: mention that exceptions in agents are treated as messages ?

## Utility Functions

### Joining Messages

You can join multiple messages into a single message using the `join_messages` function:

```python
from miniagents.utils import join_messages

async def main():
    messages = ["Hello", "world"]
    joined_message = join_messages(messages)
    print(await joined_message.aresolve())

miniagents.run(main())
```

### Splitting Messages

You can split a message into multiple messages using the `split_messages` function:

```python
from miniagents.utils import split_messages

async def main():
    message = "Hello\n\nworld"
    split_message = split_messages(message)
    print(await split_message.aresolve_messages())

miniagents.run(main())
```

## Utilities

MiniAgents provides several utility functions to help with common tasks:

- **join_messages**: Join multiple messages into a single message.
- **split_messages**: Split a message into multiple messages based on a delimiter.

Example of joining messages:

```python
from miniagents.utils import join_messages

async def main():
    async with MiniAgents() as context:
        joined_message = join_messages(["Hello", "World"], delimiter=" ")
        print(await joined_message.aresolve())

MiniAgents().run(main())
```

## Documentation

### Modules

- `miniagents`: Core classes and functions.
- `miniagents.ext`: Extensions for integrating with external services and libraries.
- `miniagents.promising`: Classes and functions for handling promises and asynchronous operations.
- `miniagents.utils`: Utility functions for common tasks.

The framework is organized into several modules:

- `miniagents.miniagents`: Core classes for creating and managing agents
- `miniagents.messages`: Classes for representing and handling messages
- `miniagents.promising`: Utilities for managing asynchronous operations using promises
- `miniagents.ext`: Extensions for integrating with external services and utilities
  - `miniagents.ext.chat_history_md`: Chat history management using Markdown files
  - `miniagents.ext.console_user_agent`: User agent for interacting via the console
  - `miniagents.ext.llm`: Integration with language models
    - `miniagents.ext.llm.openai`: OpenAI language model integration
    - `miniagents.ext.llm.anthropic`: Anthropic language model integration

For detailed documentation on each module and class, please refer to the docstrings in the source code.

### Extending MiniAgents

You can extend the functionality of MiniAgents by creating custom agents, message types, and chat history handlers. The framework is designed to be modular and flexible, allowing you to integrate it with various services and customize its behavior to fit your needs.

### Core Concepts

- `MiniAgents`: The main context manager for running agents
- **MiniAgents**: The main class that manages the lifecycle of agents and their interactions.
- `@miniagent`: Decorator for defining agents
- **MiniAgent**: A wrapper for an agent function that allows calling the agent.
- `MiniAgent` - A wrapper around a Python function that allows it to send and receive messages
- **InteractionContext**: Provides context for the interaction, including the messages and the agent.
- **Message**: Represents a message that can be sent between agents.
- `Message` - Represents a message that can be sent between agents, with optional metadata
- **MessagePromise**: A promise of a message that can be streamed token by token.
- **MessageSequencePromise**: A promise of a sequence of messages that can be streamed message by message.

- `create_openai_agent`: Creates an OpenAI language model agent
- `create_anthropic_agent`: Creates an Anthropic language model agent

### Core Classes

- `MiniAgents`: The main context manager for managing agents and their interactions.
- `MiniAgent`: A wrapper for an agent function that allows calling the agent.
- `InteractionContext`: Provides context for an agent's interaction, including the messages and reply streamer.
- `InteractionContext`: Passed to agent functions, provides methods for replying and finishing early

### Message Handling

- `Message`: Represents a message that can be sent between agents.
- `Message`: Represents a message passed between agents
- `MessagePromise`: A promise of a message that can be streamed token by token.
- `MessagePromise`: A promise that resolves to a message
- `MessageSequencePromise`: A promise of a sequence of messages that can be streamed message by message.

### Promising

- `Promise`: Represents a promise of a value that will be resolved asynchronously.
- `StreamedPromise`: Represents a promise of a whole value that can be streamed piece by piece.
- `StreamAppender`: Allows appending pieces to a stream that is consumed by a `StreamedPromise`.

### Utilities

- `achain_loop`: Runs a loop of agents, chaining their interactions.
- `join_messages`: Joins multiple messages into a single message using a delimiter.
- `split_messages`: Splits messages based on a delimiter.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MiniAgents is released under the [MIT License](LICENSE).

## Things to remember (for the developers of this framework)

- **Different Promise and StreamedPromise resolvers, piece streamers, appenders and what not should always catch
  BaseExceptions and not just Exceptions** when they capture errors to pass those errors as "pieces" in order for
  those errors to be raised at the "consumer side". This is because many of the aforementioned Promising "primitives"
  are often part of mechanisms that involve communications between async tasks via asyncio.Queue objects and just
  interrupting those promises with KeyboardInterrupt which are extended from BaseException instead of letting
  KeyboardInterrupt to go through the queue leads to hanging of those promises (a queue is waiting for END_OF_QUEUE
  sentinel forever but the task that should send it is dead).

---

This README provides an overview of the MiniAgents framework, its features, installation instructions, usage examples, and information on testing and contributing. For more detailed documentation, please refer to the source code and comments within the project.

---

Happy coding with MiniAgents! 🚀
