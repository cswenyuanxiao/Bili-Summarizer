"""
Templates Router - 总结模板 CRUD 端点
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from ..auth import verify_session_token
from ..templates import (
    get_user_templates,
    create_template,
    update_template,
    delete_template
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/templates", tags=["Templates"])


class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    prompt_template: str
    output_format: Optional[str] = "markdown"
    sections: Optional[List[str]] = []


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    output_format: Optional[str] = None
    sections: Optional[List[str]] = None


@router.get("")
async def list_templates(request: Request):
    """获取用户可用的模板列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user = await verify_session_token(token)
        user_id = user["user_id"]
    except:
        user_id = "anonymous"
    
    return get_user_templates(user_id)


@router.post("")
async def add_template(request: Request, body: TemplateCreateRequest):
    """创建自定义模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    return create_template(
        user_id=user["user_id"],
        name=body.name,
        prompt_template=body.prompt_template,
        description=body.description,
        output_format=body.output_format,
        sections=body.sections
    )


@router.patch("/{template_id}")
async def patch_template(request: Request, template_id: str, body: TemplateUpdateRequest):
    """更新自定义模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = update_template(
        template_id=template_id,
        user_id=user["user_id"],
        **body.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or no permission")
        
    return {"status": "success"}


@router.delete("/{template_id}")
async def remove_template(request: Request, template_id: str):
    """删除模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = delete_template(template_id, user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or no permission")
        
    return {"status": "success"}
