<template>
  <div class="page-card">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">功能对比</h3>
    <div class="overflow-x-auto -mx-4 px-4">
      <table class="w-full text-sm border-collapse min-w-[600px]">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th class="text-left py-3 px-2 font-semibold text-gray-900 dark:text-gray-100">功能</th>
            <th class="text-center py-3 px-2 font-semibold text-gray-900 dark:text-gray-100">免费版</th>
            <th class="text-center py-3 px-2 font-semibold text-gray-900 dark:text-gray-100">Starter</th>
            <th class="text-center py-3 px-2 font-semibold text-gray-900 dark:text-gray-100">Pro Pack</th>
            <th class="text-center py-3 px-2 font-semibold text-primary">Pro 专业版</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(feature, index) in features" :key="index" class="border-b border-gray-100 dark:border-gray-800">
            <td class="py-3 px-2 text-gray-700 dark:text-gray-300">{{ feature.name }}</td>
            <td class="py-3 px-2 text-center text-gray-600 dark:text-gray-400">
              <span v-html="formatValue(feature.free)"></span>
            </td>
            <td class="py-3 px-2 text-center text-gray-600 dark:text-gray-400">
              <span v-html="formatValue(feature.starter)"></span>
            </td>
            <td class="py-3 px-2 text-center text-gray-600 dark:text-gray-400">
              <span v-html="formatValue(feature.proPack)"></span>
            </td>
            <td class="py-3 px-2 text-center text-gray-600 dark:text-gray-400">
              <span v-html="formatValue(feature.pro)"></span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Feature {
  name: string
  free: boolean | string
  starter: boolean | string
  proPack: boolean | string
  pro: boolean | string
}

const features: Feature[] = [
  { name: '初始积分', free: '50', starter: '+30', proPack: '+120', pro: '无限' },
  { name: '响应速度', free: '标准', starter: '标准', proPack: '标准', pro: '优先' },
  { name: '思维导图', free: true, starter: true, proPack: true, pro: true },
  { name: '视频转录', free: true, starter: true, proPack: true, pro: true },
  { name: 'AI 追问', free: true, starter: true, proPack: true, pro: true },
  { name: '历史记录', free: true, starter: true, proPack: true, pro: true },
  { name: '多格式导出', free: true, starter: true, proPack: true, pro: true },
  { name: 'API 调用', free: false, starter: false, proPack: false, pro: true },
  { name: '专属客服', free: false, starter: false, proPack: false, pro: true }
]

const formatValue = (value: boolean | string): string => {
  if (value === true) return '<span class="text-green-600 dark:text-green-400 text-lg">✓</span>'
  if (value === false) return '<span class="text-gray-300 dark:text-gray-600 text-lg">✗</span>'
  return String(value)
}
</script>
