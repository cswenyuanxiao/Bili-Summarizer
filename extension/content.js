function injectButton() {
    if (document.getElementById('bilisum-btn')) return;

    // 寻找注入锚点：优先尝试新版工具栏
    const toolbar = document.querySelector('.video-toolbar-left-main') ||
        document.querySelector('.video-toolbar-left') ||
        document.querySelector('#arc_toolbar_report');

    if (toolbar) {
        const aiBtnWrap = document.createElement('div');
        aiBtnWrap.id = 'bilisum-btn';
        aiBtnWrap.className = 'toolbar-left-item-wrap'; // 使用 B 站原生类名保持间距和样式一致性
        aiBtnWrap.style.display = 'inline-flex';
        aiBtnWrap.style.alignItems = 'center';
        aiBtnWrap.style.marginRight = '12px';

        aiBtnWrap.innerHTML = `
      <div style="background: #4f46e5; color: white; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2); transition: all 0.2s; white-space: nowrap;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        AI 总结
      </div>
    `;

        aiBtnWrap.onclick = (e) => {
            e.stopPropagation();
            const currentUrl = window.location.href;
            const target = `http://localhost:5173/?url=${encodeURIComponent(currentUrl)}&auto_run=true`;
            window.open(target, '_blank');
        };

        // 鼠标悬停效果
        const btnInner = aiBtnWrap.querySelector('div');
        aiBtnWrap.onmouseenter = () => {
            btnInner.style.transform = 'translateY(-2px)';
            btnInner.style.boxShadow = '0 4px 8px rgba(79, 70, 229, 0.4)';
            btnInner.style.background = '#4338ca'; // Indigo 700
        };
        aiBtnWrap.onmouseleave = () => {
            btnInner.style.transform = 'translateY(0)';
            btnInner.style.boxShadow = '0 2px 4px rgba(79, 70, 229, 0.2)';
            btnInner.style.background = '#4f46e5'; // Indigo 600
        };

        // 插入到最前面
        if (toolbar.firstChild) {
            toolbar.insertBefore(aiBtnWrap, toolbar.firstChild);
        } else {
            toolbar.appendChild(aiBtnWrap);
        }
        console.log('Bili-Summarizer: Button injected successfully');
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
setTimeout(injectButton, 5000);
