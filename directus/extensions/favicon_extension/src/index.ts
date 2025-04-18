import { defineHook } from '@directus/extensions-sdk'

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8001'

export default defineHook(({ filter }) => {
    // Filter runs before the item is created, allowing us to modify the item
    filter('items.create', async (input: any, { collection }) => {
        console.log(`[Favicon Extension] Processing collection: ${collection}`)

        // Only process resource_links and benefit_links collections
        if (!['resource_links', 'benefit_links'].includes(collection)) {
            console.log(`[Favicon Extension] Skipping collection: ${collection}`)
            return input
        }

        console.log(`[Favicon Extension] Input data:`, {
            url: input.url,
            favicon_url: input.favicon_url,
        })

        // Only fetch favicon if url exists and favicon_url is empty
        if (input.url && !input.favicon_url) {
            try {
                const apiUrl = `${API_BASE_URL}/v1/utils/favicon?url=${encodeURIComponent(input.url)}`
                console.log(`[Favicon Extension] Fetching favicon from: ${apiUrl}`)

                const response = await fetch(apiUrl)
                const data = await response.json()
                console.log(`[Favicon Extension] Received favicon data:`, data)
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }
                // Update the input with the favicon URL
                input.favicon_url = data.favicon_url
            } catch (error) {
                console.error('[Favicon Extension] Failed to fetch favicon:', error)
            }
        } else {
            console.log('[Favicon Extension] Skipping favicon fetch: URL missing or favicon_url already set')
        }

        return input
    })
})
