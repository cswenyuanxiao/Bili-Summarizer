/**
 * 中文语言包
 */
export default {
    // 通用
    common: {
        loading: '加载中...',
        submit: '提交',
        cancel: '取消',
        confirm: '确认',
        save: '保存',
        delete: '删除',
        edit: '编辑',
        copy: '复制',
        share: '分享',
        close: '关闭',
        back: '返回',
        next: '下一步',
        previous: '上一步',
        search: '搜索',
        clear: '清空',
        refresh: '刷新',
        retry: '重试',
        success: '成功',
        error: '错误',
        warning: '警告',
        language: '语言',
    },

    // 导航
    nav: {
        home: '首页',
        product: '产品',
        pricing: '方案',
        docs: '文档',
        developer: '开发者',
        login: '登录',
        logout: '退出',
        dashboard: '仪表盘',
        settings: '设置',
        apiDocs: 'API 文档',
    },

    // 首页
    home: {
        title: 'Video Summarizer',
        subtitle: '把 B站长视频 拆成可执行的知识模块',
        inputPlaceholder: '粘贴 B 站视频链接，开始总结...',
        summarizeButton: '开始总结',
        smartMode: '智能模式',
        videoMode: '视频模式',
        smartModeDesc: '优先字幕，快速精准',
        videoModeDesc: 'AI 视频分析，内容详尽',
    },

    // 总结结果
    summary: {
        title: '视频总结',
        transcript: '视频转录',
        mindmap: '思维导图',
        noTranscript: '暂无转录内容。',
        exportMd: '导出 Markdown',
        exportPdf: '导出 PDF',
        exportSvg: '导出 SVG',
        exportPng: '导出 PNG',
    },

    // 登录
    auth: {
        loginTitle: '登录 / 注册',
        loginDesc: '登录后即可使用完整功能',
        loginWithGoogle: '使用 Google 登录',
        loginWithGithub: '使用 GitHub 登录',
        termsAgree: '登录即表示同意',
        terms: '服务条款',
        and: '和',
        privacy: '隐私政策',
    },

    // 定价
    pricing: {
        title: '选择方案',
        starterPack: '入门包',
        proPack: '专业包',
        proMonthly: 'Pro 月订',
        credits: '积分',
        unlimited: '无限次',
        buy: '立即购买',
        subscribe: '订阅',
        currentPlan: '当前方案',
    },

    // 仪表盘
    dashboard: {
        title: '仪表盘',
        credits: '剩余积分',
        usage: '本月使用',
        history: '历史记录',
        billing: '账单',
        apiKeys: 'API 密钥',
    },

    // 反馈
    feedback: {
        title: '反馈与建议',
        type: '反馈类型',
        typeBug: '问题反馈',
        typeFeature: '功能建议',
        typeOther: '其他',
        content: '反馈内容',
        contentPlaceholder: '请详细描述您的问题或建议...',
        contact: '联系方式（可选）',
        contactPlaceholder: 'your@email.com',
        submitSuccess: '感谢您的反馈！',
    },

    // 错误消息
    errors: {
        networkError: '网络连接失败，请检查网络',
        authRequired: '请先登录',
        creditsExceeded: '积分不足，请升级或购买',
        invalidUrl: '请输入有效的 B 站视频链接',
        unknown: '发生未知错误，请稍后重试',
    },

    // 页脚
    footer: {
        contact: '联系我们',
        feedback: '反馈建议',
        terms: '服务条款',
        privacy: '隐私政策',
    }
}
