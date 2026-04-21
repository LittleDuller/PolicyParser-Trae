from fastapi import HTTPException


async def get_policy_content_by_id(db_session, policy_id: int) -> str:
    """
    根据政策 ID 从数据库中获取完整的政策原文文本。
    """
    # TODO: 此处替换为真实的 select(Policy).where(Policy.id == policy_id)

    if policy_id == 1:
        return "《中华人民共和国网络安全法》是为了保障网络安全，维护网络空间主权和国家安全、社会公共利益，保护公民、法人和其他组织的合法权益，促进经济社会信息化健康发展，制定本法。"
    elif policy_id == 2:
        return "这是一份模拟的关于人工智能产业扶持的政策文档样例..."

    raise HTTPException(status_code=404, detail=f"未找到 ID={policy_id} 相关的政策文本")
