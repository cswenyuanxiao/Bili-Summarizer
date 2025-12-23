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

        // 1. Extract Mermaid code and insert placeholder
        const mermaidRegex = /```mermaid([\s\S]*?)```/g;
        currentMermaidCode = "";

        // Check if mermaid block exists
        const hasMermaid = mermaidRegex.test(summaryText);

        const cleanedSummary = summaryText.replace(mermaidRegex, (m, code) => {
            currentMermaidCode += code.trim() + "\n";
            // Return the container placeholder directly in the markdown stream
            return `\n<div id="mermaid-container" class="mermaid-inline"></div>\n`;
        });

        // 2. Render Summary (which now includes the placeholder div)
        summaryOutput.innerHTML = marked.parse(cleanedSummary);

        // 3. Render Mermaid into the inline container
        // Note: mermaidContainer global var needs to be refreshed since we removed the static one
        const inlineContainer = document.getElementById('mermaid-container');

        if (currentMermaidCode && inlineContainer) {
            inlineContainer.innerHTML = ''; // Clear loading text if any
            try {
                const id = `mermaid-diagram-${Date.now()}`;
                const { svg } = await mermaid.render(id, currentMermaidCode);
                inlineContainer.innerHTML = svg;
            } catch (err) {
                console.error("Mermaid rendering failed:", err);
                inlineContainer.innerHTML = `<div style="color:var(--danger); padding:1rem; border:1px dashed var(--danger);">思维导图渲染失败: ${err.message}</div><pre style="text-align:left; overflow-x:auto; font-size:0.8rem;">${currentMermaidCode}</pre>`;
            }
        } else if (inlineContainer) {
            // If container exists but no code (shouldn't happen with regex replace logic, but just in case)
            inlineContainer.innerHTML = '<p class="mindmap-empty">本次总结未生成思维导图。</p>';
        }

        // 4. Render Transcript
        if (transcriptText) {
            // Parse VTT/SRT-like format with timestamps
            const lines = transcriptText.split('\n').filter(l => l.trim());
            let html = '';
            lines.forEach(line => {
                // Support format: "[00:30] Text" or "00:30 Text"
                // Regex looks for optional bracket, then timestamp, then optional bracket
                const timeMatch = line.match(/^\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?/);

                if (timeMatch) {
                    const timeStr = timeMatch[1]; // Get the clean time string "00:30"
                    // Add pointer cursor style to indicate clickability
                    html += `<div class="transcript-line" data-time="${timeStr}" style="cursor:pointer;" title="跳转到 ${timeStr}"><span class="transcript-time">[${timeStr}]</span> <span class="transcript-text">${line.replace(timeMatch[0], '').trim()}</span></div>`;
                } else if (line.includes('-->')) {
                    // Skip VTT timing lines
                } else {
                    html += `<div class="transcript-line"><span class="transcript-text">${line}</span></div>`;
                }
            });
            transcriptContainer.innerHTML = html || `<pre>${transcriptText}</pre>`;

            // Add click listeners for seeking
            document.querySelectorAll('.transcript-line[data-time]').forEach(el => {
                el.addEventListener('click', () => {
                    const timeStr = el.getAttribute('data-time');
                    const seconds = parseTime(timeStr);

                    // If player is not open, open it first
                    if (!videoModal.classList.contains('active')) {
                        openVideoPlayer();
                        // Wait for player to be ready
                        setTimeout(() => {
                            if (localVideoPlayer) localVideoPlayer.currentTime = seconds;
                        }, 500);
                    } else if (localVideoPlayer) {
                        localVideoPlayer.currentTime = seconds;
                        localVideoPlayer.play();
                    }
                });
            });
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
        const container = document.getElementById('mermaid-container');
        const svg = container ? container.querySelector('svg') : null;
        if (!svg) return alert('没有可导出的思维导图');
        const svgData = new XMLSerializer().serializeToString(svg);
        downloadFile('mindmap.svg', svgData, 'image/svg+xml');
    };

    const downloadPNG = () => {
        const container = document.getElementById('mermaid-container');
        const svg = container ? container.querySelector('svg') : null;
        if (!svg) return alert('没有可导出的思维导图');

        // 1. Get accurate dimensions from viewBox
        // Mermaid SVGs usually have a viewBox but width/height might be 100% or max-width
        const viewBox = svg.viewBox.baseVal;
        const width = viewBox ? viewBox.width : svg.getBoundingClientRect().width;
        const height = viewBox ? viewBox.height : svg.getBoundingClientRect().height;

        // 2. Clone and force explicit dimensions
        const clone = svg.cloneNode(true);
        clone.setAttribute('width', width);
        clone.setAttribute('height', height);
        clone.style.backgroundColor = '#ffffff'; // Ensure white background

        const svgData = new XMLSerializer().serializeToString(clone);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        // 3. Load image and draw to canvas with scaling
        img.onload = () => {
            const scale = 3; // High resolution
            canvas.width = width * scale;
            canvas.height = height * scale;

            // White background for PNG
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.scale(scale, scale);
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob(blob => {
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'mindmap.png';
                a.click();
                URL.revokeObjectURL(a.href);
            }, 'image/png');
        };

        // Fix unicode/emoji issues by encoding
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

        // 1. Create a temporary container
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.left = '0';
        container.style.top = '0';
        container.style.width = '820px'; // Approx A4 width
        container.style.zIndex = '-9999';
        container.style.opacity = '0';
        container.style.background = '#ffffff';
        container.style.padding = '40px';
        container.style.boxSizing = 'border-box';

        // 2. Clone and clean content
        const clone = element.cloneNode(true);
        clone.style.height = 'auto';
        clone.style.overflow = 'visible';
        clone.style.color = '#111827'; // Dark text
        clone.style.backgroundColor = '#ffffff';

        // Special fix for elements that might have inherited white color in dark mode
        const allElements = clone.querySelectorAll('*');
        allElements.forEach(el => {
            el.style.color = '#111827';
            if (el.tagName === 'CODE' || el.tagName === 'PRE') {
                el.style.backgroundColor = '#f3f4f6';
                el.style.padding = '4px';
                el.style.borderRadius = '4px';
                el.style.color = '#111827';
            }
        });

        container.appendChild(clone);
        document.body.appendChild(container);

        // 3. Capture with options
        const opt = {
            margin: 10,
            filename: 'summarization.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: {
                scale: 2,
                useCORS: true,
                logging: false,
                letterRendering: true,
                scrollY: 0
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        // Give it a bit more time to settle (async layout)
        setTimeout(() => {
            html2pdf().set(opt).from(container).save().then(() => {
                document.body.removeChild(container);
            }).catch(err => {
                console.error("PDF Export Error:", err);
                if (document.body.contains(container)) document.body.removeChild(container);
            });
        }, 500);
    };

    document.getElementById('export-pdf-btn')?.addEventListener('click', exportToPDF);

    // PPT Export
    const exportPPTBtn = document.getElementById('export-ppt-btn');
    exportPPTBtn?.addEventListener('click', async () => {
        if (!currentSummaryRaw) return alert('请先生成视频总结');

        const originalText = exportPPTBtn.innerHTML;
        exportPPTBtn.disabled = true;
        exportPPTBtn.innerHTML = '🎥 生成中...';

        try {
            const response = await fetch('/generate-ppt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ summary: currentSummaryRaw })
            });

            if (!response.ok) throw new Error('生成失败');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `bili-summary-ppt-${Date.now()}.pptx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            exportPPTBtn.innerHTML = '✅ 生成成功';
            setTimeout(() => {
                exportPPTBtn.innerHTML = originalText;
                exportPPTBtn.disabled = false;
            }, 2000);

        } catch (e) {
            console.error(e);
            alert('PPT 生成失败: ' + e.message);
            exportPPTBtn.innerHTML = originalText;
            exportPPTBtn.disabled = false;
        }
    });

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

                            if (data.type) {
                                const type = data.type;
                                const payload = data.data || data; // Handle both wrapper formats if any

                                if (type === 'status') {
                                    const status = data.data || data.status;
                                    // Handle legacy string status matching for progress bar
                                    if (status.includes('Found in cache')) {
                                        updateProgress(90, "发现缓存，加载中...");
                                    } else if (status.includes('Downloading')) {
                                        const match = status.match(/(\d+(\.\d+)?)/);
                                        if (match) {
                                            updateProgress(5 + (parseFloat(match[0]) * 0.35), status);
                                        } else {
                                            updateProgress(10, "正在下载视频...");
                                        }
                                    } else if (status.includes('Parallel Analysis')) {
                                        updateProgress(75, "🚀 并行分析中：总结+转录...");
                                    } else {
                                        loaderStatus.textContent = status;
                                    }
                                }
                                else if (type === 'video_downloaded') {
                                    // Video is ready! Enable player.
                                    currentLocalVideoFile = data.video_file || (data.data && data.data.filename);
                                    updateProgress(45, "🎥 视频就绪！AI正在思考...");
                                    console.log("Video ready:", currentLocalVideoFile);
                                    // Optionally trigger a toast or small notification here
                                }
                                else if (type === 'transcript_complete') {
                                    // Transcript is ready! Render it.
                                    transcriptText = data.transcript || (data.data && data.data.transcript) || data.data; // Flexible parsing
                                    updateProgress(80, "📝 字幕已生成！保持耐心...");

                                    // Render transcript (partial update)
                                    // We need to call displaySummary but with emptiness for others?
                                    // Actually displaySummary clears everything. Let's create a partial renderer or just call the main one.
                                    // calling displaySummary will render what we have so far.
                                    // But we need to make sure summaryText is preserved or passed as empty string if not ready.
                                    await displaySummary(summaryText, null, transcriptText);
                                }
                                else if (type === 'summary_complete') {
                                    // Summary is ready!
                                    summaryText = data.summary || (data.data && data.data.summary) || data.data;
                                    const usage = data.usage || (data.data && data.data.usage);

                                    updateProgress(95, "🧠 总结生成完毕！正在最终整理...");
                                    await displaySummary(summaryText, usage, transcriptText);
                                    saveToHistory(url, summaryText, usage);
                                }
                                else if (type === 'error') {
                                    throw new Error(data.error || data.data);
                                }
                            }
                            // Legacy/Standard Status Fallback
                            else if (data.status) {
                                const status = data.status;
                                if (status === 'complete') {
                                    updateProgress(100, "处理完成！");
                                    // ... existing complete logic ...
                                    // Re-implement the complete logic here or ensure it's covered
                                    // Since the previous block was just "else if (data.status === 'complete')", 
                                    // we can just stick to the original logic structure but ensuring we catch other statuses.
                                    summaryText = data.summary;
                                    transcriptText = data.transcript || "";
                                    currentLocalVideoFile = data.video_file || null;

                                    await displaySummary(summaryText, data.usage, transcriptText);
                                    saveToHistory(url, summaryText, data.usage);

                                    document.getElementById('chat-section')?.classList.add('show');
                                    if (data.cached) {
                                        loaderStatus.textContent = "✅ 已从缓存加载";
                                    }
                                } else {
                                    // Handle generic status messages (e.g. "Checking for subtitles...", "Downloading...")
                                    // Reuse the logic we put inside type==='status'
                                    if (status.includes('Found in cache')) {
                                        updateProgress(90, "发现缓存，加载中...");
                                    } else if (status.includes('Downloading')) {
                                        const match = status.match(/(\d+(\.\d+)?)/);
                                        if (match) {
                                            updateProgress(5 + (parseFloat(match[0]) * 0.35), status);
                                        } else {
                                            updateProgress(10, "正在下载视频...");
                                        }
                                    } else if (status.includes('Parallel Analysis')) {
                                        updateProgress(75, "🚀 并行分析中：总结+转录...");
                                    } else {
                                        loaderStatus.textContent = status;
                                    }
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

    // --- Video Player & Transcript Sync ---
    const videoModal = document.getElementById('video-modal');
    const videoModalClose = document.getElementById('video-modal-close');
    const videoModalBody = document.querySelector('.video-modal-body'); // Container
    const videoPreviewPlay = document.getElementById('video-preview-play');

    let localVideoPlayer = null; // HTMLVideoElement
    let currentLocalVideoFile = null;

    // Helper to parse time string "MM:SS" to seconds
    const parseTime = (timeStr) => {
        const parts = timeStr.split(':');
        if (parts.length === 2) {
            return parseInt(parts[0]) * 60 + parseInt(parts[1]);
        }
        if (parts.length === 3) {
            return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
        }
        return 0;
    };

    // Open video player (prefer local, fallback to iframe)
    const openVideoPlayer = (startTime = 0) => {
        // If modal matches current state, just seek (optimize for avoiding reload)
        if (videoModal.classList.contains('active')) {
            if (localVideoPlayer) {
                localVideoPlayer.currentTime = startTime;
                localVideoPlayer.play();
                return;
            }
        }

        videoModalBody.innerHTML = ''; // Clear previous content
        localVideoPlayer = null;

        if (currentLocalVideoFile) {
            // Use local video player
            localVideoPlayer = document.createElement('video');
            localVideoPlayer.src = `/videos/${currentLocalVideoFile}`;
            localVideoPlayer.controls = true;
            localVideoPlayer.style.width = '100%';
            localVideoPlayer.style.height = '100%';
            // Remove autoplay attribute here, handle play in event listener for better control
            // localVideoPlayer.autoplay = true; 

            // Critical: Wait for metadata to load before seeking
            localVideoPlayer.addEventListener('loadedmetadata', () => {
                if (startTime > 0) {
                    localVideoPlayer.currentTime = startTime;
                }
                localVideoPlayer.play();
            }, { once: true });

            videoModalBody.appendChild(localVideoPlayer);
            setupTranscriptSync(localVideoPlayer);

        } else if (currentVideoUrl) {
            // Fallback to Bilibili Iframe
            const bvid = getBVid(currentVideoUrl);
            if (bvid) {
                const iframe = document.createElement('iframe');
                // Append t parameter for start time
                iframe.src = `https://player.bilibili.com/player.html?bvid=${bvid}&high_quality=1&autoplay=1&t=${startTime}`;
                iframe.allowFullscreen = true;
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                iframe.style.position = 'absolute';
                iframe.style.top = '0';
                iframe.style.left = '0';
                videoModalBody.appendChild(iframe);
            } else {
                return alert('无法播放：未找到视频源');
            }
        } else {
            return;
        }

        videoModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    // Sync transcript with video
    const setupTranscriptSync = (video) => {
        const lines = document.querySelectorAll('.transcript-line');
        if (!lines.length) return;

        // Auto-scroll logic
        video.ontimeupdate = () => {
            const currentTime = video.currentTime;

            // Find active line
            let activeLine = null;
            lines.forEach((line) => {
                const timeStr = line.getAttribute('data-time'); // "00:30"
                if (timeStr) {
                    const seconds = parseTime(timeStr);
                    if (seconds <= currentTime) {
                        activeLine = line;
                    }
                }
            });

            // Highlight and scroll
            lines.forEach(l => l.classList.remove('active-line'));
            if (activeLine) {
                activeLine.classList.add('active-line');

                // Smooth scroll to keep active line in view
                activeLine.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        };
    };

    // Close video player
    const closeVideoPlayer = () => {
        videoModal.classList.remove('active');
        videoModalBody.innerHTML = ''; // Stop playback
        localVideoPlayer = null;
        document.body.style.overflow = '';
    };

    // Extract BV ID from Bilibili URL
    const getBVid = (url) => {
        const match = url.match(/BV[\w]+/);
        return match ? match[0] : null;
    };

    // Event listeners
    videoPreviewPlay?.addEventListener('click', () => openVideoPlayer(0));
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
