from fastapi import APIRouter

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
)


@router.get(
    "",
    description="知识库列表",
)
def knowledge_list():
    pass


@router.post(
    "",
    description="创建知识库",
)
def create_knowledge():
    pass


@router.put(
    "/{knowledge_id}",
    description="编辑知识库",
)
def edit_knowledge():
    pass


@router.delete(
    "/{knowledge_id}",
    description="删除知识库",
)
def delete_knowledge():
    pass


@router.get(
    "/{knowledge_id}/document",
    description="知识库文档列表",
)
def knowledge_document_list():
    pass


@router.post(
    "/{knowledge_id}/retrieval/test",
    description="知识库召回测试",
)
def knowledge_retrieval_test():
    pass


@router.get(
    "/{knowledge_id}/retrieval/recent",
    description="知识库召回历史记录",
)
def knowledge_retrieval_recent():
    pass


@router.post(
    "/{knowledge_id}/document/process/{process_id}",
    description="处理知识库文件",
)
def process_knowledge_document_file():
    pass


@router.get(
    "/{knowledge_id}/document/{document_id}/process/{process_id}",
    description="获取知识库文件处理状态",
)
def knowledge_document_file_process_status():
    pass


@router.post(
    "/{knowledge_id}/document/{document_id}/rename",
    description="重命名知识库文档",
)
def rename_knowledge_document():
    pass


@router.delete(
    "/{knowledge_id}/document/{document_id}",
    description="删除知识库文档",
)
def delete_knowledge_document():
    pass


@router.patch(
    "/{knowledge_id}/document/{document_id}/toggle_activate",
    description="知识库文档启用状态切换",
)
def toggle_knowledge_document_activate_status():
    pass


@router.get(
    "/{knowledge_id}/document/{document_id}/chunk",
    description="知识库文档片段列表",
)
def knowledge_document_chunk_list():
    pass


@router.post(
    "/{knowledge_id}/document/{document_id}/chunk",
    description="添加知识库文档片段",
)
def add_knowledge_document_chunk():
    pass


@router.put(
    "/{knowledge_id}/document/{document_id}/chunk/{chunk_id}",
    description="编辑知识库文档片段",
)
def edit_knowledge_document_chunk():
    pass


@router.delete(
    "/{knowledge_id}/document/{document_id}/chunk/{chunk_id}",
    description="删除知识库文档片段",
)
def delete_knowledge_document_chunk():
    pass


@router.patch(
    "/{knowledge_id}/document/{document_id}/chunk/{chunk_id}/toggle_activate",
    description="切换知识库文档启用状态",
)
def toggle_knowledge_document_chunk_activate_status():
    pass
