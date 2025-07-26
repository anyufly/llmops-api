from llmops_api.base.enum.labeled_enum import LabeledEnum


class RetrievalDataSourceType(LabeledEnum):
    retrieval_test = ("retrieval_test", "召回测试")
    conversation = ("conversation", "会话")


class RetrievalMode(LabeledEnum):
    vector = ("vector", "向量检索")
    fulltext = ("fulltext", "全文检索")
    hybrid = ("hybrid", "混合检索")
