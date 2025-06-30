from collections.abc import AsyncIterator, Iterator
from operator import itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Type,
    Union,
)

from httpx import Timeout
from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.chat_models import generate_from_stream
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    message_chunk_to_message,
)
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
)
from langchain_core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    ChatResult,
)
from langchain_core.runnables import Runnable, RunnableMap, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.utils import convert_to_secret_str, get_from_dict_or_env
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.utils.pydantic import get_fields, is_basemodel_subclass
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from volcenginesdkarkruntime._streaming import AsyncStream, Stream
from volcenginesdkarkruntime.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionToolChoiceOptionParam,
)
from volcenginesdkarkruntime.types.chat.chat_completion_chunk import ChoiceDelta
from volcenginesdkarkruntime.types.chat.chat_completion_named_tool_choice_param import (
    ChatCompletionNamedToolChoiceParam,
    Function,
)

from llmops_api.const.constant import DEFAULT_ARK_MAX_RETRIES, DEFAULT_ARK_TIMEOUT


def convert_to_ai_message(message: ChatCompletionMessage) -> AIMessage:
    content = message.content or ""

    additional_kwargs: Dict = {}

    if tool_calls := message.tool_calls:
        additional_kwargs["tool_calls"] = [tool_call.model_dump() for tool_call in tool_calls]
    if reasoning_content := message.reasoning_content:
        additional_kwargs["reasoning_content"] = reasoning_content
    return AIMessage(content=content, additional_kwargs=additional_kwargs)


def convert_to_ai_message_chunk(delta: ChoiceDelta) -> AIMessageChunk:
    content = delta.content or ""

    additional_kwargs: Dict = {}

    if delta.tool_calls:
        additional_kwargs["tool_calls"] = [tool_call.model_dump() for tool_call in delta.tool_calls]

    if delta.reasoning_content:
        additional_kwargs["reasoning_content"] = delta.reasoning_content

    return AIMessageChunk(content=content, additional_kwargs=additional_kwargs)


class ArkChatModel(BaseChatModel):
    client: Any = Field(default=None, exclude=True)  #: :meta private:
    async_client: Any = Field(default=None, exclude=True)

    ark_api_key: Optional[SecretStr] = Field(default=None)

    max_retries: int = Field(default=DEFAULT_ARK_MAX_RETRIES)
    timeout: Optional[float | Timeout] = Field(default=DEFAULT_ARK_TIMEOUT)

    model_name: str = Field(default="deepseek-r1-250528", alias="model")
    top_p: Optional[float] = 0.7
    temperature: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    streaming: bool = False
    max_tokens: Optional[int] = None

    init_kwargs: Dict[str, Any] = Field(default_factory=dict)
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @property
    def _llm_type(self) -> str:
        # 火山方舟
        return "ark_chat"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            **{"model": self.model_name},
            **super()._identifying_params,
        }

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Qianfan API."""
        normal_params = {
            "model": self.model_name,
            "stream": self.streaming,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

        return {**normal_params, **self.model_kwargs}

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        values["ark_api_key"] = convert_to_secret_str(
            get_from_dict_or_env(values, ["ark_api_key"], "ARK_API_KEY", default="")
        )

        default_values = {
            name: field.default
            for name, field in get_fields(cls).items()
            if field.default is not None
        }

        default_values.update(values)

        params = {
            **values.get("init_kwargs", {}),
            "timeout": default_values.get("timeout"),
        }

        if values["ark_api_key"].get_secret_value() != "":
            params["api_key"] = values["ark_api_key"].get_secret_value()

        try:
            if values.get("client") is None:
                from volcenginesdkarkruntime import Ark

                values["client"] = Ark(**params).chat.completions

            if values.get("async_client") is None:
                from volcenginesdkarkruntime import AsyncArk

                values["async_client"] = AsyncArk(**params).chat.completions
        except ImportError:
            raise ImportError(
                "volcengine-python-sdk[ark] package not found, please install it with "
                "`pip install volcengine-python-sdk[ark]`"
            )

        return values

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        should_stream = stream if stream is not None else self.streaming
        if should_stream:
            stream_iter = self._stream(messages, stop=stop, **kwargs)
            return generate_from_stream(stream_iter)

        message_dicts = self._create_message_dicts(messages)
        params = {"stop": stop, **self._default_params, **kwargs, "messages": message_dicts}
        response = self.client.create(**params)
        return self._create_chat_result(response)

    def _create_chat_result(self, response: ChatCompletion) -> ChatResult:
        generations = []

        for res in response.choices:
            message = convert_to_ai_message(res.message)
            generation_info = {
                "finish_reason": res.finish_reason,
                "logprobs": res.logprobs,
            }

            gen = ChatGeneration(
                message=message,
                generation_info=generation_info,
            )
            generations.append(gen)

        token_usage = response.usage or {}
        llm_output = {"token_usage": token_usage, "model_name": self.model_name}
        return ChatResult(generations=generations, llm_output=llm_output)

    @staticmethod
    def _create_message_dicts(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        return [convert_message_to_dict(m) for m in messages]

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts = self._create_message_dicts(messages)
        params = {
            "stop": stop,
            **self._default_params,
            **kwargs,
            "stream": True,
            "messages": message_dicts,
        }

        stream: Stream[ChatCompletionChunk] = self.client.create(**params)
        for chunk in stream:
            for choice in chunk.choices:
                ai_message_chunk = convert_to_ai_message_chunk(choice.delta)
                generation_info = (
                    {
                        "finish_reason": choice.finish_reason,
                    }
                    if choice.finish_reason
                    else None
                )
                cg_chunk = ChatGenerationChunk(
                    message=ai_message_chunk,
                    generation_info=generation_info,
                )
                yield cg_chunk

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        should_stream = stream if stream is not None else self.streaming
        if should_stream:
            stream_iter = self._astream(messages, stop=stop, **kwargs)

            generation = None
            async for cg_chunk in stream_iter:
                if generation is None:
                    generation = cg_chunk
                else:
                    generation += cg_chunk
            if generation is None:
                msg = "No generations found in stream."
                raise ValueError(msg)

            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=message_chunk_to_message(generation.message),
                        generation_info=generation.generation_info,
                    )
                ]
            )

        message_dicts = self._create_message_dicts(messages)
        params = {"stop": stop, **self._default_params, **kwargs, "messages": message_dicts}
        response = await self.async_client.create(**params)
        return self._create_chat_result(response)

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts = self._create_message_dicts(messages)
        params = {
            "stop": stop,
            **self._default_params,
            **kwargs,
            "stream": True,
            "messages": message_dicts,
        }

        stream: AsyncStream[ChatCompletionChunk] = await self.async_client.create(**params)
        async for chunk in stream:
            for choice in chunk.choices:
                ai_message_chunk = convert_to_ai_message_chunk(choice.delta)
                generation_info = (
                    {
                        "finish_reason": choice.finish_reason,
                    }
                    if choice.finish_reason
                    else None
                )
                cg_chunk = ChatGenerationChunk(
                    message=ai_message_chunk,
                    generation_info=generation_info,
                )
                yield cg_chunk

    def bind_tools(
        self,
        tools: Sequence[
            Union[Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
        ],
        *,
        tool_choice: Optional[Union[str, ChatCompletionToolChoiceOptionParam]] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tools to the model.

        Args:
            tools: Sequence of tools to bind to the model.
            tool_choice: The tool to use. If "any" then any tool can be used.

        Returns:
            A Runnable that returns a message.
        """
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        return self.bind(tools=formatted_tools, tool_choice=tool_choice, **kwargs)

    def with_structured_output(
        self,
        schema: Union[Dict, Type[BaseModel]],  # noqa: UP006
        *,
        method: Literal["function_calling", "json_mode", "json_schema"] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[Dict, BaseModel]]:
        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")

        is_pydantic_schema = isinstance(schema, type) and is_basemodel_subclass(schema)

        if method == "function_calling":
            key_name = convert_to_openai_tool(schema)["function"]["name"]

            if is_pydantic_schema:
                output_parser: OutputParserLike = PydanticToolsParser(
                    tools=[schema],  # type: ignore[list-item]
                    first_tool_only=True,
                )
            else:
                output_parser = JsonOutputKeyToolsParser(key_name=key_name, first_tool_only=True)

            tool_choice = ChatCompletionNamedToolChoiceParam(
                type="function", function=Function(name=key_name)
            )
            llm = self.bind_tools(
                [schema],
                tool_choice=tool_choice,
            )
        elif method == "json_mode":
            llm = self.bind(response_format={"type": "json_object"})
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)  # type: ignore[arg-type]
                if is_pydantic_schema
                else JsonOutputParser()
            )

        elif method == "json_schema":
            if is_pydantic_schema:
                key_name = convert_to_openai_tool(schema)["function"]["name"]
                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": key_name,
                        "schema": schema.model_json_schema(),  # type: ignore
                        "strict": True,
                    },
                }
            else:
                response_format = schema

            llm = self.bind(response_format=response_format)
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)  # type: ignore[arg-type]
                if is_pydantic_schema
                else JsonOutputParser()
            )

        else:
            raise ValueError(
                f"Unrecognized method argument. Expected one of 'function_calling' or "
                f"'json_mode' or 'json_schema'. Received: '{method}'"
            )

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        else:
            return llm | output_parser
