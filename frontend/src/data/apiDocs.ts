// API 文档数据定义
export interface ApiParam {
    name: string
    type: string
    required: boolean
    description: string
    example?: string
}

export interface ApiError {
    code: string
    httpStatus: number
    message: string
}

export interface ApiEndpoint {
    id: string
    method: 'GET' | 'POST' | 'DELETE' | 'PUT'
    path: string
    title: string
    description: string
    auth: 'none' | 'jwt' | 'api-key'
    params: ApiParam[]
    requestExample: string
    responseExample: string
    errors: ApiError[]
    notes?: string
}

export interface ApiSection {
    id: string
    title: string
    endpoints: ApiEndpoint[]
}

// API 文档数据
export const apiSections: ApiSection[] = [
    {
        id: 'core',
        title: '核心接口',
        endpoints: [
            {
                id: 'summarize',
                method: 'GET',
                path: '/api/summarize',
                title: '视频总结（SSE）',
                description: '生成视频内容摘要，支持 Server-Sent Events 实时推送进度',
                auth: 'api-key',
                params: [
                    {
                        name: 'url',
                        type: 'string',
                        required: true,
                        description: 'B站视频 URL',
                        example: 'https://www.bilibili.com/video/BV1xx411c7mD'
                    },
                    {
                        name: 'perspective',
                        type: 'string',
                        required: false,
                        description: '分析视角：default（默认）、study（学习笔记）、creator（创作者视角）',
                        example: 'study'
                    }
                ],
                requestExample: `curl -X GET "https://api.bili-summarizer.com/api/summarize?url=https://www.bilibili.com/video/BV1xx411c7mD" \\
  -H "x-api-key: sk-bili-your-key-here" \\
  -H "Accept: text/event-stream"`,
                responseExample: `event: phase
data: {"phase":"downloading","hint":"正在获取视频信息..."}

event: progress
data: {"percent":30}

event: summary
data: {"content":"## 视频主题\\n本视频主要讲解..."}

event: mindmap
data: {"svg":"<svg>...</svg>"}

event: done
data: {"summary":"...","transcript":"...","mindmap":"...","credits_used":1}`,
                errors: [
                    { code: 'INVALID_URL', httpStatus: 400, message: '无效的视频 URL' },
                    { code: 'VIDEO_NOT_FOUND', httpStatus: 404, message: '视频不存在或无法访问' },
                    { code: 'INSUFFICIENT_CREDITS', httpStatus: 402, message: '积分不足' },
                    { code: 'INVALID_API_KEY', httpStatus: 401, message: 'API Key 无效或已过期' }
                ],
                notes: 'SSE 连接会持续 30-120 秒，请设置合理的超时时间。'
            },
            {
                id: 'video-info',
                method: 'GET',
                path: '/api/video-info',
                title: '获取视频信息',
                description: '获取视频基本信息（标题、作者、时长等），不消耗积分',
                auth: 'none',
                params: [
                    {
                        name: 'url',
                        type: 'string',
                        required: true,
                        description: 'B站视频 URL',
                        example: 'https://www.bilibili.com/video/BV1xx411c7mD'
                    }
                ],
                requestExample: `curl -X GET "https://api.bili-summarizer.com/api/video-info?url=https://www.bilibili.com/video/BV1xx411c7mD"`,
                responseExample: `{
  "title": "视频标题",
  "author": "UP主名称",
  "duration": 1234,
  "cover": "https://...",
  "view_count": 10000,
  "danmaku_count": 500
}`,
                errors: [
                    { code: 'INVALID_URL', httpStatus: 400, message: '无效的视频 URL' },
                    { code: 'VIDEO_NOT_FOUND', httpStatus: 404, message: '视频不存在' }
                ]
            }
        ]
    },
    {
        id: 'user',
        title: '用户接口',
        endpoints: [
            {
                id: 'dashboard',
                method: 'GET',
                path: '/api/dashboard',
                title: '用户仪表盘',
                description: '获取用户积分、使用统计、订阅状态',
                auth: 'jwt',
                params: [],
                requestExample: `curl -X GET "https://api.bili-summarizer.com/api/dashboard" \\
  -H "Authorization: Bearer your-jwt-token"`,
                responseExample: `{
  "credits": 120,
  "total_usage": 45,
  "daily_stats": [
    {"date": "2024-12-24", "count": 5},
    {"date": "2024-12-23", "count": 3}
  ],
  "subscription": {
    "plan": "pro",
    "expires_at": "2025-01-24T00:00:00Z"
  }
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录或 token 无效' }
                ]
            },
            {
                id: 'history',
                method: 'GET',
                path: '/api/history',
                title: '历史记录',
                description: '获取用户的总结历史记录',
                auth: 'jwt',
                params: [
                    {
                        name: 'limit',
                        type: 'number',
                        required: false,
                        description: '返回条数，默认 20，最大 100',
                        example: '20'
                    },
                    {
                        name: 'offset',
                        type: 'number',
                        required: false,
                        description: '偏移量，用于分页',
                        example: '0'
                    }
                ],
                requestExample: `curl -X GET "https://api.bili-summarizer.com/api/history?limit=20&offset=0" \\
  -H "Authorization: Bearer your-jwt-token"`,
                responseExample: `{
  "items": [
    {
      "id": "uuid",
      "url": "https://...",
      "title": "视频标题",
      "summary": "总结内容...",
      "created_at": "2024-12-24T10:00:00Z"
    }
  ],
  "total": 45
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录' }
                ]
            }
        ]
    },
    {
        id: 'payment',
        title: '支付接口',
        endpoints: [
            {
                id: 'create-payment',
                method: 'POST',
                path: '/api/payments',
                title: '创建支付订单',
                description: '创建积分充值或订阅支付订单',
                auth: 'jwt',
                params: [
                    {
                        name: 'product_type',
                        type: 'string',
                        required: true,
                        description: 'product_type: pack（积分包）或 subscription（订阅）',
                        example: 'pack'
                    },
                    {
                        name: 'product_id',
                        type: 'string',
                        required: true,
                        description: 'starter_pack、pro_pack 或 pro_monthly',
                        example: 'pro_pack'
                    },
                    {
                        name: 'payment_method',
                        type: 'string',
                        required: true,
                        description: 'alipay 或 wechat',
                        example: 'alipay'
                    }
                ],
                requestExample: `curl -X POST "https://api.bili-summarizer.com/api/payments" \\
  -H "Authorization: Bearer your-jwt-token" \\
  -H "Content-Type: application/json" \\
  -d '{"product_type":"pack","product_id":"pro_pack","payment_method":"alipay"}'`,
                responseExample: `{
  "order_id": "uuid",
  "qr_url": "https://qr.alipay.com/...",
  "amount": 3.00,
  "status": "pending"
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录' },
                    { code: 'INVALID_PRODUCT', httpStatus: 400, message: '无效的商品ID' }
                ]
            }
        ]
    },
    {
        id: 'api-keys',
        title: 'API Key 管理',
        endpoints: [
            {
                id: 'list-keys',
                method: 'GET',
                path: '/api/keys',
                title: '获取 API Key 列表',
                description: '获取当前用户的所有 API Key',
                auth: 'jwt',
                params: [],
                requestExample: `curl -X GET "https://api.bili-summarizer.com/api/keys" \\
  -H "Authorization: Bearer your-jwt-token"`,
                responseExample: `{
  "keys": [
    {
      "id": "uuid",
      "prefix": "sk-bili-abc",
      "name": "Production Key",
      "created_at": "2024-12-01T00:00:00Z",
      "last_used_at": "2024-12-24T10:00:00Z",
      "usage_count": 123
    }
  ]
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录' }
                ]
            },
            {
                id: 'create-key',
                method: 'POST',
                path: '/api/keys',
                title: '创建 API Key',
                description: '创建新的 API Key',
                auth: 'jwt',
                params: [
                    {
                        name: 'name',
                        type: 'string',
                        required: true,
                        description: 'Key 名称，便于识别',
                        example: 'Production Key'
                    }
                ],
                requestExample: `curl -X POST "https://api.bili-summarizer.com/api/keys" \\
  -H "Authorization: Bearer your-jwt-token" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Production Key"}'`,
                responseExample: `{
  "id": "uuid",
  "key": "sk-bili-xxxxxxxxxxxxxxxx",
  "name": "Production Key",
  "created_at": "2024-12-24T10:00:00Z"
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录' },
                    { code: 'QUOTA_EXCEEDED', httpStatus: 429, message: 'API Key 数量已达上限' }
                ],
                notes: '⚠️ API Key 仅在创建时显示一次，请妥善保管。'
            },
            {
                id: 'delete-key',
                method: 'DELETE',
                path: '/api/keys/{id}',
                title: '撤销 API Key',
                description: '删除指定的 API Key',
                auth: 'jwt',
                params: [
                    {
                        name: 'id',
                        type: 'string',
                        required: true,
                        description: 'API Key ID（路径参数）',
                        example: 'uuid'
                    }
                ],
                requestExample: `curl -X DELETE "https://api.bili-summarizer.com/api/keys/uuid" \\
  -H "Authorization: Bearer your-jwt-token"`,
                responseExample: `{
  "success": true
}`,
                errors: [
                    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录' },
                    { code: 'NOT_FOUND', httpStatus: 404, message: 'Key 不存在' }
                ]
            }
        ]
    }
]

// 错误码总览
export const errorCodes = [
    { code: 'INVALID_URL', httpStatus: 400, message: '无效的视频 URL' },
    { code: 'INVALID_API_KEY', httpStatus: 401, message: 'API Key 无效或已过期' },
    { code: 'UNAUTHORIZED', httpStatus: 401, message: '未登录或 token 无效' },
    { code: 'INSUFFICIENT_CREDITS', httpStatus: 402, message: '积分不足' },
    { code: 'VIDEO_NOT_FOUND', httpStatus: 404, message: '视频不存在或无法访问' },
    { code: 'RATE_LIMITED', httpStatus: 429, message: '请求频率超限' },
    { code: 'INTERNAL_ERROR', httpStatus: 500, message: '服务器内部错误' }
]

// Rate Limit 信息
export const rateLimits = [
    { tier: '免费用户', limit: '10 次/分钟' },
    { tier: 'Pro 订阅', limit: '60 次/分钟' },
    { tier: 'API Key', limit: '120 次/分钟' }
]
