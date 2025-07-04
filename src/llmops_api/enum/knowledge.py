from llmops_api.base.enum.labeled_enum import LabeledEnum


class RetrievalDataSourceType(LabeledEnum):
    retrieval_test = ("retrieval_test", "召回测试")
    conversation = ("conversation", "会话")
