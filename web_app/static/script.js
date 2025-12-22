document.addEventListener('DOMContentLoaded', () => {
    // --- Constants ---
    const HISTORY_KEY = 'bili_summarizer_history';

    // --- DOM Elements ---
    const summarizeForm = document.getElementById('summarize-form');
    const summarizeError = document.getElementById('summarize-error');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // UI Feedback elements
    const submitButton = document.getElementById('submit-button');
    const loader = document.getElementById('loader');
    const loaderStatus = document.getElementById('loader-status');
    const modeBadge = document.getElementById('mode-badge');
    const progressBar = document.getElementById('real-progress-bar');
    const summaryOutput = document.getElementById('summary-output');
    const usageInfo = document.getElementById('usage-info');
    const downloadButtonsContainer = document.getElementById('download-buttons');

    // --- History Logic ---

    const loadHistory = () => {
        const history = localStorage.getItem(HISTORY_KEY);
        return history ? JSON.parse(history) : [];
    };

    const saveToHistory = (url, summary, usage) => {
        const history = loadHistory();
        const timestamp = new Date().toLocaleString();

        // Simple title extraction from summary (first line)
        const titleMatch = summary.match(/^#+\s*(.+)|^(.+)/);
        const title = titleMatch ? (titleMatch[1] || titleMatch[2]).substring(0, 50) : url;

        const newItem = {
            id: Date.now(),
            url,
            title,
            summary,
            usage,
            timestamp
        };

        // Add to beginning, limit to 20 items
        const newHistory = [newItem, ...history.filter(item => item.url !== url)].slice(0, 20);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
        renderHistory();
    };

    const renderHistory = () => {
        const history = loadHistory();
        if (!historyList) return;

        if (history.length === 0) {
            historyList.innerHTML = '<div class="history-empty">暂无历史记录</div>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-info">
                    <div class="history-item-title">${item.title}</div>
                    <div class="history-item-meta">
                        <span>🕒 ${item.timestamp}</span>
                        <span>🔗 ${new URL(item.url).hostname}</span>
                    </div>
                </div>
            </div>
        `).join('');

        // Add click listeners to history items
        document.querySelectorAll('.history-item').forEach(el => {
            el.onclick = async () => {
                const id = el.getAttribute('data-id');
                const item = history.find(h => h.id == id);
                if (item) await displaySummary(item.summary, item.usage);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
        });
    };

    const displaySummary = async (summaryText, usage) => {
        // Render Markdown
        summaryOutput.innerHTML = marked.parse(summaryText);
        summaryOutput.style.display = 'block';

        // Render Mind Maps (Mermaid) - Relaxed Selector
        // Sometimes marked.js might not attach the class if the fence is not perfectly recognized or if spacing is off
        let mermaidBlocks = Array.from(summaryOutput.querySelectorAll('code.language-mermaid'));

        // Fallback: Check all code blocks for mermaid keywords if none found
        if (mermaidBlocks.length === 0) {
            const allCodeBlocks = summaryOutput.querySelectorAll('code');
            allCodeBlocks.forEach(block => {
                if (block.textContent.trim().startsWith('mermaid') || block.textContent.trim().startsWith('graph') || block.textContent.trim().startsWith('mindmap')) {
                    mermaidBlocks.push(block);
                }
            });
        }
        for (let i = 0; i < mermaidBlocks.length; i++) {
            const block = mermaidBlocks[i];
            const code = block.textContent;
            const id = `mermaid-${Date.now()}-${i}`;
            try {
                const { svg } = await mermaid.render(id, code);
                const parent = block.parentElement; // <pre>
                parent.outerHTML = `<div class="mermaid-diagram" style="text-align:center; margin: 2rem 0; background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #F2F2F7;">${svg}</div>`;
            } catch (err) {
                console.error("Mermaid rendering failed:", err);
                const parent = block.parentElement;
                parent.innerHTML = `<div style="color: #FF3B30; padding: 10px; border: 1px solid #FF3B30; border-radius: 8px;">思维导图渲染失败，请检查语法。</div><pre><code>${code}</code></pre>`;
            }
        }

        if (usage) {
            usageInfo.innerHTML = `<span>提示词: ${usage.prompt_tokens}</span> <span>生成: ${usage.completion_tokens}</span> <span>总计: ${usage.total_tokens}</span>`;
            usageInfo.style.display = 'flex';
        }

        if (downloadButtonsContainer) {
            downloadButtonsContainer.style.display = 'flex';

            // Setup download/copy buttons for this specific summary
            const downloadTxtBtn = document.getElementById('download-txt-btn');
            const downloadMdBtn = document.getElementById('download-md-btn');
            const copyBtn = document.getElementById('copy-btn');

            const downloadFile = (filename, content) => {
                const a = document.createElement('a');
                const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
                a.href = URL.createObjectURL(blob);
                a.download = filename;
                a.click();
                URL.revokeObjectURL(a.href);
            };

            if (downloadTxtBtn) downloadTxtBtn.onclick = () => downloadFile('summary.txt', summaryText);
            if (downloadMdBtn) downloadMdBtn.onclick = () => downloadFile('summary.md', summaryText);

            if (copyBtn) {
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(summaryText).then(() => {
                        const originalText = copyBtn.textContent;
                        copyBtn.textContent = "✅ 已复制到剪贴板";
                        setTimeout(() => copyBtn.textContent = originalText, 2000);
                    });
                };
            }
        }
    };

    if (clearHistoryBtn) {
        clearHistoryBtn.onclick = () => {
            if (confirm('确定要清空所有历史记录吗？')) {
                localStorage.removeItem(HISTORY_KEY);
                renderHistory();
            }
        };
    }

    // --- Summarizer logic ---
    if (summarizeForm) {
        summarizeForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const url = document.getElementById('video-url').value;
            const mode = document.getElementById('summarize-mode').value;
            const focus = document.getElementById('analysis-focus').value;

            submitButton.disabled = true;
            loader.style.display = 'block';
            loaderStatus.textContent = "正在连接服务器...";
            if (modeBadge) modeBadge.style.display = 'none';
            progressBar.style.width = "0%";
            summaryOutput.style.display = 'none';
            usageInfo.style.display = 'none';
            summarizeError.style.display = 'none';
            if (downloadButtonsContainer) downloadButtonsContainer.style.display = 'none';

            try {
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, mode, focus })
                });

                if (!response.ok) {
                    const result = await response.json();
                    throw new Error(result.detail || '总结失败');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let summaryText = "";
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (let line of lines) {
                        line = line.trim();
                        if (!line || !line.includes('{')) continue;

                        try {
                            const data = JSON.parse(line.substring(line.indexOf('{')));
                            if (data.error) throw new Error(data.error);

                            if (data.status) {
                                loaderStatus.textContent = data.status;

                                // Badge logic
                                if (modeBadge) {
                                    if (data.status.includes('subtitle')) {
                                        modeBadge.textContent = "🚀 极速字幕模式";
                                        modeBadge.style.backgroundColor = "#E5F1FF";
                                        modeBadge.style.color = "#007AFF";
                                        modeBadge.style.display = "inline-block";
                                    } else if (data.status.includes('audio')) {
                                        modeBadge.textContent = "🎵 极速音频模式";
                                        modeBadge.style.backgroundColor = "#F2F2F7";
                                        modeBadge.style.color = "#8E8E93";
                                        modeBadge.style.display = "inline-block";
                                    } else if (data.status.includes('visual') || data.status.includes('video')) {
                                        modeBadge.textContent = "👁️ 视觉增强模式";
                                        modeBadge.style.backgroundColor = "#FFF9E6";
                                        modeBadge.style.color = "#FF9500";
                                        modeBadge.style.display = "inline-block";
                                    }
                                }

                                // Progress logic
                                if (data.status.includes('Downloading')) {
                                    const match = data.status.match(/(\d+(\.\d+)?)/);
                                    if (match) progressBar.style.width = (parseFloat(match[0]) * 0.4) + "%";
                                } else if (data.status.includes('Uploading')) {
                                    progressBar.style.width = "50%";
                                } else if (data.status.includes('processing')) {
                                    progressBar.style.width = "70%";
                                } else if (data.status.includes('analyzing')) {
                                    progressBar.style.width = "90%";
                                }

                                if (data.status === 'complete') {
                                    progressBar.style.width = "100%";
                                    summaryText = data.summary;
                                    await displaySummary(summaryText, data.usage);
                                    saveToHistory(url, summaryText, data.usage);
                                }
                            }
                        } catch (e) {
                            console.warn("Parse error:", e);
                        }
                    }
                }
            } catch (error) {
                console.error(error);
                summarizeError.textContent = `错误: ${error.message}`;
                summarizeError.style.display = 'block';
            } finally {
                loader.style.display = 'none';
                submitButton.disabled = false;
            }
        });
    }

    // Initialize History
    renderHistory();
});
