function injectButton() {
    if (document.getElementById('bilisum-btn')) return;

    // 寻找注入锚点：优先尝试三连栏，其次标题下方
    const toolbar = document.querySelector('.video-toolbar-left') ||
        document.querySelector('#arc_toolbar_report') ||
        document.querySelector('.video-info-container');

    if (toolbar) {
        const btn = document.createElement('div');
        btn.id = 'bilisum-btn';
        btn.innerHTML = `
      <span style="background: #4f46e5; color: white; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 4px; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2); transition: all 0.2s;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        AI 总结
      </span>
    `;
        btn.style.marginRight = '12px';
        btn.style.display = 'inline-flex';
        btn.style.verticalAlign = 'middle';
        btn.style.zIndex = '999';

        btn.onclick = (e) => {
            e.stopPropagation();
            const currentUrl = window.location.href;
            // 生产环境需替换为真实域名
            const target = `http://localhost:5173/?url=${encodeURIComponent(currentUrl)}&auto_run=true`;
            window.open(target, '_blank');
        };

        // 鼠标悬停效果
        const span = btn.querySelector('span');
        btn.onmouseenter = () => {
            span.style.transform = 'translateY(-2px)';
            span.style.boxShadow = '0 4px 6px rgba(79, 70, 229, 0.3)';
        };
        btn.onmouseleave = () => {
            span.style.transform = 'translateY(0)';
            span.style.boxShadow = '0 2px 4px rgba(79, 70, 229, 0.2)';
        };

        // 插入到最前面
        if (toolbar.firstChild) {
            toolbar.insertBefore(btn, toolbar.firstChild);
        } else {
            toolbar.appendChild(btn);
        }
    }
}

// 使用 MutationObserver 处理 SPA 动态加载
const observer = new MutationObserver((mutations) => {
    if (!document.getElementById('bilisum-btn')) {
        injectButton();
    }
});

// 开始监听
observer.observe(document.body, { childList: true, subtree: true });

// 初始尝试注入
setTimeout(injectButton, 1000);
setTimeout(injectButton, 3000);
