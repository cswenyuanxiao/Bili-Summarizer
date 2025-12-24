<template>
  <div id="app" class="relative">
    <div class="aurora" aria-hidden="true">
      <div class="aurora-blob top-[-120px] left-1/2 -translate-x-1/2 bg-[#f59e0b]/70"></div>
      <div class="aurora-blob is-secondary top-24 right-[-120px] bg-[#60a5fa]/70"></div>
      <div class="aurora-blob is-tertiary top-[360px] left-[-80px] bg-[#22d3ee]/70"></div>
    </div>

    <header class="relative z-40 overflow-hidden">
      <div class="hero-glow" aria-hidden="true"></div>
      <div class="hero-fade" aria-hidden="true"></div>
      <div class="sticky top-0 z-40 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-gray-200/70 dark:border-slate-800/70">
        <div class="container mx-auto max-w-6xl px-4 sm:px-6">
          <div class="flex items-center justify-between h-14 sm:h-16">
            <div class="flex items-center gap-3">
              <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-cyan-400 text-white font-semibold">✨</div>
              <div class="text-base sm:text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100">Bili-Summarizer</div>
            </div>

            <nav class="hidden lg:flex items-center gap-6 text-sm text-gray-600 dark:text-gray-300">
              <div class="relative group">
                <button @click="scrollToSection('product')" class="hover:text-gray-900 dark:hover:text-white transition-colors">产品</button>
                <div class="absolute left-0 top-full mt-4 w-72 rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white/95 dark:bg-slate-900/95 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <div class="p-4 space-y-2">
                    <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">核心能力</div>
                    <p class="text-xs text-gray-500">总结 · 转录 · 思维导图 · AI 追问</p>
                    <div class="text-xs text-gray-400">一站式视频信息提炼与复盘。</div>
                  </div>
                </div>
              </div>
              <button @click="scrollToSection('pricing')" class="hover:text-gray-900 dark:hover:text-white transition-colors">方案</button>
              <button @click="scrollToSection('docs')" class="hover:text-gray-900 dark:hover:text-white transition-colors">使用文档</button>
              <button @click="requireAuth(() => scrollToSection('dashboard'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">仪表盘</button>
              <button @click="requireAuth(() => scrollToSection('billing'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">账单</button>
              <button @click="requireAuth(() => scrollToSection('invite'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">邀请好友</button>
              <button @click="requireAuth(() => $router.push('/templates'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">总结模板</button>
              <button @click="requireAuth(() => $router.push('/subscriptions'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">每日推送</button>
              <button @click="requireAuth(() => $router.push('/compare'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">总结对比</button>
              <button @click="requireAuth(() => $router.push('/teams'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">团队协作</button>
              <button @click="requireAuth(() => scrollToSection('developer'))" class="hover:text-gray-900 dark:hover:text-white transition-colors">开发者 API</button>
            </nav>

            <div class="flex items-center gap-3">
              <button
                @click="toggleTheme"
                class="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800 text-lg hover:scale-105 transition-transform"
                title="切换主题"
              >
                {{ isDark ? '☀️' : '🌙' }}
              </button>

              <div v-if="user" ref="userMenuRef" class="relative">
                <button
                  class="flex items-center gap-2 focus:outline-none"
                  :aria-expanded="showUserMenu"
                  aria-haspopup="menu"
                  @click="toggleUserMenu"
                >
                  <img 
                    :src="user.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.email?.charAt(0) || 'U')}&background=4f46e5&color=fff`" 
                    :alt="user.email"
                    class="w-9 h-9 rounded-full border-2 border-white/30 hover:border-primary transition-colors shadow-md"
                    @error="(e: Event) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=U&background=4f46e5&color=fff' }"
                  />
                </button>
                
                <div
                  v-show="showUserMenu"
                  class="absolute top-full right-0 mt-2 w-56 glass-card rounded-xl overflow-hidden border border-white/40 z-50"
                  role="menu"
                >
                  <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-200 truncate">{{ user.email }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">{{ planLabel }}</span>
                      <button @click="showPricingModal = true; showUserMenu = false" class="text-xs text-primary hover:underline">升级</button>
                    </div>
                  </div>
                  <button 
                    @click="showPricingModal = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between group/item"
                  >
                    <span>升级 Pro</span>
                    <span class="text-xs bg-gradient-to-r from-primary to-purple-500 text-white px-1.5 py-0.5 rounded">HOT</span>
                  </button>
                  <button
                    @click="openDashboard"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    仪表盘
                  </button>
                  <button
                    @click="openBilling"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    账单与发票
                  </button>
                  <button
                    @click="showInviteModal = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    邀请好友
                  </button>
                  <button
                    @click="$router.push('/templates'); showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    总结模板
                  </button>
                  <button
                    @click="$router.push('/subscriptions'); showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    每日推送
                  </button>
                  <button
                    @click="$router.push('/compare'); showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    总结对比
                  </button>
                  <button
                    @click="$router.push('/teams'); showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    团队协作
                  </button>
                  <button 
                    @click="showApiKeyModal = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    开发者 API
                  </button>
                  <button
                    @click="showUsageGuide = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    使用文档
                  </button>
                  <button 
                    @click="handleLogout"
                    class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    退出登录
                  </button>
                </div>
              </div>

              <button 
                v-else
                @click="showLoginModal = true" 
                class="px-4 py-2 rounded-full bg-gray-900 text-white text-sm font-medium hover:shadow-lg transition-all"
              >
                登录 / 注册
              </button>

              <button
                ref="mobileMenuButtonRef"
                class="lg:hidden w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800"
                @click="showMobileMenu = !showMobileMenu"
              >
                ☰
              </button>
            </div>
          </div>
          <div v-if="showMobileMenu" ref="mobileMenuRef" class="lg:hidden pb-4">
            <div class="rounded-2xl glass-card p-4 space-y-2 text-sm text-gray-700 dark:text-gray-200">
              <button class="w-full text-left" @click="scrollToSection('product'); showMobileMenu = false">产品</button>
              <button class="w-full text-left" @click="scrollToSection('pricing'); showMobileMenu = false">方案</button>
              <button class="w-full text-left" @click="scrollToSection('docs'); showMobileMenu = false">使用文档</button>
              <button class="w-full text-left" @click="requireAuth(() => { scrollToSection('dashboard'); showMobileMenu = false })">仪表盘</button>
              <button class="w-full text-left" @click="requireAuth(() => { scrollToSection('billing'); showMobileMenu = false })">账单与发票</button>
              <button class="w-full text-left" @click="requireAuth(() => { scrollToSection('invite'); showMobileMenu = false })">邀请好友</button>
              <button class="w-full text-left" @click="requireAuth(() => { scrollToSection('developer'); showMobileMenu = false })">开发者 API</button>
            </div>
          </div>
        </div>
      </div>

      <div class="container mx-auto max-w-6xl px-4 py-12 sm:py-14 lg:py-16 relative z-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-center">
          <div class="space-y-5 sm:space-y-6">
            <span class="fade-up inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <span class="w-6 h-[2px] bg-primary"></span>
              视频理解新方式
            </span>
            <h1 class="fade-up delay-1 text-3xl sm:text-4xl lg:text-5xl font-semibold text-gray-900 dark:text-gray-100 leading-tight">
              用 AI 把长视频拆成可执行的知识模块
            </h1>
            <p class="fade-up delay-2 text-base sm:text-lg text-gray-600 dark:text-gray-300">
              一键总结、结构化思维导图与时间戳转录，把 B 站内容变成可复盘的工作流。
            </p>
            <div class="fade-up delay-3 flex flex-wrap gap-3">
              <button
                @click="scrollToStart"
                class="px-6 py-3 rounded-full bg-primary text-white text-sm font-medium primary-shadow hover:-translate-y-0.5 transition"
              >
                立即开始
              </button>
              <button
                @click="showUsageGuide = true"
                class="px-6 py-3 rounded-full border border-gray-300 dark:border-slate-700 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800 transition"
              >
                了解使用方式
              </button>
            </div>
            <div class="fade-up delay-3 flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400">
              <span class="badge-pill">⚡ 平均 1 分钟出结果</span>
              <span class="badge-pill">🧠 思维导图自动生成</span>
              <span class="badge-pill">📄 支持 PDF/PNG 导出</span>
            </div>
          </div>
          <div class="relative fade-up delay-2">
            <div class="absolute -top-8 -left-6 h-24 w-24 rounded-2xl bg-primary/10 blur-xl"></div>
            <div class="glass-card rounded-3xl p-5 sm:p-6">
              <div class="text-sm text-gray-500 mb-3">实时流程预览</div>
              <div class="space-y-3 text-sm">
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>字幕识别</span>
                  <span class="text-primary font-semibold">✔</span>
                </div>
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>结构化总结</span>
                  <span class="text-primary font-semibold">进行中</span>
                </div>
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>思维导图渲染</span>
                  <span class="text-gray-400">等待</span>
                </div>
              </div>
              <div class="mt-4 text-xs text-gray-400">支持云端历史与多端同步</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="min-h-screen pb-20">
      <div class="container mx-auto max-w-6xl px-4">
        <div class="flex flex-col gap-[var(--section-gap)]">
          <!-- URL Input Card -->
          <div id="start" data-reveal class="flex flex-col gap-6 -mt-10 sm:-mt-14 lg:-mt-16">
            <div class="fade-up delay-1 relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-2xl glass-card px-4 py-3 text-xs sm:text-sm text-gray-600 dark:text-gray-300">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-900 dark:text-gray-100">当前积分</span>
                <span>{{ creditsLabel }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-900 dark:text-gray-100">每次消耗</span>
                <span>{{ costPerSummary }} 积分</span>
              </div>
            </div>
            <UrlInputCard 
              :is-loading="isLoading" 
              @submit="handleSummarize" 
            />
            <div
              v-if="!user"
              class="rounded-2xl border border-blue-100/80 bg-blue-50/80 px-4 py-3 text-sm text-blue-700 dark:border-blue-500/40 dark:bg-blue-950/40 dark:text-blue-200"
            >
              <div class="font-semibold">请先登录</div>
              <div class="mt-1 text-xs opacity-80">登录后才可生成总结并使用云端同步与积分体系。</div>
              <button
                class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
                @click="showLoginModal = true"
              >
                去登录
              </button>
            </div>
            <div
              v-if="phase === 'error'"
              class="rounded-2xl border border-red-200/80 bg-red-50/80 px-4 py-3 text-sm text-red-700 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-200"
            >
              <div class="font-semibold">{{ status || '请求失败' }}</div>
              <div class="mt-1 text-xs opacity-80">{{ hint || '请稍后再试' }}</div>
              <div v-if="detail" class="mt-1 text-xs opacity-70">{{ detail }}</div>
              <div v-if="errorCode === 'CREDITS_EXCEEDED'" class="mt-1 text-xs opacity-70">
                若你使用管理员账号但仍受限，请确认服务端已配置 `ADMIN_EMAILS`。
              </div>
              <button
                v-if="errorCode === 'CREDITS_EXCEEDED'"
                class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
                @click="showPricingModal = true"
              >
                去升级以获取更多积分
              </button>
              <button
                v-if="errorCode === 'AUTH_REQUIRED' || errorCode === 'AUTH_INVALID'"
                class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
                @click="showLoginModal = true"
              >
                去登录
              </button>
            </div>
        </div>

          <!-- Loading Overlay -->
          <LoadingOverlay
            :show="isLoading"
            :status="status"
            :hint="hint"
            :detail="detail"
            :progress="progress"
            :steps="loadingSteps"
            :active-step="activeStep"
            :elapsed="elapsedSeconds"
            :phase-note="phaseNote"
          />

          <!-- Results -->
          <div v-if="result.summary || result.transcript" class="results-section flex flex-col gap-8" data-reveal>
            <!-- Mermaid Mindmap -->
            <MindmapViewer
              v-if="extractedMindmap"
              ref="mindmapRef"
              :diagram="extractedMindmap"
              @export-svg="exportMindmap('svg')"
              @export-png="exportMindmap('png')"
            />

            <!-- Two Column Layout -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <!-- Left Column: Transcript -->
              <div class="lg:col-span-1">
                <TranscriptPanel
                  :content="result.transcript"
                  :video-url="currentVideoUrl"
                  :video-file="result.videoFile"
                  :video-info="videoInfo"
                  @copy="copyTranscript"
                />
              </div>

              <!-- Right Column: Summary -->
              <div class="lg:col-span-2 space-y-6">
                <SummaryCard
                  :content="result.summary"
                  :loading="isLoading"
                  @copy="copySummary"
                  @refresh="handleResummarize"
                />
                
                <ExportBar @export="handleExport" />
              </div>
            </div>
            
            <!-- AI 追问面板 -->
            <ChatPanel
              v-if="result.summary"
              :summary="result.summary"
              :transcript="result.transcript || ''"
            />
          </div>

          <!-- History -->
          <div data-reveal data-delay="200">
            <HistoryList
              :items="historyItems"
              @select="loadFromHistory"
              @clear="clearHistory"
              @guide="showUsageGuide = true"
              @share="shareHistoryItem"
            />
          </div>

          <!-- Product -->
          <section id="product" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-6">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">产品</h2>
              <button class="text-sm text-primary hover:underline" @click="scrollToStart">立即体验</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 dark:text-gray-300">
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">快速总结</div>
                <div class="mt-2 text-xs text-gray-500">一键生成结构化摘要与关键要点。</div>
              </div>
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">转录与时间戳</div>
                <div class="mt-2 text-xs text-gray-500">自动生成字幕与时间索引。</div>
              </div>
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">思维导图</div>
                <div class="mt-2 text-xs text-gray-500">将总结整理为清晰的知识图谱。</div>
              </div>
            </div>
          </section>

          <!-- Pricing -->
          <section id="pricing" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-6">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">方案</h2>
              <button class="text-sm text-primary hover:underline" @click="showPricingModal = true">查看购买</button>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300">
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-6">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Starter Pack</div>
                <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥1</div>
                <div class="mt-1 text-xs text-gray-500">30 积分 / 适合轻度使用</div>
              </div>
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-6">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro Pack</div>
                <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥3</div>
                <div class="mt-1 text-xs text-gray-500">120 积分 / 高频总结</div>
              </div>
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-6">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro 专业版</div>
                <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥29.9</div>
                <div class="mt-1 text-xs text-gray-500">月付 / 无限次总结</div>
              </div>
            </div>
          </section>

          <!-- Docs -->
          <section id="docs" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-6">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">使用文档</h2>
              <button class="text-sm text-primary hover:underline" @click="showUsageGuide = true">查看完整指南</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300">
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">快速上手</div>
                <ol class="mt-2 space-y-1 text-xs text-gray-500 list-decimal list-inside">
                  <li>登录后获取积分</li>
                  <li>粘贴 B 站链接生成总结</li>
                  <li>保存、导出或分享结果</li>
                </ol>
              </div>
              <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5">
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">常见问题</div>
                <div class="mt-2 text-xs text-gray-500">如果提示积分不足，可通过套餐购买或订阅升级。</div>
              </div>
            </div>
          </section>

          <!-- Dashboard -->
          <section id="dashboard" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">仪表盘</h2>
              <button class="text-sm text-primary hover:underline" @click="requireAuth(openDashboard)">打开仪表盘</button>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">
              查看剩余积分、使用趋势与订阅状态。
            </div>
          </section>

          <!-- Billing -->
          <section id="billing" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">账单</h2>
              <button class="text-sm text-primary hover:underline" @click="requireAuth(openBilling)">查看账单</button>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">
              查看订阅与一次性额度包的支付记录，支持发票下载。
            </div>
          </section>

          <!-- Invite -->
          <section id="invite" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">邀请好友</h2>
              <button class="text-sm text-primary hover:underline" @click="requireAuth(() => showInviteModal = true)">生成邀请码</button>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">
              分享邀请码，双方各获得 10 积分奖励。
            </div>
          </section>

          <!-- Developer API -->
          <section id="developer" data-reveal class="rounded-3xl glass-card p-8 sm:p-10 space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">开发者 API</h2>
              <button class="text-sm text-primary hover:underline" @click="requireAuth(() => showApiKeyModal = true)">管理 API Key</button>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-300">
              通过 API Key 将总结能力集成到你的应用或工作流。
            </div>
          </section>
        </div>
      </div>
    </main>

    <LoginModal :show="showLoginModal" @close="showLoginModal = false" />
    <PricingModal :show="showPricingModal" @close="showPricingModal = false" />
    <ApiKeyModal :show="showApiKeyModal" @close="showApiKeyModal = false" />
    <DashboardModal
      :show="showDashboard"
      :loading="dashboardLoading"
      :error="dashboardError"
      :data="dashboardData"
      :subscription="subscriptionData"
      @close="showDashboard = false"
      @refresh="fetchDashboard"
      @upgrade="showPricingModal = true"
    />
    <InviteModal
      :show="showInviteModal"
      @close="showInviteModal = false"
      @refreshed="fetchDashboard"
    />
    <BillingModal
      :show="showBillingModal"
      :loading="billingLoading"
      :error="billingError"
      :items="billingItems"
      @close="showBillingModal = false"
    />
    <UsageGuideModal :show="showUsageGuide" @close="showUsageGuide = false" />

    <footer class="bg-gray-100 dark:bg-gray-800 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
      <div class="container mx-auto">
        <p>
          Powered by <a href="https://ai.google.dev/" target="_blank" class="text-primary hover:underline">Google Gemini</a> · Built with ❤️
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { marked } from 'marked'
import html2pdf from 'html2pdf.js'
import UrlInputCard from './components/UrlInputCard.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import SummaryCard from './components/SummaryCard.vue'
import TranscriptPanel from './components/TranscriptPanel.vue'
import MindmapViewer from './components/MindmapViewer.vue'
import ChatPanel from './components/ChatPanel.vue'
import ExportBar from './components/ExportBar.vue'
import HistoryList from './components/HistoryList.vue'
import LoginModal from './components/LoginModal.vue'
import PricingModal from './components/PricingModal.vue'
import ApiKeyModal from './components/ApiKeyModal.vue'
import DashboardModal from './components/DashboardModal.vue'
import BillingModal from './components/BillingModal.vue'
import InviteModal from './components/InviteModal.vue'
import UsageGuideModal from './components/UsageGuideModal.vue'
import { useSummarize } from './composables/useSummarize'
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import { useHistorySync } from './composables/useHistorySync'
import { useReveal } from './composables/useReveal'
import type { SummarizeRequest } from './types/api'
import { isSupabaseConfigured, supabase } from './supabase'

// Theme management
const { isDark, toggleTheme, initTheme } = useTheme()
const { refresh: refreshReveal } = useReveal()

onMounted(async () => {
  initTheme()
  await nextTick()
  refreshReveal()
})


// Auth management
const { user, logout } = useAuth()
const showLoginModal = ref(false)
const showPricingModal = ref(false)
const showApiKeyModal = ref(false)
const showDashboard = ref(false)
const showBillingModal = ref(false)
const showInviteModal = ref(false)
const showUsageGuide = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const mobileMenuRef = ref<HTMLElement | null>(null)
const mobileMenuButtonRef = ref<HTMLElement | null>(null)
const currentVideoUrl = ref('')
type VideoInfo = {
  title: string
  thumbnail: string
  duration: number
  uploader: string
  view_count: number
}

const videoInfo = ref<VideoInfo | null>(null)
const requireAuth = (action: () => any) => {
  if (!user.value) {
    showLoginModal.value = true
    return
  }
  action()
}
const mindmapRef = ref<InstanceType<typeof MindmapViewer> | null>(null)
const dashboardLoading = ref(false)
const dashboardError = ref('')
const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
  daily_usage?: { day: string; count: number }[]
  email?: string | null
} | null>(null)
const subscriptionData = ref<{
  plan: string
  status: string
  current_period_end?: string | null
} | null>(null)
const billingLoading = ref(false)
const billingError = ref('')
const billingItems = ref<Array<{
  id: string
  amount_cents: number
  currency: string
  status: string
  period_start?: string | null
  period_end?: string | null
  invoice_url?: string | null
  created_at?: string | null
}>>([])

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

// Summarization logic
const { isLoading, status, hint, detail, progress, phase, elapsedSeconds, errorCode, result, summarize } = useSummarize()

// Ensure animations trigger when results appear
watch(() => result.value.summary, (newVal) => {
  if (newVal) {
    nextTick(() => {
      refreshReveal()
    })
    if (user.value) {
      fetchDashboard().catch(() => undefined)
    }
  }
})

// Cloud history sync
const { syncToCloud, addHistoryItem, getLocalHistory, clearHistory: clearHistorySync } = useHistorySync()
const lastRequest = ref<SummarizeRequest | null>(null)

// History - convert cloud format to display format
const rawHistory = ref(getLocalHistory())
const displayHistory = computed(() => {
  return rawHistory.value.map(item => ({
    id: item.id || item.video_url,
    title: item.video_title || extractTitle(item.summary),
    mode: item.mode as 'smart' | 'video',
    timestamp: item.created_at ? new Date(item.created_at).getTime() : Date.now(),
    url: item.video_url,
    summary: item.summary,
    transcript: item.transcript || '',
    mindmap: item.mindmap || ''
  }))
})

const historyItems = displayHistory // Alias for compatibility

const handleSummarize = async (request: SummarizeRequest) => {
  if (!user.value) {
    showLoginModal.value = true
    return
  }
  lastRequest.value = request
  currentVideoUrl.value = request.url
  videoInfo.value = null
  fetchVideoInfo(request.url)
  await summarize(request)
  
  // Save to history after completion
  if (result.value.summary) {
    const currentInfo = videoInfo.value as VideoInfo | null
    addHistoryItem({
      video_url: request.url,
      video_title: currentInfo?.title || '',
      video_thumbnail: currentInfo?.thumbnail || '',
      mode: request.mode,
      focus: request.focus,
      summary: result.value.summary,
      transcript: result.value.transcript,
      mindmap: extractedMindmap.value || ''
    })
    
    // Refresh history display
    rawHistory.value = getLocalHistory()
    
    // Sync to cloud if logged in
    if (user.value) {
      syncToCloud().catch(err => console.error('Sync failed:', err))
    }
  }
}

const handleResummarize = async () => {
  if (!lastRequest.value || isLoading.value) return
  await summarize({ ...lastRequest.value, skip_cache: true })
}

const extractTitle = (summary: string) => {
  const firstLine = summary.split('\n')[0]
  return firstLine?.replace(/^#+ /, '').trim() || '未命名总结'
}

// Robust Mermaid Diagram Extraction
const extractedMindmap = computed(() => {
  if (!result.value.summary) return ''
  
  // 1. Standard pattern: ```mermaid ... ```
  const standardMatch = result.value.summary.match(/```mermaid[\s\S]*?\n([\s\S]*?)\n```/)
  if (standardMatch?.[1]) return standardMatch[1].trim()
  
  // 2. Fallback: Check for graph/mindmap/pie keywords if backticks are missing
  const fallbackMatch = result.value.summary.match(/(graph\s+(?:TD|LR|TB|BT)[\s\S]*|mindmap[\s\S]*|pie[\s\S]*)/i)
  if (fallbackMatch) return fallbackMatch[0].trim()
  
  return ''
})

const loadingSteps = ['连接', '下载/字幕', 'AI 分析', '整理结果']
const activeStep = computed(() => {
  switch (phase.value) {
    case 'connecting':
      return 0
    case 'downloading':
    case 'transcript':
      return 1
    case 'summarizing':
      return 2
    case 'finalizing':
    case 'complete':
      return 3
    default:
      return -1
  }
})

const phaseNote = computed(() => {
  switch (phase.value) {
    case 'connecting':
      return { title: '建立连接', body: '正在创建会话并与服务器握手。' }
    case 'downloading':
      return { title: '获取素材', body: '拉取视频/音频与字幕，准备进入分析。' }
    case 'transcript':
      return { title: '生成字幕', body: '识别并整理可读的转录文本。' }
    case 'summarizing':
      return { title: 'AI 分析', body: '模型提炼重点并构建结构化内容。' }
    case 'finalizing':
      return { title: '整理结果', body: '汇总输出并渲染思维导图。' }
    case 'complete':
      return { title: '完成', body: '结果已就绪，可以开始查看。' }
    case 'error':
      return { title: '出现问题', body: '连接或处理失败，请稍后重试。' }
    default:
      return null
  }
})

const handleDocumentClick = (event: MouseEvent) => {
  if (!showUserMenu.value || !userMenuRef.value) return
  const target = event.target as Node | null
  if (target && userMenuRef.value.contains(target)) return
  showUserMenu.value = false
}

const handleMobileMenuClick = (event: MouseEvent) => {
  if (!showMobileMenu.value || !mobileMenuRef.value) return
  const target = event.target as Node | null
  if (target && mobileMenuButtonRef.value?.contains(target)) return
  if (target && mobileMenuRef.value.contains(target)) return
  showMobileMenu.value = false
}

const handleDocumentKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLogout = async () => {
  try {
    await logout()
    showUserMenu.value = false
  showPricingModal.value = false
  showApiKeyModal.value = false
  showDashboard.value = false
  showBillingModal.value = false
  showInviteModal.value = false
  showUsageGuide.value = false
  showLoginModal.value = false
  } catch (error: any) {
    alert(`退出登录失败: ${error?.message || '未知错误'}`)
  }
}

const fetchDashboard = async () => {
  if (!user.value) {
    dashboardData.value = null
    return
  }
  if (!isSupabaseConfigured) {
    dashboardError.value = '登录服务未配置'
    dashboardData.value = null
    return
  }
  dashboardLoading.value = true
  dashboardError.value = ''
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // 改进：先检查响应状态，再尝试解析
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取仪表盘失败')
      } catch (parseError) {
        // JSON 解析失败，使用状态码
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    
    dashboardData.value = await response.json()
  } catch (error: any) {
    dashboardError.value = error?.message || '获取仪表盘失败'
  } finally {
    dashboardLoading.value = false
  }
}

const fetchSubscription = async () => {
  if (!user.value) {
    subscriptionData.value = null
    return
  }
  if (!isSupabaseConfigured) {
    subscriptionData.value = null
    return
  }
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/subscription', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取订阅信息失败')
      } catch (parseError) {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    
    subscriptionData.value = await response.json()
  } catch (error) {
    subscriptionData.value = null
  }
}

const fetchBilling = async () => {
  if (!user.value) {
    billingItems.value = []
    return
  }
  if (!isSupabaseConfigured) {
    billingError.value = '登录服务未配置'
    billingItems.value = []
    return
  }
  billingLoading.value = true
  billingError.value = ''
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/billing', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取账单失败')
      } catch (parseError) {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    
    billingItems.value = await response.json()
  } catch (error: any) {
    billingError.value = error?.message || '获取账单失败'
  } finally {
    billingLoading.value = false
  }
}

const openDashboard = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showDashboard.value = true
  await fetchDashboard()
}

const openBilling = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showBillingModal.value = true
  await fetchBilling()
}

const shareHistoryItem = async (item: {
  title: string
  summary: string
  transcript: string
  mindmap?: string
}) => {
  if (!user.value) {
    showLoginModal.value = true
    return
  }
  if (!isSupabaseConfigured) {
    alert('当前环境未配置登录服务，无法分享。')
    return
  }
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/share', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: item.title,
        summary: item.summary,
        transcript: item.transcript,
        mindmap: item.mindmap
      })
    })
    if (!response.ok) throw new Error('生成分享链接失败')
    const data = await response.json()
    const shareUrl = `${window.location.origin}${data.share_url}`
    await navigator.clipboard.writeText(shareUrl)
    alert('分享链接已复制')
  } catch (error: any) {
    alert(error?.message || '分享失败')
  }
}

const scrollToStart = () => {
  document.getElementById('start')?.scrollIntoView({ behavior: 'smooth' })
}

const scrollToSection = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('click', handleMobileMenuClick)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('click', handleMobileMenuClick)
  document.removeEventListener('keydown', handleDocumentKeydown)
})

// Auto-sync on login
watch(user, async (nextUser, prevUser) => {
  if (nextUser) {
    showLoginModal.value = false
    
    // Trigger cloud sync when user logs in
    if (!prevUser) {
      try {
        const synced = await syncToCloud()
        if (synced) {
          rawHistory.value = synced
        }
      } catch (error) {
        console.error('Auto-sync on login failed:', error)
      }
    }
    fetchDashboard().catch(() => undefined)
    fetchSubscription().catch(() => undefined)
    return
  }
  
  showUserMenu.value = false
  showPricingModal.value = false
  showApiKeyModal.value = false
  showDashboard.value = false
  showBillingModal.value = false
  showInviteModal.value = false
})

watch(errorCode, (code) => {
  if (code === 'CREDITS_EXCEEDED') {
    // 使用 nextTick 确保在下一个渲染周期显示弹窗，避免被其他逻辑关闭
    nextTick(() => {
      showPricingModal.value = true
    })
  }
  if (code === 'AUTH_REQUIRED' || code === 'AUTH_INVALID') {
    nextTick(() => {
      showLoginModal.value = true
    })
  }
})

// Cleaned summary (remove mermaid code from text display)
const cleanedSummary = computed(() => {
  if (!result.value.summary) return ''
  
  // Remove the standard block
  let cleaned = result.value.summary.replace(/```mermaid[\s\S]*?```/g, '')
  
  // If no backticks but we matched fallback, we should ideally not remove text 
  // unless we are sure it's the diagram. For now, only remove if explicitly in backticks.
  return cleaned.trim() || result.value.summary
})

const costPerSummary = computed(() => dashboardData.value?.cost_per_summary ?? 10)

const creditsLabel = computed(() => {
  if (!user.value) return '登录后可查看'
  if (!dashboardData.value) return '加载中...'
  return `${dashboardData.value.credits} 积分`
})

const planLabel = computed(() => {
  if (subscriptionData.value?.plan === 'pro' && subscriptionData.value?.status === 'active') {
    return 'Pro'
  }
  return '免费版'
})

const copySummary = () => {
  navigator.clipboard.writeText(result.value.summary)
  alert('已复制总结到剪贴板')
}

const copyTranscript = () => {
  navigator.clipboard.writeText(result.value.transcript)
  alert('已复制转录到剪贴板')
}

const fetchVideoInfo = async (url: string) => {
  if (!url) {
    videoInfo.value = null
    return
  }

  try {
    const response = await fetch('/api/video-info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    if (!response.ok) {
      videoInfo.value = null
      return
    }

    videoInfo.value = await response.json()
  } catch (error) {
    console.warn('Video info fetch failed:', error)
    videoInfo.value = null
  }
}

const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const stripMarkdown = (content: string) => {
  return content
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*]\([^)]+\)/g, '')
    .replace(/\[([^\]]+)]\([^)]+\)/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s?/gm, '')
    .replace(/^\s{0,3}[-*+]\s+/gm, '')
    .replace(/^\s{0,3}\d+\.\s+/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const exportSummaryPdf = async () => {
  if (!result.value.summary) {
    alert('暂无可导出的总结内容')
    return
  }

  const container = document.createElement('div')
  container.style.position = 'fixed'
  container.style.left = '0'
  container.style.top = '0'
  container.style.width = '800px'
  container.style.padding = '24px'
  container.style.background = '#ffffff'
  container.style.color = '#111827'
  container.style.fontFamily = '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif'
  container.style.opacity = '0'
  container.style.pointerEvents = 'none'
  container.style.zIndex = '-1'

  const html = marked.parse(cleanedSummary.value)
  container.innerHTML = `
    <div style="font-size: 22px; font-weight: 700; margin-bottom: 16px;">视频总结</div>
    <div style="font-size: 14px; line-height: 1.7;">${html}</div>
  `

  document.body.appendChild(container)
  try {
    await new Promise<void>(resolve => {
      requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
    })
    await html2pdf().set({
      margin: 10,
      filename: 'summary.pdf',
      html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(container).save()
  } finally {
    container.remove()
  }
}

const handleExport = async (format: 'md' | 'txt' | 'pdf') => {
  if (!result.value.summary) {
    alert('暂无可导出的总结内容')
    return
  }

  if (format === 'pdf') {
    await exportSummaryPdf()
    return
  }

  const content = format === 'md'
    ? result.value.summary
    : stripMarkdown(cleanedSummary.value)
  const mime = format === 'md' ? 'text/markdown' : 'text/plain'
  downloadBlob(new Blob([content], { type: `${mime};charset=utf-8` }), `summary.${format}`)
}

const getSvgSize = (svg: SVGSVGElement) => {
  const widthAttr = svg.getAttribute('width')
  const heightAttr = svg.getAttribute('height')
  let width = widthAttr ? parseFloat(widthAttr) : 0
  let height = heightAttr ? parseFloat(heightAttr) : 0
  if ((!width || !height) && svg.getAttribute('viewBox')) {
    const viewBox = svg.getAttribute('viewBox')?.split(/\s+/).map(Number) || []
    if (viewBox.length === 4) {
      width = viewBox[2] || 0
      height = viewBox[3] || 0
    }
  }
  return {
    width: width || 1200,
    height: height || 800
  }
}

const buildSvgExport = () => {
  const svgEl = mindmapRef.value?.getSvgElement()
  const svgMarkup = mindmapRef.value?.getSvgMarkup()
  if (svgMarkup) {
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgMarkup, 'image/svg+xml')
    const parsedSvg = doc.querySelector('svg')
    if (parsedSvg) {
      return parsedSvg as SVGSVGElement
    }
  }
  return svgEl
}

const exportMindmap = async (format: 'svg' | 'png') => {
  const svgEl = buildSvgExport()
  if (!svgEl) {
    alert('暂无可导出的思维导图')
    return
  }

  const serializer = new XMLSerializer()
  let svgText = serializer.serializeToString(svgEl)
  if (!svgText.includes('xmlns=')) {
    svgText = svgText.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
  }
  if (!svgText.includes('xmlns:xlink=')) {
    svgText = svgText.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
  }

  if (format === 'svg') {
    downloadBlob(new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' }), 'mindmap.svg')
    return
  }

  const { width, height } = getSvgSize(svgEl)
  const svgBlob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, width, height)
      ctx.drawImage(img, 0, 0, width, height)
      canvas.toBlob((blob) => {
        if (blob) {
          downloadBlob(blob, 'mindmap.png')
        } else {
          alert('导出 PNG 失败，请重试')
        }
        URL.revokeObjectURL(url)
      }, 'image/png')
    } else {
      URL.revokeObjectURL(url)
      alert('导出 PNG 失败，请重试')
    }
  }
  img.onerror = () => {
    URL.revokeObjectURL(url)
    alert('导出 PNG 失败，请重试')
  }
  img.decoding = 'async'
  img.src = url
}

const loadFromHistory = (item: any) => {
  result.value.summary = item.summary
  result.value.transcript = item.transcript
  result.value.videoFile = null
  currentVideoUrl.value = item.url || ''
  fetchVideoInfo(currentVideoUrl.value)
}

const clearHistory = () => {
  if (confirm('确定要清空所有历史记录吗？')) {
    clearHistorySync()
    rawHistory.value = []
  }
}
</script>
