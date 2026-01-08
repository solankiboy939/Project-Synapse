import React, { useState } from 'react';
import { 
  ChartBarIcon, 
  ClockIcon,
  UsersIcon,
  ServerIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

const queryTrends = [
  { month: 'Jul', queries: 1200, users: 45 },
  { month: 'Aug', queries: 1450, users: 52 },
  { month: 'Sep', queries: 1680, users: 58 },
  { month: 'Oct', queries: 1920, users: 64 },
  { month: 'Nov', queries: 2150, users: 71 },
  { month: 'Dec', queries: 2380, users: 78 },
  { month: 'Jan', queries: 2650, users: 85 }
];

const siloUsage = [
  { name: 'Engineering', queries: 1250, color: '#0ea5e9' },
  { name: 'Documentation', queries: 890, color: '#3b82f6' },
  { name: 'Support', queries: 650, color: '#8b5cf6' },
  { name: 'Security', queries: 420, color: '#d946ef' },
  { name: 'DevOps', queries: 380, color: '#06b6d4' },
  { name: 'Product', queries: 290, color: '#10b981' }
];

const responseTimeData = [
  { time: '00:00', avgTime: 180, p95Time: 320 },
  { time: '04:00', avgTime: 165, p95Time: 290 },
  { time: '08:00', avgTime: 245, p95Time: 450 },
  { time: '12:00', avgTime: 280, p95Time: 520 },
  { time: '16:00', avgTime: 320, p95Time: 580 },
  { time: '20:00', avgTime: 210, p95Time: 380 }
];

const topQueries = [
  { query: "How to implement OAuth2 authentication?", count: 156, avgTime: 245 },
  { query: "Database migration best practices", count: 142, avgTime: 198 },
  { query: "Container security scanning", count: 128, avgTime: 267 },
  { query: "API rate limiting strategies", count: 115, avgTime: 223 },
  { query: "Kubernetes deployment patterns", count: 98, avgTime: 289 }
];

const userEngagement = [
  { segment: 'Power Users', users: 25, queries: 1200, color: '#dc2626' },
  { segment: 'Regular Users', users: 45, queries: 800, color: '#ea580c' },
  { segment: 'Occasional Users', users: 85, queries: 300, color: '#ca8a04' },
  { segment: 'New Users', users: 35, queries: 150, color: '#65a30d' }
];

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d');

  const stats = {
    totalQueries: 2847,
    avgResponseTime: 245,
    activeUsers: 156,
    silosIndexed: 47,
    queryGrowth: 23.5,
    responseTimeChange: -12.3,
    userGrowth: 18.7,
    siloGrowth: 8.2
  };

  const StatCard = ({ title, value, change, icon: Icon, suffix = '' }) => (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">
            {typeof value === 'number' ? value.toLocaleString() : value}{suffix}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <Icon className="w-8 h-8 text-synapse-600 mb-2" />
          {change !== undefined && (
            <div className={`flex items-center text-sm ${
              change > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {change > 0 ? (
                <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
              ) : (
                <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
              )}
              {Math.abs(change)}%
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-2 text-gray-600">
            Insights into system usage, performance, and user behavior
          </p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="1d">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Queries"
          value={stats.totalQueries}
          change={stats.queryGrowth}
          icon={ChartBarIcon}
        />
        <StatCard
          title="Avg Response Time"
          value={stats.avgResponseTime}
          change={stats.responseTimeChange}
          icon={ClockIcon}
          suffix="ms"
        />
        <StatCard
          title="Active Users"
          value={stats.activeUsers}
          change={stats.userGrowth}
          icon={UsersIcon}
        />
        <StatCard
          title="Silos Indexed"
          value={stats.silosIndexed}
          change={stats.siloGrowth}
          icon={ServerIcon}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Query Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Query & User Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={queryTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="queries"
                stackId="1"
                stroke="#0ea5e9"
                fill="#0ea5e9"
                fillOpacity={0.6}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="users"
                stroke="#d946ef"
                strokeWidth={2}
                dot={{ fill: '#d946ef' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Silo Usage */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Silo Usage Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={siloUsage} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="queries" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Response Time Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Patterns</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="avgTime"
                stroke="#0ea5e9"
                strokeWidth={2}
                name="Average"
              />
              <Line
                type="monotone"
                dataKey="p95Time"
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="95th Percentile"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* User Engagement */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Engagement</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={userEngagement}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="users"
              >
                {userEngagement.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Queries */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Queries</h3>
          <div className="space-y-4">
            {topQueries.map((query, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {query.query}
                  </p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                    <span>{query.count} queries</span>
                    <span>{query.avgTime}ms avg</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-synapse-600">#{index + 1}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Insights */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h3>
          <div className="space-y-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />
                <span className="font-medium text-green-800">Improved Performance</span>
              </div>
              <p className="text-sm text-green-700">
                Average response time decreased by 12.3% this week due to index optimizations.
              </p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <ChartBarIcon className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-blue-800">Usage Growth</span>
              </div>
              <p className="text-sm text-blue-700">
                Query volume increased 23.5% with 18.7% more active users this month.
              </p>
            </div>
            
            <div className="p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <ClockIcon className="w-5 h-5 text-yellow-600" />
                <span className="font-medium text-yellow-800">Peak Hours</span>
              </div>
              <p className="text-sm text-yellow-700">
                Highest usage between 12-4 PM. Consider scaling during these hours.
              </p>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <ServerIcon className="w-5 h-5 text-purple-600" />
                <span className="font-medium text-purple-800">Silo Health</span>
              </div>
              <p className="text-sm text-purple-700">
                All 47 silos are healthy with 95%+ uptime. 3 new silos added this week.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}