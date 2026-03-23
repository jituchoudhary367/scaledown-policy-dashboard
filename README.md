# ScaleDown Policy Dashboard - Analytics Feature

This branch implements a comprehensive **Analytics and Trend Dashboard** for the ScaleDown Policy Dashboard.

## Key Features

### 1. Backend Analytics API
- **Endpoint**: `/api/analytics`
- **Functionality**: Aggregates policy data from various ministries and entities.
- **Sentiment Analysis**: Each policy is processed to determine sentiment (Positive, Neutral, Negative), providing a high-level view of policy reception.
- **Aggregation**: Data is grouped by Entity, Ministry, and Date to facilitate trends and comparison.

### 2. Frontend Visualization
- **Real-time Analytics**: New `AnalyticsPanel` added to the main dashboard.
- **Interactive Charts (Recharts)**:
    - **Policy Distribution Heatmap**: Visualizes volume across different ministries and entities.
    - **Trend Over Time**: Tracks the flow of policies across a timeline.
    - **Entity Cloud**: Highlights which entities are most active in policy changes.
    - **Sentiment Breakdown**: Pie chart showing the distribution of policy sentiment.
- **Seamless Integration**: Fully integrated into the existing dark-themed UI.

## Implementation Details
- **Frontend**: React, TypeScript, Recharts.
- **Backend**: FastAPI/Python, Sentiment Analysis logic.
- **State Management**: Updated `usePolicyData` hook to fetch and cache analytics data.
