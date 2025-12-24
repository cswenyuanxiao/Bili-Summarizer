<template>
  <main class="min-h-screen py-12 page-shell">
    <div class="container mx-auto max-w-4xl px-4">
      <!-- 顶部导航 -->
      <div class="mb-8">
        <RouterLink to="/" class="text-sm text-primary hover:underline inline-flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          返回首页
        </RouterLink>
      </div>
      
      <!-- 标题 -->
      <div class="mb-12 text-center">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">Bili-Summarizer 隐私政策</h1>
        <p class="text-sm text-gray-500">最后更新：2024年12月24日</p>
      </div>
      
      <!-- 目录 -->
      <nav class="mb-12 p-6 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
        <h2 class="font-semibold text-gray-900 dark:text-gray-100 mb-4">目录</h2>
        <ul class="space-y-2 text-sm text-primary">
          <li><a href="#collection" class="hover:underline">1. 信息收集</a></li>
          <li><a href="#usage" class="hover:underline">2. 信息使用</a></li>
          <li><a href="#sharing" class="hover:underline">3. 信息共享与披露</a></li>
          <li><a href="#storage" class="hover:underline">4. 数据存储与保护</a></li>
          <li><a href="#cookies" class="hover:underline">5. Cookie 政策</a></li>
          <li><a href="#rights" class="hover:underline">6. 用户权利</a></li>
          <li><a href="#children" class="hover:underline">7. 儿童隐私</a></li>
          <li><a href="#updates" class="hover:underline">8. 政策更新</a></li>
          <li><a href="#contact" class="hover:underline">9. 联系我们</a></li>
        </ul>
      </nav>
      
      <!-- 正文 -->
      <article class="prose prose-gray dark:prose-invert max-w-none space-y-12">
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500 text-sm">
          <strong>您的隐私对我们至关重要。</strong> 本隐私政策说明 Bili-Summarizer 如何收集、使用和保护您的个人信息。
        </div>
        
        <!-- 1. 信息收集 -->
        <section id="collection">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">1. 信息收集</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>我们收集以下类型的信息：</p>
            
            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">1.1 账号信息</h3>
                <ul class="list-disc pl-6 space-y-1">
                  <li>邮箱地址（用于注册和登录）</li>
                  <li>第三方授权信息（GitHub、Google 账号的公开资料）</li>
                  <li>用户名和头像（如有）</li>
                </ul>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">1.2 使用数据</h3>
                <ul class="list-disc pl-6 space-y-1">
                  <li>总结历史记录（视频 URL、生成的总结内容）</li>
                  <li>积分消费记录</li>
                  <li>支付订单信息（订单号、金额、支付时间）</li>
                  <li>API 调用记录（API Key、调用时间、请求参数）</li>
                </ul>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">1.3 技术数据</h3>
                <ul class="list-disc pl-6 space-y-1">
                  <li>IP 地址</li>
                  <li>设备类型和浏览器信息</li>
                  <li>访问时间和页面浏览记录</li>
                  <li>Cookies 和本地存储数据</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
        
        <!-- 2. 信息使用 -->
        <section id="usage">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">2. 信息使用</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>我们使用收集的信息用于以下目的：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li><strong>提供服务</strong>：处理视频总结请求、管理账号和积分</li>
              <li><strong>改进产品</strong>：分析使用模式、优化算法和用户体验</li>
              <li><strong>账户管理</strong>：身份验证、密码重置、订阅管理</li>
              <li><strong>通知发送</strong>：服务更新、积分变动、订阅到期提醒</li>
              <li><strong>安全防护</strong>：检测和防止滥用、欺诈行为</li>
              <li><strong>数据统计</strong>：生成匿名化的使用统计报告</li>
            </ul>
            <p class="text-sm text-gray-500">我们不会将您的个人信息用于未经说明的其他目的。</p>
          </div>
        </section>
        
        <!-- 3. 信息共享与披露 -->
        <section id="sharing">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">3. 信息共享与披露</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong class="text-red-600 dark:text-red-400">我们不会出售您的个人数据。</strong></p>
            <p>我们仅在以下情况下共享信息：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li><strong>服务提供商</strong>：与第三方服务商（如 Google Gemini、Supabase、支付网关）共享必要信息以提供服务</li>
              <li><strong>法律要求</strong>：根据法律法规、法院命令或政府要求披露信息</li>
              <li><strong>业务转让</strong>：在合并、收购等情况下，您的信息可能作为资产转移</li>
              <li><strong>征得同意</strong>：在您明确同意的情况下共享信息</li>
            </ul>
          </div>
        </section>
        
        <!-- 4. 数据存储与保护 -->
        <section id="storage">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">4. 数据存储与保护</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>存储位置</strong>：您的数据存储在 Supabase（美国）和 Render（美国）的服务器上。</p>
            <p><strong>保留期限</strong>：</p>
            <ul class="list-disc pl-6 space-y-1">
              <li>账号数据：账号存续期间及注销后 30 天</li>
              <li>总结历史：账号存续期间（可自行删除）</li>
              <li>支付记录：至少保留 3 年（税务合规要求）</li>
            </ul>
            <p><strong>安全措施</strong>：</p>
            <ul class="list-disc pl-6 space-y-1">
              <li>数据传输加密（HTTPS/TLS）</li>
              <li>数据库访问控制和加密存储</li>
              <li>定期安全审计和漏洞修复</li>
              <li>API Key 加密存储</li>
            </ul>
            <p class="text-sm text-yellow-700 dark:text-yellow-400">⚠️ 尽管我们采取合理措施保护数据，但无法保证绝对安全。</p>
          </div>
        </section>
        
        <!-- 5. Cookie 政策 -->
        <section id="cookies">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">5. Cookie 政策</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>我们使用 Cookies 和类似技术来：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li><strong>身份认证</strong>：保持登录状态</li>
              <li><strong>偏好设置</strong>：记住您的主题选择（深色/浅色模式）</li>
              <li><strong>本地存储</strong>：在浏览器中缓存历史记录（可在设置中清除）</li>
            </ul>
            <p>您可以通过浏览器设置拒绝 Cookies，但这可能影响部分功能的正常使用。</p>
          </div>
        </section>
        
        <!-- 6. 用户权利 -->
        <section id="rights">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">6. 用户权利</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>根据适用法律，您享有以下权利：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li><strong>访问权</strong>：查看我们持有的您的个人数据</li>
              <li><strong>修改权</strong>：更正不准确的个人信息</li>
              <li><strong>删除权</strong>：要求删除您的账号和相关数据</li>
              <li><strong>导出权</strong>：以结构化格式导出您的历史记录</li>
              <li><strong>撤回同意</strong>：随时撤回对数据处理的同意</li>
            </ul>
            <p>如需行使上述权利，请联系我们的客服邮箱。我们将在 30 天内处理您的请求。</p>
          </div>
        </section>
        
        <!-- 7. 儿童隐私 -->
        <section id="children">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">7. 儿童隐私</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>本服务不面向 13 岁以下儿童。我们不会故意收集儿童的个人信息。</p>
            <p>如果您发现您的孩子在未经许可的情况下向我们提供了个人信息，请联系我们，我们将立即删除相关数据。</p>
          </div>
        </section>
        
        <!-- 8. 政策更新 -->
        <section id="updates">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">8. 政策更新</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>我们可能会不定期更新本隐私政策。重大变更时，我们将：</p>
            <ul class="list-disc pl-6 space-y-1">
              <li>更新页面顶部的"最后更新"日期</li>
              <li>通过邮件通知您（如变更涉及您的重要权利）</li>
              <li>在网站首页显示通知</li>
            </ul>
            <p>继续使用服务即表示您接受更新后的隐私政策。</p>
          </div>
        </section>
        
        <!-- 9. 联系我们 -->
        <section id="contact">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">9. 联系我们</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>如对本隐私政策有任何疑问或需要行使您的权利，请通过以下方式联系我们：</p>
            <ul class="space-y-2">
              <li><strong>邮箱</strong>：<a href="mailto:privacy@bili-summarizer.com" class="text-primary hover:underline">privacy@bili-summarizer.com</a></li>
              <li><strong>GitHub</strong>：<a href="https://github.com/xxx/bili-summarizer/discussions" target="_blank" class="text-primary hover:underline">提交讨论</a></li>
            </ul>
          </div>
        </section>
      </article>
      
      <!-- 底部 -->
      <div class="mt-16 pt-8 border-t border-gray-200 dark:border-gray-700 text-center">
        <p class="text-sm text-gray-500">
          使用本服务即表示您同意本隐私政策。
          <br>
          另请阅读我们的 <RouterLink to="/terms" class="text-primary hover:underline">服务条款</RouterLink>
        </p>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
// Smooth scroll for anchor links
</script>

<style scoped>
html {
  scroll-behavior: smooth;
}

/* Anchor offset for fixed header */
section[id]::before {
  content: '';
  display: block;
  height: 80px;
  margin-top: -80px;
  visibility: hidden;
}
</style>
