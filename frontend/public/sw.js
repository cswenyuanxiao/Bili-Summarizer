/**
 * Service Worker for Push Notifications
 */

self.addEventListener('push', (event) => {
    if (!event.data) return

    try {
        const data = event.data.json()
        const title = data.title || 'Bili-Summarizer'
        const options = {
            body: data.body || '你有新的视频总结',
            icon: data.video_cover || '/favicon.ico',
            badge: '/badge.png',
            data: {
                url: data.video_url || '/'
            }
        }

        event.waitUntil(
            self.registration.showNotification(title, options)
        )
    } catch (err) {
        console.error('Error parsing push data:', err)
    }
})

self.addEventListener('notificationclick', (event) => {
    event.notification.close()

    const url = event.notification.data.url

    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((clientList) => {
            for (const client of clientList) {
                if (client.url === url && 'focus' in client) {
                    return client.focus()
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(url)
            }
        })
    )
})
