import { useState, useEffect, useCallback } from 'react'

export interface Policy {
    id: string
    title: string
    type: string
    source: string
    source_url: string
    ministry: string
    published_date: string
    summary: string
    impact: string
    entities: string[]
    importance: string
    scraped_at: string
}

export interface NewsItem {
    id: string
    title: string
    source: string
    source_url: string
    published_date: string
    summary: string
    category: string
    url: string
}

export interface DashboardStats {
    total_policies: number
    active_updates: number
    sources: string[]
    last_updated: string
}

export interface AnalyticsData {
    by_ministry: Record<string, number>
    by_entity: Record<string, number>
    by_date: Array<{ date: string, count: number }>
    sentiment_distribution: Record<string, number>
}

export interface DashboardData {
    policies: Policy[]
    news: NewsItem[]
    stats: DashboardStats
}

const API_BASE = 'http://localhost:8000/api'

export function usePolicyData() {
    const [policies, setPolicies] = useState<Policy[]>([])
    const [news, setNews] = useState<NewsItem[]>([])
    const [stats, setStats] = useState<DashboardStats | null>(null)
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

    // Filter states
    const [activeFilter, setActiveFilter] = useState('all')
    const [activeSource, setActiveSource] = useState('All Sources')
    const [filterType, setFilterType] = useState<string | null>(null)

    const fetchData = useCallback(async () => {
        try {
            setLoading(true)

            // Build query params
            let url = `${API_BASE}/dashboard`
            const params = new URLSearchParams()

            if (activeSource && activeSource !== 'All Sources') {
                params.append('source', activeSource.toLowerCase())
            }
            if (activeFilter && activeFilter !== 'all') {
                params.append('entity', activeFilter)
            }
            if (filterType) {
                params.append('filter_type', filterType)
            }

            if (params.toString()) {
                url += '?' + params.toString()
            }

            const response = await fetch(url)

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data: DashboardData = await response.json()
            setPolicies(data.policies)
            setNews(data.news)
            setStats(data.stats)
            setLastUpdated(new Date(data.stats.last_updated))
            
            // Fetch analytics separately
            try {
                const analyticsRes = await fetch(`${API_BASE}/analytics`)
                if (analyticsRes.ok) {
                    const analyticsData: AnalyticsData = await analyticsRes.json()
                    setAnalytics(analyticsData)
                }
            } catch (aErr) {
                console.error('Failed to fetch analytics:', aErr)
            }

            setError(null)
        } catch (err) {
            console.error('Failed to fetch policy data:', err)
            setError(err instanceof Error ? err.message : 'Failed to fetch data')
        } finally {
            setLoading(false)
        }
    }, [activeSource, activeFilter, filterType])

    const refreshData = useCallback(async () => {
        try {
            await fetch(`${API_BASE}/refresh`, { method: 'POST' })
            await fetchData()
        } catch (err) {
            console.error('Failed to refresh data:', err)
        }
    }, [fetchData])

    // Initial fetch
    useEffect(() => {
        fetchData()
    }, [fetchData])

    // Auto-refresh every 6 hours
    useEffect(() => {
        const interval = setInterval(() => {
            refreshData()
        }, 6 * 60 * 60 * 1000)
        return () => clearInterval(interval)
    }, [refreshData])

    // Filter functions
    const filterBySource = useCallback((source: string) => {
        setActiveSource(source)
    }, [])

    const filterByEntity = useCallback((entity: string) => {
        setActiveFilter(entity)
    }, [])

    const setFilter = useCallback((type: string | null) => {
        setFilterType(type)
    }, [])

    return {
        policies,
        news,
        stats,
        analytics,
        loading,
        error,
        lastUpdated,
        refreshData,
        fetchData,
        filterBySource,
        filterByEntity,
        setFilter,
        activeFilter,
        activeSource,
        filterType
    }
}
