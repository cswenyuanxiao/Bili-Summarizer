/**
 * Mermaid 稳定渲染器
 * 包含代码预处理、错误处理、重试和回退机制
 */
import mermaid from 'mermaid'

// 现代化主题配置
mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    securityLevel: 'loose',
    fontFamily: '"Inter", "PingFang SC", "Microsoft YaHei", sans-serif',
    themeVariables: {
        // 主色调 - 优雅紫色系
        primaryColor: '#6366f1',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#4f46e5',
        // 次级色调
        secondaryColor: '#f0abfc',
        secondaryTextColor: '#1f2937',
        secondaryBorderColor: '#e879f9',
        // 第三色调
        tertiaryColor: '#fde68a',
        tertiaryTextColor: '#1f2937',
        tertiaryBorderColor: '#fbbf24',
        // 线条和背景
        lineColor: '#94a3b8',
        textColor: '#1f2937',
        mainBkg: '#f8fafc',
        nodeBorder: '#e2e8f0',
        // 特殊节点
        nodeTextColor: '#1f2937',
        // 字体
        fontSize: '14px',
        // 思维导图专用
        mindmapRootBg: '#6366f1',
        mindmapRootColor: '#ffffff',
        mindmapLevel1Bg: '#a78bfa',
        mindmapLevel1Color: '#ffffff',
        mindmapLevel2Bg: '#c4b5fd',
        mindmapLevel2Color: '#1f2937'
    },
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
        padding: 20,
        nodeSpacing: 50,
        rankSpacing: 60
    },
    mindmap: {
        useMaxWidth: true,
        padding: 16
    }
})

export interface RenderResult {
    success: boolean
    svg?: string
    error?: string
}

/**
 * 预处理 Mermaid 代码
 * 修复常见的语法问题，如中文符号、过长文本等
 */
function preprocessCode(code: string): string {
    let processed = code.trim()

    // 移除可能的渲染标记
    processed = processed.replace(/^```mermaid\n?/i, '')
    processed = processed.replace(/\n?```$/i, '')

    // 1. 基础清理
    processed = processed
        .replace(/\r\n/g, '\n')
        // 将中文括号转为英文 (Mermaid 不支持中文括号作为节点边界)
        .replace(/（/g, '(')
        .replace(/）/g, ')')
        .replace(/【/g, '[')
        .replace(/】/g, ']')
        .replace(/：/g, ': ')

    // 2. 增强转义：处理节点内容中的特殊字符
    const lines = processed.split('\n')
    const fixedLines = lines.map(line => {
        // 处理形如 ID[Content] 的节点定义
        if (line.includes('[') && line.includes(']')) {
            return line.replace(/\[([^\]]+)\]/g, (_, content) => {
                // 如果内容包含引号且未正确关闭，或者包含特殊字符
                const safeContent = content
                    .replace(/"/g, "'")    // 内部双引号转单引号
                    .replace(/<br\/?>/gi, ' ') // 移除换行符
                    .replace(/[<>]/g, '')  // 移除标签符
                return `["${safeContent}"]` // 统一使用引号包裹
            })
        }
        return line
    })

    return fixedLines.join('\n')
}

/**
 * 简化图表代码（备用方案）
 * 如果主方案失败，尝试极简模式渲染
 */
function simplifyDiagram(code: string): string {
    const lines = code.split('\n')
    const simplified: string[] = []

    for (const line of lines) {
        if (line.match(/^(graph|flowchart|mindmap|sequenceDiagram|classDiagram|pie)/i)) {
            simplified.push(line)
            continue
        }

        // 只保留基础连接和文字，剔除复杂样式定义
        let l = line.trim()
        if (l.includes('--') || l.includes('->') || l.match(/^[a-zA-Z0-9_\u4e00-\u9fa5]/)) {
            // 限制节点文字长度
            l = l.replace(/\[([^\]]{40,})\]/g, (_, content) => `[${content.substring(0, 37)}...]`)
            simplified.push(l)
        }
    }

    return simplified.join('\n')
}

/**
 * 安全渲染 Mermaid 图表
 */
export async function renderMermaid(
    code: string,
    id_prefix: string = 'mermaid'
): Promise<RenderResult> {
    const id = `${id_prefix}-${Date.now()}`
    const processedCode = preprocessCode(code)

    try {
        const { svg } = await mermaid.render(id, processedCode)
        return { success: true, svg }
    } catch (error) {
        console.warn('Mermaid 主渲染解析失败，尝试回退简化模式...', error)

        try {
            const fallbackId = `${id}-fallback`
            const simplifiedCode = simplifyDiagram(processedCode)
            const { svg } = await mermaid.render(fallbackId, simplifiedCode)
            return { success: true, svg }
        } catch (fallbackError) {
            console.error('Mermaid 简化模式渲染亦失败:', fallbackError)
            return {
                success: false,
                error: `渲染失败：图表代码语法错误或过于复杂。`
            }
        }
    }
}
