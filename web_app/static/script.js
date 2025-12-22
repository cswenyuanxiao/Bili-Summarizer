document.addEventListener('DOMContentLoaded', () => {
    // --- Constants ---
    const HISTORY_KEY = 'bili_summarizer_history';
    let currentVideoUrl = ''; // Store current video URL for player

    // --- DOM Elements ---
    const summarizeForm = document.getElementById('summarize-form');
    const submitButton = document.getElementById('submit-button');
    const videoUrlInput = document.getElementById('video-url');
    const loader = document.getElementById('loader');
    const loaderStatus = document.getElementById('loader-status');
    const progressBar = document.getElementById('real-progress-bar');
    const resultContainer = document.getElementById('result-container');
    const summaryOutput = document.getElementById('summary-output');
    const mermaidContainer = document.getElementById('mermaid-container');
    const transcriptContainer = document.getElementById('transcript-container');
    const usageInfo = document.getElementById('usage-info');
    const summarizeError = document.getElementById('summarize-error');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const exportBar = document.getElementById('export-bar');

    // Store raw data for download
    let currentSummaryRaw = "";
    let currentMermaidCode = "";
    let currentTranscript = "";

    // --- Simple Progress Helper (Replaced ProgressManager) ---
    const updateProgress = (percent, message) => {
        progressBar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        if (message) loaderStatus.textContent = message;

        if (percent >= 100) {
            progressBar.parentElement.classList.add('finished');
        } else {
            progressBar.parentElement.classList.remove('finished');
        }
    };

    // --- Tab Switching Logic ---
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            document.getElementById(`tab-${target}`).classList.add('active');
        });
    });

    // --- History Logic ---
    const loadHistory = () => {
        const history = localStorage.getItem(HISTORY_KEY);
        return history ? JSON.parse(history) : [];
    };

    const saveToHistory = (url, summary, usage) => {
        const history = loadHistory();
        const timestamp = new Date().toLocaleString();
        const titleMatch = summary.match(/^#+\s*(.+)|^(.+)/);
        const title = titleMatch ? (titleMatch[1] || titleMatch[2]).substring(0, 50) : url.substring(0, 50);

        const newItem = {
            id: Date.now(),
            url,
            title,
            summary,
            usage,
            timestamp
        };

        const newHistory = [newItem, ...history.filter(item => item.url !== url)].slice(0, 20);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
        renderHistory();
    };

    const renderHistory = () => {
        const history = loadHistory();
        if (!historyList) return;

        if (history.length === 0) {
            historyList.innerHTML = '<div class="history-empty">暂无历史记录。开始总结一个视频吧！</div>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-title">${item.title}</div>
                <div class="history-item-meta">
                    <span>🕒 ${item.timestamp}</span>
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.history-item').forEach(el => {
            el.onclick = async () => {
                const id = el.getAttribute('data-id');
                const item = history.find(h => h.id == id);
                if (item) {
                    await displaySummary(item.summary, item.usage, "");
                    window.scrollTo({ top: resultContainer.offsetTop - 20, behavior: 'smooth' });
                }
            };
        });
    };

    // --- Display Result ---
    const displaySummary = async (summaryText, usage, transcriptText) => {
        currentSummaryRaw = summaryText;
        currentTranscript = transcriptText;

        // Show result container
        resultContainer.style.display = 'grid';
        loader.style.display = 'none';

        // 1. Extract Mermaid code
        const mermaidRegex = /```mermaid([\s\S]*?)```/g;
        currentMermaidCode = "";
        const cleanedSummary = summaryText.replace(mermaidRegex, (m, code) => {
            currentMermaidCode += code.trim() + "\n";
            return "";
        });

        // 2. Render Summary
        summaryOutput.innerHTML = marked.parse(cleanedSummary);

        // 3. Render Mermaid
        mermaidContainer.innerHTML = '';
        if (currentMermaidCode) {
            try {
                const id = `mermaid-diagram-${Date.now()}`;
                const { svg } = await mermaid.render(id, currentMermaidCode);
                mermaidContainer.innerHTML = svg;
            } catch (err) {
                console.error("Mermaid rendering failed:", err);
                mermaidContainer.innerHTML = `<div style="color:var(--danger); padding:1rem;">思维导图渲染失败: ${err.message}</div><pre style="text-align:left; overflow-x:auto; font-size:0.8rem;">${currentMermaidCode}</pre>`;
            }
        } else {
            mermaidContainer.innerHTML = '<p class="mindmap-empty">本次总结未生成思维导图。</p>';
        }

        // 4. Render Transcript
        if (transcriptText) {
            // Parse VTT/SRT-like format with timestamps
            const lines = transcriptText.split('\n').filter(l => l.trim());
            let html = '';
            lines.forEach(line => {
                // Check if line contains timestamp (e.g., "00:00:05.000 --> 00:00:10.000" or starts with time)
                const timeMatch = line.match(/^(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)/);
                if (timeMatch) {
                    html += `<div class="transcript-line"><span class="transcript-time">${timeMatch[1]}</span></div>`;
                } else if (line.includes('-->')) {
                    // Skip VTT timing lines
                } else {
                    html += `<div class="transcript-line"><span class="transcript-text">${line}</span></div>`;
                }
            });
            transcriptContainer.innerHTML = html || `<pre>${transcriptText}</pre>`;
        } else {
            transcriptContainer.innerHTML = '<p class="mindmap-empty">未找到该视频的字幕/转录内容。</p>';
        }

        // 5. Usage Info
        if (usage) {
            usageInfo.innerHTML = `<span>Prompt: ${usage.prompt_tokens}</span><span>Output: ${usage.completion_tokens}</span><span>Total: ${usage.total_tokens}</span>`;
            usageInfo.style.display = 'flex';
        } else {
            usageInfo.style.display = 'none';
        }

        // Switch to Summary tab
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        document.querySelector('[data-tab="summary"]').classList.add('active');
        document.getElementById('tab-summary').classList.add('active');
    };

    // --- Download & Export Functions ---
    const downloadFile = (filename, content, type = 'text/plain') => {
        const blob = new Blob([content], { type: `${type};charset=utf-8` });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.click();
        URL.revokeObjectURL(a.href);
    };

    const downloadSVG = () => {
        const svg = mermaidContainer.querySelector('svg');
        if (!svg) return alert('没有可导出的思维导图');
        const svgData = new XMLSerializer().serializeToString(svg);
        downloadFile('mindmap.svg', svgData, 'image/svg+xml');
    };

    const downloadPNG = () => {
        const svg = mermaidContainer.querySelector('svg');
        if (!svg) return alert('没有可导出的思维导图');

        const svgData = new XMLSerializer().serializeToString(svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        img.onload = () => {
            // Use higher resolution for better quality
            const scale = 2;
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.scale(scale, scale);
            ctx.drawImage(img, 0, 0);

            canvas.toBlob(blob => {
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'mindmap.png';
                a.click();
                URL.revokeObjectURL(a.href);
            }, 'image/png');
        };

        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    };

    const copyToClipboard = (text, button) => {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.textContent;
            button.textContent = '✅';
            setTimeout(() => button.textContent = originalText, 1500);
        });
    };

    // --- Event Listeners ---
    document.getElementById('download-md-btn')?.addEventListener('click', () => downloadFile('summary.md', currentSummaryRaw));
    document.getElementById('download-txt-btn')?.addEventListener('click', () => downloadFile('summary.txt', currentSummaryRaw));
    document.getElementById('export-mindmap-svg-btn')?.addEventListener('click', downloadSVG);
    document.getElementById('export-mindmap-png-btn')?.addEventListener('click', downloadPNG);
    document.getElementById('copy-summary-btn')?.addEventListener('click', function () { copyToClipboard(currentSummaryRaw, this); });
    document.getElementById('copy-transcript-btn')?.addEventListener('click', function () { copyToClipboard(currentTranscript, this); });

    // PDF Export Function
    const exportToPDF = () => {
        const element = document.getElementById('summary-output');
        if (!element || !window.html2pdf) {
            alert('PDF 导出功能加载中，请稍后再试');
            return;
        }

        const opt = {
            margin: [10, 10, 10, 10],
            filename: 'bili-summary.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        // Clone element to add styling
        const clone = element.cloneNode(true);
        clone.style.padding = '20px';
        clone.style.background = 'white';
        clone.style.color = '#1f2937';

        html2pdf().set(opt).from(clone).save();
    };

    document.getElementById('export-pdf-btn')?.addEventListener('click', exportToPDF);

    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        if (videoUrlInput.value) {
            summarizeForm.dispatchEvent(new Event('submit'));
        }
    });

    clearHistoryBtn?.addEventListener('click', () => {
        if (confirm('确定要清空所有历史记录吗？')) {
            localStorage.removeItem(HISTORY_KEY);
            renderHistory();
        }
    });

    // --- Main Form Submission ---
    if (summarizeForm) {
        summarizeForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const rawInput = videoUrlInput.value;
            const urlMatch = rawInput.match(/(https?:\/\/[^\s]+)/);
            const url = urlMatch ? urlMatch[0] : rawInput;
            if (url !== rawInput) videoUrlInput.value = url;

            const mode = document.getElementById('summarize-mode').value;
            const focus = document.getElementById('analysis-focus').value;

            // Reset UI
            updateProgress(0, "正在连接...");
            loader.style.display = 'block';
            resultContainer.style.display = 'none';
            summarizeError.classList.add('hidden');
            document.getElementById('chat-section')?.classList.remove('show');
            document.getElementById('chat-messages').innerHTML = '';

            // Connection
            updateProgress(5, "正在连接服务器...");

            // Fetch video info in parallel
            fetchVideoInfo(url);

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
                let transcriptText = "";
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
                                const status = data.status;

                                // --- Improved Progress Logic ---
                                if (status === 'complete') {
                                    updateProgress(100, "处理完成！");
                                    summaryText = data.summary;
                                    transcriptText = data.transcript || "";

                                    await displaySummary(summaryText, data.usage, transcriptText);
                                    saveToHistory(url, summaryText, data.usage);

                                    document.getElementById('chat-section')?.classList.add('show');
                                    if (data.cached) {
                                        loaderStatus.textContent = "✅ 已从缓存加载";
                                    }
                                }
                                else if (status.includes('Found in cache')) {
                                    updateProgress(90, "发现缓存，准备渲染...");
                                }
                                else if (status.includes('Downloading')) {
                                    const match = status.match(/(\d+(\.\d+)?)/);
                                    if (match) {
                                        const percent = parseFloat(match[0]);
                                        // 5-40% range
                                        updateProgress(5 + (percent * 0.35), status);
                                    } else {
                                        updateProgress(10, "正在下载视频...");
                                    }
                                }
                                else if (status.includes('Processing subtitles') || status.includes('字幕')) {
                                    updateProgress(45, "正在解析字幕...");
                                }
                                else if (status.includes('Uploading')) {
                                    updateProgress(50, "正在上传至 AI...");
                                }
                                else if (status.includes('uploaded')) {
                                    updateProgress(60, "上传完成，等待 AI 响应...");
                                }
                                else if (status.includes('Cloud processing')) {
                                    updateProgress(70, "云端处理中，请耐心等待...");
                                }
                                else if (status.includes('analyzing') || status.includes('thinking')) {
                                    updateProgress(80, "AI 正在分析核心观点...");
                                }
                                else if (status.includes('Extracting transcript')) {
                                    updateProgress(90, "生成 AI 字幕...");
                                }
                                else {
                                    loaderStatus.textContent = status;
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
                summarizeError.classList.remove('hidden');
                loader.style.display = 'none';
                updateProgress(0, "失败");
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('theme-toggle');
    const THEME_KEY = 'bili_summarizer_theme';

    const initTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.body.classList.add('dark-mode');
            if (themeToggle) themeToggle.textContent = '☀️';
        }
    };

    themeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        themeToggle.textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
    });

    initTheme();

    // --- Video Info Fetch ---
    const fetchVideoInfo = async (url) => {
        currentVideoUrl = url; // Store for video player

        const preview = document.getElementById('video-preview');
        const thumbnail = document.getElementById('video-thumbnail');
        const title = document.getElementById('video-title');
        const meta = document.getElementById('video-meta');

        if (!preview) return;

        preview.classList.remove('show');
        title.textContent = '加载中...';
        meta.textContent = '';
        thumbnail.src = ''; // Reset thumbnail

        try {
            const res = await fetch('/video-info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (res.ok) {
                const info = await res.json();

                // Set thumbnail with fallback on error
                if (info.thumbnail) {
                    thumbnail.src = info.thumbnail;
                    thumbnail.onerror = () => {
                        console.warn('Thumbnail load failed');
                        thumbnail.alt = '封面加载失败';
                    };
                }

                title.textContent = info.title || '未知标题';

                // Fix duration: ensure integer seconds to avoid floating point display
                const totalSeconds = Math.floor(info.duration || 0);
                const durationMin = Math.floor(totalSeconds / 60);
                const durationSec = totalSeconds % 60;
                const formattedDuration = `${durationMin}:${String(durationSec).padStart(2, '0')}`;

                meta.textContent = `${info.uploader || '未知作者'} · ${formattedDuration} · ${(info.view_count || 0).toLocaleString()} 播放`;

                preview.classList.add('show');
            }
        } catch (e) {
            console.warn('Video info fetch failed:', e);
        }
    };

    // --- AI Chat ---
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMessages = document.getElementById('chat-messages');

    const sendChatMessage = async () => {
        const question = chatInput?.value.trim();
        if (!question || !currentSummaryRaw) return;

        // Add user message
        chatMessages.innerHTML += `<div class="chat-message user">${question}</div>`;
        chatInput.value = '';
        chatSendBtn.disabled = true;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, context: currentSummaryRaw })
            });

            if (!res.ok) throw new Error('AI 回复失败');

            const data = await res.json();
            chatMessages.innerHTML += `<div class="chat-message ai">${marked.parse(data.answer)}</div>`;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (e) {
            chatMessages.innerHTML += `<div class="chat-message ai" style="color:var(--danger);">错误: ${e.message}</div>`;
        } finally {
            chatSendBtn.disabled = false;
        }
    };

    chatSendBtn?.addEventListener('click', sendChatMessage);
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // --- Video Player Modal ---
    const videoModal = document.getElementById('video-modal');
    const videoModalClose = document.getElementById('video-modal-close');
    const videoModalIframe = document.getElementById('video-modal-iframe');
    const videoModalTitle = document.getElementById('video-modal-title');
    const videoPreviewPlay = document.getElementById('video-preview-play');

    // Extract BV ID from Bilibili URL
    const getBVid = (url) => {
        const match = url.match(/BV[\w]+/);
        return match ? match[0] : null;
    };

    // Open video player
    const openVideoPlayer = () => {
        if (!currentVideoUrl) return;

        const bvid = getBVid(currentVideoUrl);
        if (!bvid) {
            alert('无法解析视频 ID');
            return;
        }

        // Bilibili embed player URL
        const embedUrl = `https://player.bilibili.com/player.html?bvid=${bvid}&high_quality=1&autoplay=0`;

        videoModalIframe.src = embedUrl;
        videoModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    };

    // Close video player
    const closeVideoPlayer = () => {
        videoModal.classList.remove('active');
        videoModalIframe.src = ''; // Stop playback
        document.body.style.overflow = ''; // Restore scrolling
    };

    // Event listeners
    videoPreviewPlay?.addEventListener('click', openVideoPlayer);
    videoModalClose?.addEventListener('click', closeVideoPlayer);
    videoModal?.addEventListener('click', (e) => {
        if (e.target === videoModal) closeVideoPlayer();
    });

    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && videoModal.classList.contains('active')) {
            closeVideoPlayer();
        }
    });

    // Initialize History
    renderHistory();
});
