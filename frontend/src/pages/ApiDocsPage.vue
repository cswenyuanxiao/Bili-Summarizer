<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-7xl px-4">
      <div class="flex gap-8">
        <!-- 侧边栏导航 -->
        <aside class="hidden lg:block w-64 flex-shrink-0 sticky top-4 h-[calc(100vh-2rem)] overflow-y-auto">
          <nav class="space-y-6 py-8">
            <!-- 概述 -->
            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase mb-2">概述</h3>
              <ul class="space-y-1">
                <li>
                  <a href="#overview" class="nav-link">快速开始</a>
                </li>
                <li>
                  <a href="#auth" class="nav-link">认证方式</a>
                </li>
                <li>
                  <a href="#rate-limit" class="nav-link">Rate Limit</a>
                </li>
              </ul>
            </div>
            
            <!-- API 分组 -->
            <div v-for="section in apiSections" :key="section.id">
              <h3 class="text-xs font-semibold text-gray-500 uppercase mb-2">{{ section.title }}</h3>
              <ul class="space-y-1">
                <li v-for="endpoint in section.endpoints" :key="endpoint.id">
                  <a :href="`#${endpoint.id}`" class="nav-link">{{ endpoint.title }}</a>
                </li>
              </ul>
            </div>
            
            <!-- 错误码 -->
            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase mb-2">参考</h3>
              <ul class="space-y-1">
                <li>
                  <a href="#errors" class="nav-link">错误码</a>
                </li>
              </ul>
            </div>
          </nav>
        </aside>
        
        <!-- 主内容区 -->
        <div class="flex-1 py-8">
          <!-- 标题 -->
          <div class="mb-12" data-reveal>
            <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">API 文档</h1>
            <p class="text-lg text-gray-600 dark:text-gray-300">
              Bili-Summarizer 提供简洁易用的 RESTful API，支持视频总结、转录、思维导图生成等功能。
            </p>
            <div class="flex gap-4 mt-6">
              <RouterLink to="/developer" class="btn-primary px-4 py-2 text-sm">
                管理 API Key
              </RouterLink>
              <a href="#overview" class="px-4 py-2 text-sm rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
                快速开始
              </a>
            </div>
          </div>
          
          <!-- 概述 -->
          <section id="overview" class="mb-12 page-card" data-reveal>
            <h2 class="text-2xl font-bold mb-4">快速开始</h2>
            <div class="space-y-4 text-gray-600 dark:text-gray-300">
              <p><strong>基础 URL：</strong> <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">https://api.bili-summarizer.com</code></p>
              <p>所有 API 请求都需要使用 HTTPS 协议。请求和响应格式均为 JSON（SSE 接口除外）。</p>
            </div>
          </section>
          
          <!-- 认证方式 -->
          <section id="auth" class="mb-12 page-card" data-reveal>
            <h2 class="text-2xl font-bold mb-4">认证方式</h2>
            <div class="space-y-4">
              <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">方式1：API Key（推荐）</h3>
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
                  在请求 Header 中加入 <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">x-api-key</code>
                </p>
                <pre class="bg-gray-900 text-gray-100 p-3 rounded-lg text-xs overflow-x-auto"><code>curl -H "x-api-key: sk-bili-your-key-here" ...</code></pre>
              </div>
              
              <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">方式2：JWT Token</h3>
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
                  适用于用户接口，在 Header 中加入 <code class="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">Authorization: Bearer</code>
                </p>
                <pre class="bg-gray-900 text-gray-100 p-3 rounded-lg text-xs overflow-x-auto"><code>curl -H "Authorization: Bearer your-jwt-token" ...</code></pre>
              </div>
            </div>
          </section>
          
          <!-- Rate Limit -->
          <section id="rate-limit" class="mb-12 page-card" data-reveal>
            <h2 class="text-2xl font-bold mb-4">Rate Limit</h2>
            <table class="w-full text-sm">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-4 py-3 text-left">用户类型</th>
                  <th class="px-4 py-3 text-left">限制</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="item in rateLimits" :key="item.tier">
                  <td class="px-4 py-3">{{ item.tier }}</td>
                  <td class="px-4 py-3 font-mono text-primary">{{ item.limit }}</td>
                </tr>
              </tbody>
            </table>
            <p class="text-sm text-gray-500 mt-4">
              超出限制时会返回 <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">429 Too Many Requests</code>
            </p>
          </section>
          
          <!-- API 分组 -->
          <div v-for="section in apiSections" :key="section.id" class="mb-16">
            <h2 class="text-3xl font-bold mb-8 text-gray-900 dark:text-gray-100" :id="section.id" data-reveal>
              {{ section.title }}
            </h2>
            <div class="space-y-8">
              <div v-for="endpoint in section.endpoints" :key="endpoint.id" :id="endpoint.id" data-reveal>
                <ApiEndpoint :endpoint="endpoint" />
              </div>
            </div>
          </div>
          
          <!-- 错误码表 -->
          <section id="errors" class="mb-12 page-card" data-reveal>
            <h2 class="text-2xl font-bold mb-4">错误码参考</h2>
            <div class="space-y-2">
              <div 
                v-for="error in errorCodes" 
                :key="error.code"
                class="flex items-start gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <span class="px-2 py-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded font-mono text-xs font-bold">
                  {{ error.httpStatus }}
                </span>
                <div class="flex-1">
                  <code class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ error.code }}</code>
                  <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{{ error.message }}</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { apiSections, errorCodes, rateLimits } from '../data/apiDocs'
import ApiEndpoint from '../components/ApiEndpoint.vue'
import { useReveal } from '../composables/useReveal'

useReveal()
</script>

<style scoped>
.nav-link {
  display: block;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: rgb(107 114 128);
  border-radius: 0.5rem;
  transition: all 150ms;
}

.nav-link:hover {
  color: rgb(99 102 241);
  background-color: rgb(243 244 246);
}

.dark .nav-link:hover {
  background-color: rgb(31 41 55);
}

.nav-link:target,
.nav-link.active {
  color: rgb(99 102 241);
  background-color: rgb(238 242 255);
}

.dark .nav-link:target,
.dark .nav-link.active {
  background-color: rgb(55 65 81);
}

/* 平滑滚动 */
html {
  scroll-behavior: smooth;
}

/* 锚点偏移 */
section[id]::before {
  content: '';
  display: block;
  height: 80px;
  margin-top: -80px;
  visibility: hidden;
}
</style>
