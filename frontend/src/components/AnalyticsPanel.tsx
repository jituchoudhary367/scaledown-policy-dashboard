import React from 'react';
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
    LineChart, Line, PieChart, Pie, Cell, Legend, AreaChart, Area
} from 'recharts';
import { AnalyticsData } from '../hooks/usePolicyData';

interface AnalyticsPanelProps {
    data: AnalyticsData | null;
}

const COLORS = ['#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981'];
const SENTIMENT_COLORS: Record<string, string> = {
    'Positive': '#10b981',
    'Neutral': '#3b82f6',
    'Negative': '#ef4444'
};

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({ data }) => {
    if (!data) {
        return (
            <div className="analytics-loading">
                <div className="loader"></div>
                <p>Aggregating policy trends...</p>
            </div>
        );
    }

    // Transform ministry data for BarChart
    const ministryData = Object.entries(data.by_ministry).map(([name, count]) => ({
        name,
        count
    })).sort((a, b) => b.count - a.count);

    // Transform entity data
    const entityData = Object.entries(data.by_entity).map(([name, count]) => ({
        name,
        count
    })).sort((a, b) => b.count - a.count).slice(0, 8);

    // Transform sentiment data
    const sentimentData = Object.entries(data.sentiment_distribution).map(([name, value]) => ({
        name,
        value
    }));

    return (
        <div className="analytics-container">
            <div className="analytics-grid">
                {/* Policy Activity Trend */}
                <div className="analytics-card full-width">
                    <h3 className="analytics-card-title">Policy Activity Trend (7 Days)</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={data.by_date}>
                                <defs>
                                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                                <YAxis stroke="#94a3b8" fontSize={12} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#111827', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}
                                    itemStyle={{ color: '#14b8a6' }}
                                />
                                <Area type="monotone" dataKey="count" stroke="#14b8a6" fillOpacity={1} fill="url(#colorCount)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Ministry Breakdown */}
                <div className="analytics-card">
                    <h3 className="analytics-card-title">Policy Heatmap by Ministry</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={ministryData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={10} width={80} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#111827', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}
                                />
                                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20}>
                                    {ministryData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sentiment Analysis */}
                <div className="analytics-card">
                    <h3 className="analytics-card-title">Sentiment Impact Distribution</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={sentimentData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {sentimentData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name] || '#94a3b8'} />
                                    ))}
                                </Pie>
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#111827', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}
                                />
                                <Legend verticalAlign="bottom" height={36}/>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Entity Focus */}
                <div className="analytics-card full-width">
                    <h3 className="analytics-card-title">Top 8 Affected Sectors</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={entityData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
                                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                                <YAxis stroke="#94a3b8" fontSize={12} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#111827', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}
                                />
                                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={40} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};
