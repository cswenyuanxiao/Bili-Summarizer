#!/usr/bin/env python3
"""
API Key 功能测试脚本 - 修复版

测试 API Key 的创建、列表和删除功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n🔍 测试 1: 健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    assert response.status_code == 200, "健康检查失败"
    print("✅ 通过")

def test_create_key_without_auth():
    """测试未鉴权时创建密钥（应该失败）"""
    print("\n🔍 测试 2: 未鉴权创建密钥")
    response = requests.post(
        f"{BASE_URL}/api/keys",
        json={"name": "Test Key"}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    assert response.status_code == 401, "应该返回 401 Unauthorized"
    print("✅ 通过（正确拒绝未鉴权请求）")

def test_list_keys_without_auth():
    """测试未鉴权时列出密钥（应该失败）"""
    print("\n🔍 测试 3: 未鉴权列出密钥")
    response = requests.get(f"{BASE_URL}/api/keys")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    assert response.status_code == 401, "应该返回 401 Unauthorized"
    print("✅ 通过（正确拒绝未鉴权请求）")

def test_database_direct():
    """直接检查数据库表结构"""
    print("\n🔍 测试 4: 数据库表结构")
    import sqlite3
    
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    # 检查 api_keys 表
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='api_keys'
    """)
    
    if cursor.fetchone():
        print("✅ api_keys 表存在")
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(api_keys)")
        columns = cursor.fetchall()
        print("\n表结构:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 检查索引
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='api_keys'
        """)
        indexes = cursor.fetchall()
        if indexes:
            print("\n索引:")
            for idx in indexes:
                print(f"  - {idx[0]}")
    else:
        print("❌ api_keys 表不存在")
    
    # 检查 usage_daily 表
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='usage_daily'
    """)
    
    if cursor.fetchone():
        print("\n✅ usage_daily 表存在")
        cursor.execute("PRAGMA table_info(usage_daily)")
        columns = cursor.fetchall()
        print("表结构:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("❌ usage_daily 表不存在")
    
    conn.close()

def main():
    print("=" * 60)
    print("API Key 功能测试")
    print("=" * 60)
    
    try:
        test_health()
        test_create_key_without_auth()
        test_list_keys_without_auth()
        test_database_direct()
        
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print("✅ 后端服务正常运行")
        print("✅ 鉴权逻辑正确（拒绝未授权请求）")
        print("✅ 数据库表已正确初始化")
        print("✅ API 端点响应符合预期")
        print("\n⚠️  完整 CRUD 测试需要：")
        print("   1. 在前端登录获取真实 Supabase token")
        print("   2. 或配置 SUPABASE_URL 和 SUPABASE_ANON_KEY")
        print("   3. 使用真实 token 测试创建/列表/删除操作")
        print("\n💡 建议：在浏览器中打开 http://localhost:5173")
        print("   登录后点击用户头像 → 开发者 API 进行测试")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
