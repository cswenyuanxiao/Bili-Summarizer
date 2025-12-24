/**
 * PDF 导出工具
 * 支持长文分页、中文字体、Mermaid 图表
 */
import html2pdf from 'html2pdf.js'

export interface PdfExportOptions {
    filename?: string
    pageSize?: 'a4' | 'letter' | 'legal'
    orientation?: 'portrait' | 'landscape'
    margin?: number | [number, number, number, number]
    enablePageBreaks?: boolean
    imageQuality?: number
}

const defaultOptions: PdfExportOptions = {
    filename: 'bili-summary.pdf',
    pageSize: 'a4',
    orientation: 'portrait',
    margin: 15,
    enablePageBreaks: true,
    imageQuality: 2
}

/**
 * 预处理 HTML 内容
 * - 将 Mermaid SVG 转换为图片
 * - 添加分页标记
 * - 处理中文字体
 */
async function preprocessContent(element: HTMLElement): Promise<HTMLElement> {
    const clone = element.cloneNode(true) as HTMLElement

    // 1. 处理 Mermaid SVG -> 转换为 PNG (通过 Canvas)
    // 注意：在 PDF 中 SVG 可能渲染不全，转换为图片更稳定
    const svgs = clone.querySelectorAll('svg.mermaid')
    for (const svg of svgs) {
        try {
            const canvas = document.createElement('canvas')
            const ctx = canvas.getContext('2d')
            if (!ctx) continue

            const svgData = new XMLSerializer().serializeToString(svg)
            const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
            const url = URL.createObjectURL(svgBlob)

            const img = new Image()
            await new Promise((resolve, reject) => {
                img.onload = resolve
                img.onerror = reject
                img.src = url
            })

            // 高清渲染
            canvas.width = img.width * 2
            canvas.height = img.height * 2
            ctx.scale(2, 2)
            ctx.drawImage(img, 0, 0)

            const imgElement = document.createElement('img')
            imgElement.src = canvas.toDataURL('image/png')
            imgElement.style.maxWidth = '100%'
            imgElement.style.height = 'auto'
            imgElement.style.display = 'block'
            imgElement.style.margin = '10px auto'

            svg.parentNode?.replaceChild(imgElement, svg)
            URL.revokeObjectURL(url)
        } catch (e) {
            console.warn('Failed to convert SVG to PNG:', e)
        }
    }

    // 2. 添加分页控制样式
    const style = document.createElement('style')
    style.textContent = `
    /* 中文字体支持 */
    * {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", 
                   "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", 
                   "WenQuanYi Micro Hei", sans-serif !important;
    }
    
    /* 分页控制 */
    h1, h2, h3 {
      page-break-after: avoid;
      break-after: avoid;
      color: #1a1a1a;
    }
    
    p, li {
      orphans: 3;
      widows: 3;
      color: #333;
      line-height: 1.6;
    }
    
    pre, code, table {
      page-break-inside: avoid;
      break-inside: avoid;
      background: #f5f5f5;
    }
    
    img {
      max-width: 100%;
      height: auto;
      page-break-inside: avoid;
    }
    
    /* 强制分页点 */
    .page-break {
      page-break-before: always;
      break-before: page;
    }

    /* 隐藏导出时不必要的元素 */
    .no-export {
      display: none !important;
    }

    /* 确保容器背景为白色 */
    .pdf-container {
      background: white !important;
      padding: 20px;
    }
  `
    clone.prepend(style)
    clone.classList.add('pdf-container')

    // 3. 在大标题前添加分页逻辑 (防止 PDF 单页过长)
    const h2s = clone.querySelectorAll('h2')
    h2s.forEach((h2, index) => {
        // 除了第一个二级标题，其他的如果前面内容较多则尝试分页
        if (index > 0) {
            h2.classList.add('page-break')
        }
    })

    return clone
}

/**
 * 导出 PDF
 */
export async function exportToPdf(
    element: HTMLElement,
    options: PdfExportOptions = {}
): Promise<void> {
    const opts = { ...defaultOptions, ...options }

    // 预处理内容
    const processedElement = await preprocessContent(element)

    // 创建临时容器以确保样式不受外界干扰
    const container = document.createElement('div')
    container.style.position = 'absolute'
    container.style.left = '-9999px'
    container.style.width = '210mm' // A4 宽度
    container.appendChild(processedElement)
    document.body.appendChild(container)

    try {
        const worker = html2pdf()
            .set({
                margin: opts.margin,
                filename: opts.filename,
                image: {
                    type: 'jpeg',
                    quality: 0.98
                },
                html2canvas: {
                    scale: opts.imageQuality,
                    useCORS: true,
                    letterRendering: true,
                    scrollY: 0,
                    windowWidth: 1200 // 增加渲染宽度以获得更好排版
                },
                jsPDF: {
                    unit: 'mm',
                    format: opts.pageSize,
                    orientation: opts.orientation
                },
                // @ts-ignore: html2pdf.js options may not fully match the @types/html2pdf.js
                pagebreak: {
                    mode: ['avoid-all', 'css', 'legacy'],
                    before: '.page-break',
                    avoid: ['pre', 'code', 'table', 'img', 'h1', 'h2', 'h3']
                }
            })
            .from(processedElement)

        await worker.save()
    } finally {
        document.body.removeChild(container)
    }
}

/**
 * 导出带目录的 PDF
 */
export async function exportToPdfWithToc(
    element: HTMLElement,
    options: PdfExportOptions = {}
): Promise<void> {
    const clone = element.cloneNode(true) as HTMLElement

    // 生成简单的目录 HTML
    const headings = clone.querySelectorAll('h1, h2, h3')
    if (headings.length > 0) {
        const tocHtml = `
      <div class="toc" style="margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px;">
        <h1 style="text-align: center; margin-bottom: 20px;">内容目录</h1>
        <ul style="list-style: none; padding-left: 0;">
          ${Array.from(headings).map((h, _i) => {
            const levelStr = h.tagName.charAt(1)
            const level = parseInt(levelStr || '1')
            const indent = (level - 1) * 20
            const fontSize = level === 1 ? '18px' : level === 2 ? '16px' : '14px'
            return `<li style="margin-left: ${indent}px; margin-bottom: 8px; font-size: ${fontSize};">
              <span style="border-bottom: 1px dotted #ccc; display: block;">${h.textContent || ''}</span>
            </li>`
        }).join('')}
        </ul>
      </div>
      <div class="page-break"></div>
    `
        clone.insertAdjacentHTML('afterbegin', tocHtml)
    }

    await exportToPdf(clone, options)
}
