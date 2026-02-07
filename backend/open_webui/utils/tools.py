import inspect
import logging
import re

from pydantic import BaseModel, Field, create_model
from typing import (
    Any,
    Awaitable,
    Callable,
    get_type_hints,
)
from functools import update_wrapper, partial


from fastapi import Request

from langchain_core.utils.function_calling import (
    convert_to_openai_function as convert_pydantic_model_to_openai_function_spec,
)

from open_webui.tools.builtin import (
    search_web,
    fetch_url,
    generate_image,
    edit_image,
    search_memories,
    add_memory,
    replace_memory_content,
    get_current_timestamp,
    calculate_timestamp,
    search_chats,
    view_chat,
    list_knowledge_bases,
    search_knowledge_bases,
    query_knowledge_bases,
    search_knowledge_files,
    query_knowledge_files,
    view_knowledge_file,
)

log = logging.getLogger(__name__)


def get_async_tool_function_and_apply_extra_params(
    function: Callable, extra_params: dict
) -> Callable[..., Awaitable]:
    sig = inspect.signature(function)
    extra_params = {k: v for k, v in extra_params.items() if k in sig.parameters}
    partial_func = partial(function, **extra_params)

    # Remove the 'frozen' keyword arguments from the signature
    # python-genai uses the signature to infer the tool properties for native function calling
    parameters = []
    for name, parameter in sig.parameters.items():
        # Exclude keyword arguments that are frozen
        if name in extra_params:
            continue
        # Keep remaining parameters
        parameters.append(parameter)

    new_sig = inspect.Signature(
        parameters=parameters, return_annotation=sig.return_annotation
    )

    if inspect.iscoroutinefunction(function):
        # wrap the functools.partial as python-genai has trouble with it
        # https://github.com/googleapis/python-genai/issues/907
        async def new_function(*args, **kwargs):
            return await partial_func(*args, **kwargs)

    else:
        # Make it a coroutine function when it is not already
        async def new_function(*args, **kwargs):
            return partial_func(*args, **kwargs)

    update_wrapper(new_function, function)
    new_function.__signature__ = new_sig

    new_function.__function__ = function  # type: ignore
    new_function.__extra_params__ = extra_params  # type: ignore

    return new_function


def get_updated_tool_function(function: Callable, extra_params: dict):
    # Get the original function and merge updated params
    __function__ = getattr(function, "__function__", None)
    __extra_params__ = getattr(function, "__extra_params__", None)

    if __function__ is not None and __extra_params__ is not None:
        return get_async_tool_function_and_apply_extra_params(
            __function__,
            {**__extra_params__, **extra_params},
        )

    return function


def get_builtin_tools(
    request: Request, extra_params: dict, features: dict = None, model: dict = None
) -> dict[str, dict]:
    """
    Get built-in tools for native function calling.
    Only returns tools when BOTH the global config is enabled AND the model capability allows it.
    """
    tools_dict = {}
    builtin_functions = []
    features = features or {}
    model = model or {}

    # Helper to get model capabilities (defaults to True if not specified)
    def get_model_capability(name: str, default: bool = True) -> bool:
        return (
            model.get("info", {})
            .get("meta", {})
            .get("capabilities", {})
            .get(name, default)
        )

    # Time utilities - always available for date calculations
    builtin_functions.extend([get_current_timestamp, calculate_timestamp])

    # Knowledge base tools - conditional injection based on model knowledge
    # If model has attached knowledge (any type), only provide query_knowledge_files
    # Otherwise, provide all KB browsing tools
    model_knowledge = model.get("info", {}).get("meta", {}).get("knowledge", [])
    if model_knowledge:
        # Model has attached knowledge - only allow semantic search within it
        builtin_functions.append(query_knowledge_files)
    else:
        # No model knowledge - allow full KB browsing
        builtin_functions.extend(
            [
                list_knowledge_bases,
                search_knowledge_bases,
                query_knowledge_bases,
                search_knowledge_files,
                query_knowledge_files,
                view_knowledge_file,
            ]
        )

    # Chats tools - search and fetch user's chat history
    builtin_functions.extend([search_chats, view_chat])

    # Add memory tools if enabled for this chat
    if features.get("memory"):
        builtin_functions.extend([search_memories, add_memory, replace_memory_content])

    # Add web search tools if enabled globally AND model has web_search capability
    if getattr(
        request.app.state.config, "ENABLE_WEB_SEARCH", False
    ) and get_model_capability("web_search"):
        builtin_functions.extend([search_web, fetch_url])

    # Add image generation/edit tools if enabled globally AND model has image_generation capability
    if getattr(
        request.app.state.config, "ENABLE_IMAGE_GENERATION", False
    ) and get_model_capability("image_generation"):
        builtin_functions.append(generate_image)
    if getattr(
        request.app.state.config, "ENABLE_IMAGE_EDIT", False
    ) and get_model_capability("image_generation"):
        builtin_functions.append(edit_image)


    # Channels tools - search channels and messages (if channels enabled globally)
    for func in builtin_functions:
        callable = get_async_tool_function_and_apply_extra_params(
            func,
            {
                "__request__": request,
                "__user__": extra_params.get("__user__", {}),
                "__event_emitter__": extra_params.get("__event_emitter__"),
                "__chat_id__": extra_params.get("__chat_id__"),
                "__message_id__": extra_params.get("__message_id__"),
                "__model_knowledge__": model_knowledge,
            },
        )

        # Generate spec from function
        pydantic_model = convert_function_to_pydantic_model(func)
        spec = convert_pydantic_model_to_openai_function_spec(pydantic_model)

        tools_dict[func.__name__] = {
            "tool_id": f"builtin:{func.__name__}",
            "callable": callable,
            "spec": spec,
            "type": "builtin",
        }

    return tools_dict


def parse_description(docstring: str | None) -> str:
    """
    Parse a function's docstring to extract the description.

    Args:
        docstring (str): The docstring to parse.

    Returns:
        str: The description.
    """

    if not docstring:
        return ""

    lines = [line.strip() for line in docstring.strip().split("\n")]
    description_lines: list[str] = []

    for line in lines:
        if re.match(r":param", line) or re.match(r":return", line):
            break

        description_lines.append(line)

    return "\n".join(description_lines)


def parse_docstring(docstring):
    """
    Parse a function's docstring to extract parameter descriptions in reST format.

    Args:
        docstring (str): The docstring to parse.

    Returns:
        dict: A dictionary where keys are parameter names and values are descriptions.
    """
    if not docstring:
        return {}

    # Regex to match `:param name: description` format
    param_pattern = re.compile(r":param (\w+):\s*(.+)")
    param_descriptions = {}

    for line in docstring.splitlines():
        match = param_pattern.match(line.strip())
        if not match:
            continue
        param_name, param_description = match.groups()
        if param_name.startswith("__"):
            continue
        param_descriptions[param_name] = param_description

    return param_descriptions


def convert_function_to_pydantic_model(func: Callable) -> type[BaseModel]:
    """
    Converts a Python function's type hints and docstring to a Pydantic model,
    including support for nested types, default values, and descriptions.

    Args:
        func: The function whose type hints and docstring should be converted.
        model_name: The name of the generated Pydantic model.

    Returns:
        A Pydantic model class.
    """
    type_hints = get_type_hints(func)
    signature = inspect.signature(func)
    parameters = signature.parameters

    docstring = func.__doc__

    function_description = parse_description(docstring)
    function_param_descriptions = parse_docstring(docstring)

    field_defs = {}
    for name, param in parameters.items():
        type_hint = type_hints.get(name, Any)
        default_value = param.default if param.default is not param.empty else ...

        param_description = function_param_descriptions.get(name, None)

        if param_description:
            field_defs[name] = (
                type_hint,
                Field(default_value, description=param_description),
            )
        else:
            field_defs[name] = type_hint, default_value

    model = create_model(func.__name__, **field_defs)
    model.__doc__ = function_description

    return model
