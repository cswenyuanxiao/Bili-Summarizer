chrome.action.onClicked.addListener((tab) => {
    if (tab.url && tab.url.includes('bilibili.com/video/')) {
        const target = `http://localhost:5173/?url=${encodeURIComponent(tab.url)}&auto_run=true`;
        chrome.tabs.create({ url: target });
    } else {
        // 如果不是 B 站视频页，直接打开主页
        chrome.tabs.create({ url: 'http://localhost:5173' });
    }
});
