from web_app.douyin_resolver import (
    extract_download_url,
    extract_metadata,
)


def test_extract_download_url_primary_path():
    payload = {
        "data": {
            "nwm_video_url": "https://cdn.example.com/video.mp4"
        }
    }
    assert extract_download_url(payload) == "https://cdn.example.com/video.mp4"


def test_extract_download_url_fallback_list():
    payload = {
        "data": {
            "video": {
                "play_addr": {
                    "url_list": [
                        "https://cdn.example.com/video.mp4",
                        "https://cdn.example.com/video_hd.mp4"
                    ]
                }
            }
        }
    }
    assert extract_download_url(payload) == "https://cdn.example.com/video.mp4"


def test_extract_download_url_deep_search():
    payload = {
        "data": {
            "urls": [],
            "assets": {
                "items": [
                    {
                        "url": "https://cdn.example.com/video.mp4"
                    }
                ]
            }
        }
    }
    assert extract_download_url(payload) == "https://cdn.example.com/video.mp4"


def test_extract_metadata_candidates():
    payload = {
        "data": {
            "desc": "测试视频标题",
            "author": {"nickname": "作者A"},
            "cover_url": "https://cdn.example.com/cover.jpg",
            "duration": 90123
        }
    }
    metadata = extract_metadata(payload)
    assert metadata["title"] == "测试视频标题"
    assert metadata["author"] == "作者A"
    assert metadata["cover"] == "https://cdn.example.com/cover.jpg"
    assert metadata["duration"] == 90
