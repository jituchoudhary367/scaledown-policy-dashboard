import { useState, useMemo, useEffect } from 'react'
import {
    FileText,
    Building2,
    GraduationCap,
    Sprout,
    Briefcase,
    Wallet,
    RefreshCw,
    Loader2,
    AlertCircle,
    X,
    ExternalLink,
    ChevronDown,
    ChevronUp,
    Search,
    TrendingUp,
    Clock,
    Star,
    Zap
} from 'lucide-react'
import { usePolicyData, Policy, NewsItem } from './hooks/usePolicyData'

// Citizen filter definitions
const citizenFilters = [
    { id: 'all', label: 'All Policies', icon: FileText, count: 0 },
    { id: 'startups', label: 'Startups', icon: Building2, count: 0 },
    { id: 'students', label: 'Students', icon: GraduationCap, count: 0 },
    { id: 'farmers', label: 'Farmers', icon: Sprout, count: 0 },
    { id: 'businesses', label: 'Businesses', icon: Briefcase, count: 0 },
    { id: 'taxpayers', label: 'Taxpayers', icon: Wallet, count: 0 }
]

const sources = ['All Sources', 'Parliament', 'PIB', 'MeitY', 'Gazette']
const feedTabs = [
    { id: 'latest', label: 'Latest', icon: Clock },
    { id: 'important', label: 'Important', icon: Star }
]

function formatDate(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 60) return `${minutes} min ago`
    if (hours < 24) return `${hours} hours ago`
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

// Article Detail Modal Component
function ArticleModal({
    policy,
    relatedPolicies,
    onClose,
    onSelectRelated
}: {
    policy: Policy,
    relatedPolicies: Policy[],
    onClose: () => void,
    onSelectRelated: (p: Policy) => void
}) {
    const [expanded, setExpanded] = useState(false)

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="modal-tags">
                        <span className={`policy-type ${policy.type}`}>{policy.type}</span>
                        {policy.importance === 'important' && (
                            <span className="importance-badge">
                                <Star size={12} /> Important
                            </span>
                        )}
                    </div>
                    <button className="modal-close" onClick={onClose} title="Close">
                        <X size={20} />
                    </button>
                </div>

                <h2 className="modal-title">{policy.title}</h2>

                <div className="modal-meta">
                    <span className="meta-item">
                        <Building2 size={14} />
                        {policy.source}
                    </span>
                    <span className="meta-item">
                        <Clock size={14} />
                        {formatDate(policy.published_date)}
                    </span>
                    <span className="meta-item">
                        {policy.ministry}
                    </span>
                </div>

                <div className="modal-section">
                    <h3>Summary</h3>
                    <div className="summary-content">
                        {policy.summary.split('\n').map((line, i) => (
                            <p key={i}>{line}</p>
                        ))}
                    </div>
                </div>

                <div className="modal-section">
                    <h3>Impact</h3>
                    <p className="impact-text">{policy.impact}</p>
                </div>

                <div className="modal-section">
                    <h3>Affected Sectors</h3>
                    <div className="entities-list">
                        {policy.entities.map(entity => (
                            <span key={entity} className="entity-tag">{entity}</span>
                        ))}
                    </div>
                </div>

                {relatedPolicies.length > 0 && (
                    <div className="modal-section related-section">
                        <h3>
                            <TrendingUp size={16} />
                            Related Articles
                        </h3>
                        <div className="related-list">
                            {relatedPolicies.map(p => (
                                <button
                                    key={p.id}
                                    className="related-item"
                                    onClick={() => onSelectRelated(p)}
                                >
                                    <span className="related-title">{p.title}</span>
                                    <span className="related-source">{p.source} • {formatDate(p.published_date)}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="modal-footer">
                    <a
                        href={policy.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="know-more-btn"
                    >
                        <ExternalLink size={16} />
                        Know More on Government Site
                    </a>
                </div>
            </div>
        </div>
    )
}

// Policy Card Component
function PolicyCard({
    policy,
    onViewDetails
}: {
    policy: Policy,
    onViewDetails: (p: Policy) => void
}) {
    const [expanded, setExpanded] = useState(false)

    return (
        <article className="policy-card">
            <div className="policy-header">
                <div className="policy-meta">
                    <span className={`policy-type ${policy.type}`}>{policy.type}</span>
                    {policy.importance === 'important' && (
                        <span className="importance-indicator">
                            <Star size={12} />
                        </span>
                    )}
                    <span className="policy-source">{policy.source}</span>
                    <span className="policy-time">{formatDate(policy.published_date)}</span>
                </div>
                <span className="policy-ministry">{policy.ministry}</span>
            </div>

            <h3 className="policy-title">{policy.title}</h3>

            <p className={`policy-summary ${expanded ? 'expanded' : ''}`}>
                {policy.summary}
            </p>

            {policy.summary.length > 150 && (
                <button
                    className="expand-btn"
                    onClick={() => setExpanded(!expanded)}
                >
                    {expanded ? (
                        <>Show Less <ChevronUp size={14} /></>
                    ) : (
                        <>Read More <ChevronDown size={14} /></>
                    )}
                </button>
            )}

            <div className="policy-impact">
                <span className="policy-impact-label">Impact:</span>
                <span>{policy.impact}</span>
            </div>

            <div className="policy-footer">
                <div className="policy-entities">
                    {policy.entities.slice(0, 3).map(entity => (
                        <span key={entity} className="entity-tag">{entity}</span>
                    ))}
                </div>
                <div className="policy-actions">
                    <button className="view-details-btn" onClick={() => onViewDetails(policy)}>
                        View Details
                    </button>
                    <a
                        href={policy.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="know-more-btn-card"
                    >
                        Know More
                    </a>
                </div>
            </div>
        </article>
    )
}

function App() {
    const {
        policies,
        news,
        stats,
        loading,
        error,
        lastUpdated,
        refreshData,
        filterBySource,
        filterByEntity,
        setFilter,
        activeFilter,
        activeSource,
        filterType
    } = usePolicyData()

    const [searchQuery, setSearchQuery] = useState('')
    const [isRefreshing, setIsRefreshing] = useState(false)
    const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null)

    // Update filter counts from stats
    const filtersWithCounts = useMemo(() => {
        return citizenFilters.map(filter => {
            if (filter.id === 'all') {
                return { ...filter, count: stats?.total_policies || 0 }
            }
            const filtered = policies.filter(p =>
                p.entities.some(e => e.toLowerCase().includes(filter.id.toLowerCase()))
            )
            return { ...filter, count: filtered.length }
        })
    }, [stats, policies])

    // Get filtered policies - real-time filtering
    const filteredPolicies = useMemo(() => {
        let result = policies

        // Source filter
        if (activeSource && activeSource !== 'All Sources') {
            result = result.filter(p => p.source.toLowerCase() === activeSource.toLowerCase())
        }

        // Entity filter
        if (activeFilter && activeFilter !== 'all') {
            result = result.filter(p =>
                p.entities.some(e => e.toLowerCase().includes(activeFilter.toLowerCase()))
            )
        }

        // Search filter
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase()
            result = result.filter(p =>
                p.title.toLowerCase().includes(query) ||
                p.summary.toLowerCase().includes(query) ||
                p.impact.toLowerCase().includes(query) ||
                p.entities.some(e => e.toLowerCase().includes(query))
            )
        }

        return result
    }, [policies, activeSource, activeFilter, searchQuery])

    // Get related policies for selected policy
    const getRelatedPolicies = (policy: Policy): Policy[] => {
        return policies
            .filter(p =>
                p.id !== policy.id &&
                (p.type === policy.type ||
                    p.ministry === policy.ministry ||
                    p.entities.some(e => policy.entities.includes(e)))
            )
            .slice(0, 4)
    }

    const handleRefresh = async () => {
        setIsRefreshing(true)
        await refreshData()
        setIsRefreshing(false)
    }

    const handleViewDetails = (policy: Policy) => {
        setSelectedPolicy(policy)
    }

    const handleSelectRelated = (policy: Policy) => {
        setSelectedPolicy(policy)
    }

    const handleNewsClick = (newsItem: NewsItem) => {
        // Open the real article in new tab
        window.open(newsItem.url, '_blank', 'noopener,noreferrer')
    }

    if (loading && !stats) {
        return (
            <div className="loading-screen">
                <Loader2 className="animate-spin" size={48} />
                <p>Loading policy data...</p>
            </div>
        )
    }

    return (
        <>
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">SD</div>
                        <div className="logo-text">ScaleDown <span>Policy</span></div>
                    </div>

                    <div className="header-stats">
                        <div className="stat-item">
                            <span className="stat-value">{stats?.total_policies.toLocaleString() || '—'}</span>
                            <span className="stat-label">Total Policies</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{stats?.active_updates || '—'}</span>
                            <span className="stat-label">Active Updates</span>
                        </div>
                    </div>

                    <div className="header-actions">
                        <button
                            className="refresh-btn"
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                        >
                            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
                            {isRefreshing ? 'Refreshing...' : 'Refresh'}
                        </button>
                        <div className="live-indicator">
                            <span className="live-dot"></span>
                            Live Updates
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Container */}
            <main className="main-container">
                {/* Left Sidebar */}
                <aside className="sidebar">
                    {/* Search */}
                    <div className="card search-card">
                        <div className="search-input-wrapper">
                            <Search size={18} className="search-icon" />
                            <input
                                type="text"
                                placeholder="Search policies..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="search-input"
                            />
                        </div>
                    </div>

                    {/* Citizen Filters */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">👥 Citizen Filters</h2>
                        </div>
                        <div className="filter-group">
                            {filtersWithCounts.map(filter => (
                                <button
                                    key={filter.id}
                                    className={`filter-btn ${activeFilter === filter.id ? 'active' : ''}`}
                                    data-filter={filter.id}
                                    onClick={() => filterByEntity(filter.id)}
                                >
                                    <span className="filter-icon">
                                        <filter.icon size={16} />
                                    </span>
                                    <span className="filter-label">{filter.label}</span>
                                    <span className="filter-count">{filter.count.toLocaleString()}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Source Filters */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">📡 Sources</h2>
                        </div>
                        <div className="source-filters">
                            {sources.map(source => (
                                <button
                                    key={source}
                                    className={`source-btn ${activeSource === source ? 'active' : ''}`}
                                    onClick={() => filterBySource(source)}
                                >
                                    {source}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Policy Timeline */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">📅 Policy Timeline</h2>
                        </div>
                        <div className="timeline">
                            <div className="timeline-item active">
                                <div className="timeline-stage">Bill Passed</div>
                                <div className="timeline-date">Mar 2026</div>
                            </div>
                            <div className="timeline-item">
                                <div className="timeline-stage">Parliament Discussion</div>
                                <div className="timeline-date">Feb 2026</div>
                            </div>
                            <div className="timeline-item">
                                <div className="timeline-stage">Draft Published</div>
                                <div className="timeline-date">Jan 2026</div>
                            </div>
                            <div className="timeline-item">
                                <div className="timeline-stage">Committee Review</div>
                                <div className="timeline-date">Dec 2025</div>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Main Feed */}
                <section className="main-feed">
                    <div className="feed-header">
                        <h2 className="feed-title">📜 Latest Policy Updates</h2>
                        <div className="feed-tabs">
                            {feedTabs.map(tab => (
                                <button
                                    key={tab.id}
                                    className={`feed-tab ${filterType === tab.id ? 'active' : ''}`}
                                    onClick={() => setFilter(filterType === tab.id ? null : tab.id)}
                                >
                                    <tab.icon size={14} />
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="error-banner">
                            <AlertCircle size={20} />
                            <span>{error}</span>
                            <button onClick={refreshData}>Retry</button>
                        </div>
                    )}

                    {/* Policy Cards */}
                    {filteredPolicies.length === 0 ? (
                        <div className="empty-state">
                            <FileText size={48} />
                            <h3>No policies found</h3>
                            <p>Try adjusting your filters or search query</p>
                        </div>
                    ) : (
                        filteredPolicies.map(policy => (
                            <PolicyCard
                                key={policy.id}
                                policy={policy}
                                onViewDetails={handleViewDetails}
                            />
                        ))
                    )}
                </section>

                {/* Right Panel */}
                <aside className="right-panel">
                    {/* Policy News - Clickable to open real articles */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">📰 Policy News</h2>
                        </div>
                        <div>
                            {news.slice(0, 8).map(item => (
                                <div
                                    key={item.id}
                                    className="news-item clickable"
                                    onClick={() => handleNewsClick(item)}
                                >
                                    <div className="news-icon">
                                        <FileText size={18} />
                                    </div>
                                    <div className="news-content">
                                        <div className="news-title">{item.title}</div>
                                        <div className="news-meta">{item.source} • {formatDate(item.published_date)}</div>
                                    </div>
                                    <ExternalLink size={14} className="news-external-icon" />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Last Updated */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">🔄 Last Updated</h2>
                        </div>
                        <div className="last-updated">
                            {lastUpdated ? lastUpdated.toLocaleString() : 'Never'}
                        </div>
                        <p className="update-note">Data refreshes every 6 hours</p>
                    </div>
                </aside>
            </main>

            {/* Article Detail Modal */}
            {selectedPolicy && (
                <ArticleModal
                    policy={selectedPolicy}
                    relatedPolicies={getRelatedPolicies(selectedPolicy)}
                    onClose={() => setSelectedPolicy(null)}
                    onSelectRelated={handleSelectRelated}
                />
            )}
        </>
    )
}

export default App
