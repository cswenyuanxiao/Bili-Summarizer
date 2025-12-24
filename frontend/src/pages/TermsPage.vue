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
        <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">Bili-Summarizer 服务条款</h1>
        <p class="text-sm text-gray-500">最后更新：2024年12月24日</p>
      </div>
      
      <!-- 目录 -->
      <nav class="mb-12 p-6 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
        <h2 class="font-semibold text-gray-900 dark:text-gray-100 mb-4">目录</h2>
        <ul class="space-y-2 text-sm text-primary">
          <li><a href="#service" class="hover:underline">1. 服务说明</a></li>
          <li><a href="#user" class="hover:underline">2. 用户责任</a></li>
          <li><a href="#ip" class="hover:underline">3. 知识产权</a></li>
          <li><a href="#payment" class="hover:underline">4. 付费与退款</a></li>
          <li><a href="#disclaimer" class="hover:underline">5. 免责声明</a></li>
          <li><a href="#changes" class="hover:underline">6. 服务变更与终止</a></li>
          <li><a href="#dispute" class="hover:underline">7. 争议解决</a></li>
          <li><a href="#contact" class="hover:underline">8. 联系我们</a></li>
        </ul>
      </nav>
      
      <!-- 正文 -->
      <article class="prose prose-gray dark:prose-invert max-w-none space-y-12">
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500 text-sm">
          欢迎使用 Bili-Summarizer！请仔细阅读本服务条款，使用本服务即表示您同意遵守以下条款。
        </div>
        
        <!-- 1. 服务说明 -->
        <section id="service">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">1. 服务说明</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>Bili-Summarizer（以下简称"本服务"）是一个基于人工智能的视频内容总结工具，为用户提供以下功能：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li>视频内容智能总结</li>
              <li>自动转录与字幕提取</li>
              <li>思维导图生成与导出</li>
              <li>AI 对话式追问</li>
              <li>历史记录管理</li>
            </ul>
            <p>本服务依赖第三方平台（如 Bilibili）的公开数据，我们不对视频内容本身负责。</p>
          </div>
        </section>
        
        <!-- 2. 用户责任 -->
        <section id="user">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">2. 用户责任</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>使用本服务时，您需要遵守以下规范：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li><strong>合法使用</strong>：不得将本服务用于任何违反法律法规的目的</li>
              <li><strong>禁止滥用</strong>：不得通过技术手段恶意刷取积分或绕过使用限制</li>
              <li><strong>账号安全</strong>：您需妥善保管账号密码和 API Key，因账号泄露造成的损失由您自行承担</li>
              <li><strong>内容版权</strong>：使用本服务生成的内容不得侵犯他人知识产权</li>
            </ul>
            <p class="text-sm text-red-600 dark:text-red-400">⚠️ 违反上述规定可能导致账号被封禁且不予退款。</p>
          </div>
        </section>
        
        <!-- 3. 知识产权 -->
        <section id="ip">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">3. 知识产权</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>服务所有权</strong>：本服务的所有代码、设计、商标归 Bili-Summarizer 所有。</p>
            <p><strong>生成内容</strong>：通过本服务生成的总结、思维导图等内容归您所有，但您需自行确保不侵犯原视频的版权。</p>
            <p><strong>禁止行为</strong>：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li>逆向工程、反编译或反汇编本服务</li>
              <li>将本服务用于开发竞品</li>
              <li>未经许可商业化销售本服务</li>
            </ul>
          </div>
        </section>
        
        <!-- 4. 付费与退款 -->
        <section id="payment">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">4. 付费与退款</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>积分有效期</strong>：一次性购买的积分包永久有效，不设过期时间。</p>
            <p><strong>订阅周期</strong>：Pro 专业版按月订阅，自动续费，可随时取消。</p>
            <p><strong>退款政策</strong>：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li>积分包和订阅费用一经购买概不退款</li>
              <li>如遇服务故障导致积分异常扣除，可联系客服申请补偿</li>
              <li>如因违规被封禁，已购积分和订阅不予退款</li>
            </ul>
            <p><strong>价格变更</strong>：我们保留调整价格的权利，但已购买的积分和订阅不受影响。</p>
          </div>
        </section>
        
        <!-- 5. 免责声明 -->
        <section id="disclaimer">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">5. 免责声明</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>服务可用性</strong>：我们尽力保证服务稳定，但不对以下情况承担责任：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li>因第三方平台（如 Bilibili、Google Gemini）故障导致的服务中断</li>
              <li>因网络、服务器等不可抗力导致的数据丢失</li>
              <li>因系统维护或升级导致的短暂停机</li>
            </ul>
            <p><strong>内容准确性</strong>：AI 生成的总结仅供参考，我们不保证其完全准确，用户需自行判断。</p>
            <p><strong>间接损失</strong>：我们不对因使用本服务导致的任何间接损失（如利润损失、数据丢失）负责。</p>
          </div>
        </section>
        
        <!-- 6. 服务变更与终止 -->
        <section id="changes">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">6. 服务变更与终止</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>功能调整</strong>：我们可能随时增加、修改或删除服务功能，恕不另行通知。</p>
            <p><strong>服务终止</strong>：在以下情况下，我们有权终止您的账号：</p>
            <ul class="list-disc pl-6 space-y-2">
              <li>违反本服务条款</li>
              <li>滥用服务或进行欺诈行为</li>
              <li>长期不活跃（超过 12 个月）</li>
            </ul>
            <p><strong>终止通知</strong>：账号终止前我们会通过邮件提前 7 天通知，但紧急情况下可能立即终止。</p>
          </div>
        </section>
        
        <!-- 7. 争议解决 -->
        <section id="dispute">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">7. 争议解决</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p><strong>适用法律</strong>：本条款适用中华人民共和国法律。</p>
            <p><strong>管辖法院</strong>：因本服务产生的任何争议，应提交至服务提供方所在地人民法院诉讼解决。</p>
            <p><strong>争议协商</strong>：我们鼓励通过友好协商解决争议，请先联系客服。</p>
          </div>
        </section>
        
        <!-- 8. 联系我们 -->
        <section id="contact">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">8. 联系我们</h2>
          <div class="space-y-4 text-gray-600 dark:text-gray-300">
            <p>如对本服务条款有任何疑问，请通过以下方式联系我们：</p>
            <ul class="space-y-2">
              <li><strong>邮箱</strong>：<a href="mailto:support@bili-summarizer.com" class="text-primary hover:underline">support@bili-summarizer.com</a></li>
              <li><strong>GitHub</strong>：<a href="https://github.com/xxx/bili-summarizer/issues" target="_blank" class="text-primary hover:underline">提交 Issue</a></li>
            </ul>
          </div>
        </section>
      </article>
      
      <!-- 底部 -->
      <div class="mt-16 pt-8 border-t border-gray-200 dark:border-gray-700 text-center">
        <p class="text-sm text-gray-500">
          继续使用本服务即表示您同意本服务条款。
          <br>
          另请阅读我们的 <RouterLink to="/privacy" class="text-primary hover:underline">隐私政策</RouterLink>
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
