(function () {
    'use strict';

    let injected = false; // 全局标记，防止重复注入
    let observer = null;

    function injectButton() {
        if (injected || document.getElementById('bilisum-btn')) {
            return;
        }

        try {
            const toolbar =
                document.querySelector('.video-toolbar-left-main') ||
                document.querySelector('.video-toolbar-left') ||
                document.querySelector('#arc_toolbar_report');

            if (!toolbar) {
                console.debug('[Bili-Summarizer] Toolbar not found, will retry');
                return;
            }

            const aiBtnWrap = document.createElement('div');
            aiBtnWrap.id = 'bilisum-btn';
            aiBtnWrap.className = 'toolbar-left-item-wrap';
            aiBtnWrap.style.cssText = 'display: inline-flex; align-items: center; margin-right: 12px;';

            aiBtnWrap.innerHTML = `
        <div style="background: #4f46e5; color: white; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2); transition: all 0.2s; white-space: nowrap;">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
          AI 总结
        </div>
      `;

            const btnInner = aiBtnWrap.querySelector('div');

            aiBtnWrap.addEventListener('click', (e) => {
                e.stopPropagation();
                const currentUrl = window.location.href;
                const target = `http://localhost:5173/?url=${encodeURIComponent(currentUrl)}&auto_run=true`;
                window.open(target, '_blank');
            });

            aiBtnWrap.addEventListener('mouseenter', () => {
                btnInner.style.transform = 'translateY(-2px)';
                btnInner.style.boxShadow = '0 4px 8px rgba(79, 70, 229, 0.4)';
                btnInner.style.background = '#4338ca';
            });

            aiBtnWrap.addEventListener('mouseleave', () => {
                btnInner.style.transform = 'translateY(0)';
                btnInner.style.boxShadow = '0 2px 4px rgba(79, 70, 229, 0.2)';
                btnInner.style.background = '#4f46e5';
            });

            if (toolbar.firstChild) {
                toolbar.insertBefore(aiBtnWrap, toolbar.firstChild);
            } else {
                toolbar.appendChild(aiBtnWrap);
            }

            injected = true;
            console.log('[Bili-Summarizer] Button injected successfully');

            // 成功注入后立即断开 Observer
            if (observer) {
                observer.disconnect();
                observer = null;
            }
        } catch (err) {
            console.error('[Bili-Summarizer] Injection failed:', err);
        }
    }

    // 使用精准的 MutationObserver
    function startObserver() {
        if (observer || injected) return;

        const targetNode = document.querySelector('#bilibili-player') || document.body;

        observer = new MutationObserver(() => {
            if (!injected && !document.getElementById('bilisum-btn')) {
                injectButton();
            }
        });

        // 仅监听 childList，不监听 subtree（减少触发频率）
        observer.observe(targetNode, { childList: true, subtree: false });
    }

    // 监听 SPA 路由变化
    function handleRouteChange() {
        if (window.location.pathname.includes('/video/')) {
            injected = false; // 重置标记
            setTimeout(() => {
                injectButton();
                if (!injected) {
                    startObserver();
                }
            }, 800);
        }
    }

    // 初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(injectButton, 500);
        });
    } else {
        setTimeout(injectButton, 500);
    }

    // 备用重试（仅一次）
    setTimeout(() => {
        if (!injected) {
            injectButton();
            startObserver();
        }
    }, 2000);

    // 监听 SPA 路由变化
    window.addEventListener('popstate', handleRouteChange);
    let lastUrl = location.href;
    new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            handleRouteChange();
        }
    }).observe(document, { subtree: true, childList: true });
})();
