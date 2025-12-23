

# --- History Sync API ---
@app.get("/api/history")
async def get_user_history(user: dict = Depends(get_current_user)):
    """获取用户的云端历史记录"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase not configured, returning empty history")
            return []
        
        supabase = create_client(supabase_url, supabase_key)
        
        response = supabase.table("summaries")\
            .select("*")\
            .eq("user_id", user["user_id"])\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        return response.data
    
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history")
async def sync_history(
    items: List[HistoryItem],
    user: dict = Depends(get_current_user)
):
    """批量上传本地历史到云端"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            return {"uploaded": 0, "total": len(items), "error": "Supabase not configured"}
        
        supabase = create_client(supabase_url, supabase_key)
        
        uploaded = 0
        errors = []
        
        for item in items:
            try:
                # 准备数据
                data = item.dict(exclude_none=True, exclude={"id"})  # 排除 id，由数据库生成
                data["user_id"] = user["user_id"]
                
                # Upsert（存在则更新，不存在则插入）
                supabase.table("summaries").upsert(data).execute()
                uploaded += 1
            except Exception as e:
                logger.error(f"Sync error for {item.video_url}: {e}")
                errors.append(str(e))
        
        return {
            "uploaded": uploaded,
            "total": len(items),
            "errors": errors if errors else None
        }
    
    except Exception as e:
        logger.error(f"Batch sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{history_id}")
async def delete_history_item(
    history_id: str,
    user: dict = Depends(get_current_user)
):
    """删除云端历史记录"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise HTTPException(503, "Supabase not configured")
        
        supabase = create_client(supabase_url, supabase_key)
        
        # 验证所有权并删除
        response = supabase.table("summaries")\
            .delete()\
            .eq("id", history_id)\
            .eq("user_id", user["user_id"])\
            .execute()
        
        return {"message": "History item deleted"}
    
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
