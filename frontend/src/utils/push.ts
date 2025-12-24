/**
 * 浏览器推送订阅工具
 */

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || ""
import { supabase } from '../supabase'

export async function subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported')
        return null
    }

    try {
        // 1. 注册 Service Worker
        const registration = await navigator.serviceWorker.register('/sw.js')
        await navigator.serviceWorker.ready

        // 2. 获取公钥（如果不通过环境变量提供，可以请求后端）
        let publicKey = VAPID_PUBLIC_KEY
        if (!publicKey) {
            const res = await fetch('/api/push/vapid-key')
            const data = await res.json()
            publicKey = data.publicKey
        }

        if (!publicKey) {
            throw new Error('VAPID public key not found')
        }

        // 3. 订阅推送
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicKey)
        })

        // 4. 将订阅对象发送给后端
        // FIXED: Use supabase.auth.getSession() instead of localStorage
        if (!supabase) return subscription
        const { data: sessionData } = await supabase.auth.getSession()
        const token = sessionData.session?.access_token

        if (!token) {
            console.warn('User not logged in, skipping push subscription upload')
            return subscription
        }

        await fetch('/api/push/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(subscription)
        })

        return subscription
    } catch (error) {
        console.error('Failed to subscribe to push:', error)
        return null
    }
}

function urlBase64ToUint8Array(base64String: string) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')

    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray
}
