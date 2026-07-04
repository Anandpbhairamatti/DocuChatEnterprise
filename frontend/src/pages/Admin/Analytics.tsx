import { useState, useEffect } from 'react';
import { api } from '../../api/axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock time series data since backend only provides aggregates
const mockTimeSeriesData = [
  { name: 'Mon', requests: 400 },
  { name: 'Tue', requests: 300 },
  { name: 'Wed', requests: 550 },
  { name: 'Thu', requests: 200 },
  { name: 'Fri', requests: 278 },
  { name: 'Sat', requests: 189 },
  { name: 'Sun', requests: 239 },
];

export default function Analytics() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get('/analytics/overview');
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="p-8 text-muted-foreground">Loading analytics...</div>;
  }

  if (!data) {
    return <div className="p-8 text-red-500">Failed to load analytics data.</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">System Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-muted-foreground">Total Users</h3>
          <p className="text-2xl font-bold mt-1">{data.users.total}</p>
        </div>
        <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-muted-foreground">Total Documents</h3>
          <p className="text-2xl font-bold mt-1">{data.documents.total}</p>
        </div>
        <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-muted-foreground">Est. AI Cost</h3>
          <p className="text-2xl font-bold mt-1">${data.ai.estimated_cost_usd.toFixed(4)}</p>
        </div>
        <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-muted-foreground">Avg Response Time</h3>
          <p className="text-2xl font-bold mt-1">{(data.ai.avg_response_time_ms / 1000).toFixed(2)}s</p>
        </div>
      </div>
      
      <div className="h-80 bg-card border border-border rounded-xl p-4 shadow-sm">
        <h3 className="text-sm font-medium text-muted-foreground mb-4">AI Usage Over Time (Weekly Mock)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={mockTimeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="name" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip 
              contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
              itemStyle={{ color: 'hsl(var(--foreground))' }}
            />
            <Line type="monotone" dataKey="requests" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
