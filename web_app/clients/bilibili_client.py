import json
import logging
import os
import random
import time
import uuid
from typing import Any, Dict, List, Optional

import httpx

from ..wbi import sign_wbi, parse_wbi_keys

logger = logging.getLogger(__name__)

BILIBILI_API = "https://api.bilibili.com"
BILIBILI_SESSDATA = os.getenv("BILIBILI_SESSDATA", "")


async def search_up(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索 UP 主"""
    url = f"{BILIBILI_API}/x/web-interface/search/type"
    params = {
        "keyword": keyword,
        "search_type": "bili_user",
        "page": 1,
        "page_size": limit
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://search.bilibili.com/",
        "Cookie": "buvid3=infoc;"  # 尝试简单的 buvid3
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            data = response.json()

            if data.get("code") != 0:
                logger.error(f"Search UP failed: {data.get('message')}")
                return []

            results = []
            for item in data.get("data", {}).get("result", []):
                results.append({
                    "mid": str(item.get("mid")),
                    "name": item.get("uname", ""),
                    "avatar": item.get("upic", ""),
                    "fans": item.get("fans", 0),
                    "videos": item.get("videos", 0),
                    "sign": item.get("usign", "")
                })

            return results
        except Exception as e:
            logger.error(f"Search UP exception: {e}")
            return []


async def get_up_latest_video(
    mid: str,
    client: Optional[httpx.AsyncClient] = None,
    wbi_keys: Optional[tuple[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """获取 UP 主最新视频 (支持 WBI 签名)"""

    should_close = False
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://space.bilibili.com/"
    }

    if not client:
        cookies = {}
        if BILIBILI_SESSDATA:
            cookies["SESSDATA"] = BILIBILI_SESSDATA
            logger.info(f"Using SESSDATA for single video fetch (mid={mid})")

        client = httpx.AsyncClient(headers=headers, cookies=cookies, timeout=10)
        should_close = True

    try:
        # 如果没有 key 或 是新创建的 client (没有 cookie)，都需要请求 nav
        # 注意：WBI 接口强依赖 /nav 接口种下的 buvid3/buvid4 cookie
        if not wbi_keys or should_close:
            try:
                nav_resp = await client.get("https://api.bilibili.com/x/web-interface/nav")
                nav_data = nav_resp.json()
                if not wbi_keys:
                    wbi_keys = parse_wbi_keys(nav_data)
            except Exception as e:
                logger.error(f"Failed to fetch nav info: {e}")
                return None

        if not wbi_keys or not wbi_keys[0]:
            logger.error("Failed to parse WBI keys")
            return None

        img_key, sub_key = wbi_keys

        # 构造 WBI 请求
        url = "https://api.bilibili.com/x/space/wbi/arc/search"
        params = {
            "mid": mid,
            "pn": 1,
            "ps": 1,
            "order": "pubdate"
        }

        signed_params = sign_wbi(params, img_key, sub_key)

        response = await client.get(url, params=signed_params)
        data = response.json()

        if data.get("code") != 0:
            code = data.get("code")
            msg = data.get("message", "")
            logger.error(f"Get UP latest video failed (mid={mid}): {msg} code={code}")
            # 风控错误(-352)时，刷新 nav + cookie 并重试一次
            if code == -352:
                try:
                    nav_headers = headers.copy()
                    nav_headers["Referer"] = "https://www.bilibili.com"
                    nav_resp = await client.get("https://api.bilibili.com/x/web-interface/nav", headers=nav_headers)
                    nav_data = nav_resp.json()
                    wbi_keys = parse_wbi_keys(nav_data)
                    client.cookies.update(nav_resp.cookies)
                    if wbi_keys and wbi_keys[0]:
                        img_key, sub_key = wbi_keys
                        signed_params = sign_wbi(params, img_key, sub_key)
                        retry_resp = await client.get(url, params=signed_params)
                        retry_data = retry_resp.json()
                        if retry_data.get("code") == 0:
                            data = retry_data
                        else:
                            logger.error(f"Retry failed (mid={mid}): {retry_data.get('message', '')} code={retry_data.get('code')}")
                            return None
                    else:
                        logger.error("Retry failed: WBI keys missing after nav refresh")
                        return None
                except Exception as retry_err:
                    logger.error(f"Retry exception (mid={mid}): {retry_err}")
                    return None
            else:
                return None

        videos = data.get("data", {}).get("list", {}).get("vlist", [])
        if not videos:
            return None

        v = videos[0]
        return {
            "bvid": v.get("bvid", ""),
            "title": v.get("title", ""),
            "cover": v.get("pic", ""),
            "duration": v.get("length", ""),
            "created": v.get("created", 0),
            "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}"
        }
    except Exception as e:
        logger.error(f"Get UP latest video exception: {e}")
        return None
    finally:
        if should_close:
            await client.aclose()


async def get_up_latest_videos(
    mid: str,
    count: int = 2,
    client: Optional[httpx.AsyncClient] = None,
    wbi_keys: Optional[tuple[str, str]] = None
) -> Optional[List[Dict[str, Any]]]:
    """获取 UP 主最新 N 个视频 (支持 WBI 签名)

    Args:
        mid: UP主的mid
        count: 获取视频数量
        client: 可选的httpx客户端
        wbi_keys: 可选的WBI密钥对

    Returns:
        视频列表,每个元素包含 bvid, title, cover, duration, created, url
    """

    should_close = False

    # 生成随机的浏览器指纹Cookie
    def generate_buvid():
        """生成类似B站的buvid"""
        chars = '0123456789ABCDEF'
        return ''.join(random.choice(chars) for _ in range(32))

    # 增强请求头,完全模拟真实Chrome浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://space.bilibili.com/{mid}/video",
        "Origin": "https://space.bilibili.com",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=1, i",
        "Connection": "keep-alive"
    }

    if not client:
        # 生成更真实的Cookie
        buvid3_value = generate_buvid()
        buvid4_value = f"infoc-{int(time.time() * 1000)}"

        cookies = {
            "buvid3": buvid3_value,
            "buvid4": buvid4_value,
            "b_nut": str(int(time.time())),
            "_uuid": str(uuid.uuid4()),
            "buvid_fp": generate_buvid()[:32],
            "fingerprint": generate_buvid()[:32],
            "b_lsid": str(uuid.uuid4()).replace('-', '_').upper()[:8],
        }

        # 添加SESSDATA（如果环境变量中配置了）
        if BILIBILI_SESSDATA:
            cookies["SESSDATA"] = BILIBILI_SESSDATA
            logger.info(f"Using SESSDATA from environment for mid={mid}")

        client = httpx.AsyncClient(headers=headers, cookies=cookies, timeout=20, follow_redirects=True)
        should_close = True

    try:
        # 如果没有 key 或 是新创建的 client (没有 cookie)，都需要请求 nav
        if not wbi_keys or should_close:
            try:
                # 随机延迟,模拟人类行为(0.5-1.5秒)
                import asyncio
                delay = 0.5 + random.random()
                await asyncio.sleep(delay)

                # 添加nav请求的特定头
                nav_headers = headers.copy()
                nav_headers["Referer"] = "https://www.bilibili.com"

                nav_resp = await client.get(
                    "https://api.bilibili.com/x/web-interface/nav",
                    headers=nav_headers
                )
                nav_data = nav_resp.json()

                if not wbi_keys:
                    wbi_keys = parse_wbi_keys(nav_data)

                # 更新Cookie(nav接口会返回新cookie)
                client.cookies.update(nav_resp.cookies)

            except Exception as e:
                logger.error(f"Failed to fetch nav info: {e}")
                return None

        if not wbi_keys or not wbi_keys[0]:
            logger.error("Failed to parse WBI keys")
            return None

        img_key, sub_key = wbi_keys

        # 随机延迟,避免风控(0.3-0.8秒)
        import asyncio
        delay = 0.3 + random.random() * 0.5
        await asyncio.sleep(delay)

        # 构造 WBI 请求
        url = "https://api.bilibili.com/x/space/wbi/arc/search"
        params = {
            "mid": str(mid),
            "pn": "1",
            "ps": str(count),
            "order": "pubdate",
            "platform": "web",
            "web_location": "1550101",
            "order_avoided": "true",
            "dm_img_list": "[]",
            "dm_img_str": "V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ",
        }

        signed_params = sign_wbi(params, img_key, sub_key)

        # 添加特定的请求头
        video_headers = headers.copy()
        video_headers["Referer"] = f"https://space.bilibili.com/{mid}/video"

        response = await client.get(url, params=signed_params, headers=video_headers)
        data = response.json()

        code = data.get("code")
        if code != 0:
            msg = data.get("message", '')
            logger.warning(f"Get UP latest videos failed (mid={mid}): {msg} code={code}")

            # 风控错误(-352)时,刷新 nav/cookie 并重试一次
            if code == -352:
                logger.info(f"Retrying for mid={mid} after wind control...")
                await asyncio.sleep(1 + random.random())  # 更长的延迟

                # 重新生成指纹
                client.cookies.update({
                    "buvid_fp": generate_buvid()[:32],
                    "b_lsid": str(uuid.uuid4()).replace('-', '_').upper()[:8],
                })

                try:
                    nav_headers = headers.copy()
                    nav_headers["Referer"] = "https://www.bilibili.com"
                    nav_resp = await client.get(
                        "https://api.bilibili.com/x/web-interface/nav",
                        headers=nav_headers
                    )
                    nav_data = nav_resp.json()
                    wbi_keys = parse_wbi_keys(nav_data)
                    client.cookies.update(nav_resp.cookies)

                    if not wbi_keys or not wbi_keys[0]:
                        logger.error(f"Retry failed for mid={mid}: missing WBI keys")
                        return []

                    img_key, sub_key = wbi_keys
                    signed_params = sign_wbi(params, img_key, sub_key)

                    response = await client.get(url, params=signed_params, headers=video_headers)
                    data = response.json()
                    if data.get("code") != 0:
                        logger.error(f"Retry failed for mid={mid}")
                        return []
                except Exception as retry_err:
                    logger.error(f"Retry exception for mid={mid}: {retry_err}")
                    return []
            else:
                return []

        videos = data.get("data", {}).get("list", {}).get("vlist", [])
        if not videos:
            return []

        # 转换为统一格式
        result = []
        for v in videos:
            result.append({
                "bvid": v.get("bvid", ""),
                "title": v.get("title", ""),
                "cover": v.get("pic", ""),
                "duration": v.get("length", ""),
                "created": v.get("created", 0),
                "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}"
            })

        return result
    except Exception as e:
        logger.error(f"Get UP latest videos exception: {e}")
        # 异常时返回空列表,避免前端显示错误
        return []
    finally:
        if should_close:
            await client.aclose()
