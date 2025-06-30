from dataclasses import dataclass
from http import HTTPStatus
from typing import List, Tuple

from dashscope.embeddings import TextEmbedding
from loguru._logger import Logger


class EmbeddingException(Exception):
    pass


@dataclass
class QwenEmbedding:
    api_key: str
    logger: Logger

    def embed_documents(
        self,
        documents: List[str],
        *,
        dimension: int = 1024,
        model="text-embedding-v4",
        output_type="dense",
    ):
        resp = TextEmbedding.call(
            model=model,
            input=documents,
            dimension=dimension,
            api_key=self.api_key,
            output_type=output_type,
        )
        if resp.status_code != HTTPStatus.OK:
            self.logger.bind(resp=resp).error("text embedding failed..")
            raise EmbeddingException("text embedding failed..")

        embeddings = resp["output"]["embeddings"]
        usage = resp["usage"]["total_tokens"]

        embedding_map = {documents[i]: embeddings[i]["embedding"] for i in range(len(embeddings))}

        return embedding_map, usage

    def embed_query(
        self,
        query: str,
        *,
        dimension: int = 1024,
        model="text-embedding-v4",
        output_type="dense",
    ) -> Tuple[List[float], int]:
        resp = TextEmbedding.call(
            model=model,
            input=query,
            dimension=dimension,
            api_key=self.api_key,
            output_type=output_type,
        )
        if resp.status_code != HTTPStatus.OK:
            self.logger.bind(resp=resp).error("text embedding failed..")
            raise EmbeddingException("text embedding failed..")

        return resp["output"]["embeddings"][0]["embedding"], resp["usage"]["total_tokens"]
