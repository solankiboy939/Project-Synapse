import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ServerIcon, 
  MagnifyingGlassIcon, 
  ShieldCheckIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  UsersIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import apiService from '../services/api';

const mockStats = {
  totalSilos: 47,
  totalDocuments: 125000,
  queriesThisWeek: 2847,
  privacyBudgetUsed: 23.5,
  avgResponseTime: 245,
  activeUsers: 156
};

const queryData = [
  { name: 'Mon', queries: 420 },
  { name: 'Tue', queries: 380 },
  { name: 'Wed', queries: 450 },
  { name: 'Thu', queries: 520 },
  { name: 'Fri', queries: 610 },
  { name: 'Sat', queries: 280 },
  { name: 'Sun', queries: 187 }
];

const siloData = [
  { name: 'Engineering', value: 18, color: '#0ea5e9' },
  { name: 'Documentation', value: 12, color: '#3b82f6' },
  { name: 'Support', value: 8, color: '#8b5cf6' },
  { name: 'Security', value: 5, color: '#d946ef' },
  { name: 'Other', value: 4, color: '#6b7280' }
];

const recentQueries = [
  { query: "How to implement OAuth2 in microservices?", user: "Alice Chen", time: "2 minutes ago", results: 8 },
  { query: "Database migration best practices", user: "Bob Smith", time: "5 minutes ago", results: 12 },
  { query: "Container security scanning tools", user: "Carol Johnson", time: "8 minutes ago", results: 6 },
  { query: "API rate limiting strategies", user: "David Wilson", time: "12 minutes ago", results: 15 },
  { query: "Kubernetes deployment patterns", user: "Eve Davis", time: "18 minutes ago", results: 9 }
];

export default function Dashboard() {
  const [stats, setStats] = useState(mockStats);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load stats from API
    const loadStats = async () => {
      try {
        const data = await apiService.getStats();
        setStats(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to load stats:', error);
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const StatCard = ({ title, value, icon: Icon, change, color = "synapse" }) => (
    <div className="card">
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 bg-${color}-100 rounded-lg`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-baseline">
            <p className="text-2xl font-semibold text-gray-900">
              {loading ? (
                <div className="animate-pulse bg-gray-200 h-8 w-16 rounded"></div>
              ) : (
                value
              )}
            </p>
            {change && (
              <p className={`ml-2 flex items-baseline text-sm font-semibold ${
                change > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
                {change > 0 ? '+' : ''}{change}%
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to Project Synapse - Your Cross-Silo Knowledge Fabric
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link to="/query" className="btn-primary text-center block">
          <MagnifyingGlassIcon className="w-5 h-5 mx-auto mb-2" />
          New Query
        </Link>
        <Link to="/silos" className="btn-secondary text-center block">
          <ServerIcon className="w-5 h-5 mx-auto mb-2" />
          Manage Silos
        </Link>
        <Link to="/privacy" className="btn-secondary text-center block">
          <ShieldCheckIcon className="w-5 h-5 mx-auto mb-2" />
          Privacy Center
        </Link>
        <Link to="/demo" className="btn-secondary text-center block">
          <DocumentTextIcon className="w-5 h-5 mx-auto mb-2" />
          View Demo
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Active Silos"
          value={stats.totalSilos}
          icon={ServerIcon}
          change={12}
        />
        <StatCard
          title="Total Documents"
          value={stats.totalDocuments.toLocaleString()}
          icon={DocumentTextIcon}
          change={8}
        />
        <StatCard
          title="Queries This Week"
          value={stats.queriesThisWeek.toLocaleString()}
          icon={MagnifyingGlassIcon}
          change={15}
        />
        <StatCard
          title="Privacy Budget Used"
          value={`${stats.privacyBudgetUsed}%`}
          icon={ShieldCheckIcon}
          change={-5}
          color="privacy"
        />
        <StatCard
          title="Avg Response Time"
          value={`${stats.avgResponseTime}ms`}
          icon={ClockIcon}
          change={-12}
          color="green"
        />
        <StatCard
          title="Active Users"
          value={stats.activeUsers}
          icon={UsersIcon}
          change={23}
          color="blue"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Query Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Query Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={queryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="queries" 
                stroke="#0ea5e9" 
                strokeWidth={2}
                dot={{ fill: '#0ea5e9' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Silo Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Silo Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={siloData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {siloData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Queries */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Queries</h3>
          <div className="space-y-4">
            {recentQueries.map((query, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-synapse-100 rounded-full flex items-center justify-center">
                  <MagnifyingGlassIcon className="w-4 h-4 text-synapse-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {query.query}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{query.user}</span>
                    <span>•</span>
                    <span>{query.time}</span>
                    <span>•</span>
                    <span>{query.results} results</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">API Server</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-600">Healthy</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Database</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-600">Connected</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Redis Cache</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-600">Online</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Elasticsearch</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-sm text-yellow-600">Indexing</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Privacy Engine</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-600">Protected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}