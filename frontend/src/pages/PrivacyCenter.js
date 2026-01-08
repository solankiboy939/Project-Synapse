import React, { useState } from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ArrowPathIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const privacyBudgetData = {
  global: 50.0,
  used: 12.3,
  remaining: 37.7,
  dailyUsage: [
    { day: 'Mon', usage: 2.1 },
    { day: 'Tue', usage: 1.8 },
    { day: 'Wed', usage: 2.4 },
    { day: 'Thu', usage: 3.2 },
    { day: 'Fri', usage: 2.8 },
    { day: 'Sat', usage: 0.8 },
    { day: 'Sun', usage: 0.5 }
  ]
};

const mechanismUsage = [
  { name: 'Gaussian Noise', value: 45, color: '#0ea5e9' },
  { name: 'Laplace Noise', value: 30, color: '#3b82f6' },
  { name: 'Exponential Mechanism', value: 15, color: '#8b5cf6' },
  { name: 'Private Histogram', value: 10, color: '#d946ef' }
];

const accessLogs = [
  {
    id: 1,
    timestamp: '2024-01-09T10:30:15Z',
    user: 'john.doe@company.com',
    action: 'Query Execution',
    silo: 'Engineering Docs',
    privacyBudget: 0.15,
    status: 'success'
  },
  {
    id: 2,
    timestamp: '2024-01-09T10:28:42Z',
    user: 'alice.chen@company.com',
    action: 'Silo Access',
    silo: 'Security KB',
    privacyBudget: 0.08,
    status: 'success'
  },
  {
    id: 3,
    timestamp: '2024-01-09T10:25:33Z',
    user: 'bob.smith@company.com',
    action: 'Knowledge Synthesis',
    silo: 'Multiple Silos',
    privacyBudget: 0.22,
    status: 'success'
  },
  {
    id: 4,
    timestamp: '2024-01-09T10:22:18Z',
    user: 'carol.johnson@company.com',
    action: 'Query Execution',
    silo: 'Code Repository',
    privacyBudget: 0.12,
    status: 'denied'
  }
];

const complianceStatus = [
  { framework: 'GDPR', status: 'compliant', lastAudit: '2024-01-05', nextAudit: '2024-04-05' },
  { framework: 'SOX', status: 'compliant', lastAudit: '2024-01-03', nextAudit: '2024-04-03' },
  { framework: 'FedRAMP', status: 'compliant', lastAudit: '2023-12-15', nextAudit: '2024-03-15' },
  { framework: 'HIPAA', status: 'not_applicable', lastAudit: null, nextAudit: null }
];

export default function PrivacyCenter() {
  const [budgetData, setBudgetData] = useState(privacyBudgetData);
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');
  const [showResetModal, setShowResetModal] = useState(false);

  const handleResetBudget = () => {
    setBudgetData(prev => ({
      ...prev,
      used: 0,
      remaining: prev.global
    }));
    setShowResetModal(false);
    toast.success('Privacy budget reset successfully');
    toast.error('⚠️ All previous privacy guarantees are now void', { duration: 6000 });
  };

  const getBudgetColor = (percentage) => {
    if (percentage < 50) return 'text-green-600';
    if (percentage < 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'non_compliant': return 'text-red-600 bg-red-100';
      case 'not_applicable': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const usagePercentage = (budgetData.used / budgetData.global) * 100;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Privacy Center</h1>
          <p className="mt-2 text-gray-600">
            Monitor privacy budget usage, compliance status, and access controls
          </p>
        </div>
        <button
          onClick={() => setShowResetModal(true)}
          className="btn-secondary flex items-center space-x-2 text-red-600 hover:bg-red-50"
        >
          <ArrowPathIcon className="w-5 h-5" />
          <span>Reset Budget</span>
        </button>
      </div>

      {/* Privacy Budget Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy Budget Usage</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">{budgetData.global}</div>
                <div className="text-sm text-gray-600">Global Budget</div>
              </div>
              <div className="text-center">
                <div className={`text-3xl font-bold ${getBudgetColor(usagePercentage)}`}>
                  {budgetData.used.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Used</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{budgetData.remaining.toFixed(1)}</div>
                <div className="text-sm text-gray-600">Remaining</div>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>Budget Utilization</span>
                <span>{usagePercentage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-300 ${
                    usagePercentage < 50 ? 'bg-green-500' :
                    usagePercentage < 80 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                ></div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={budgetData.dailyUsage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="#d946ef" 
                  strokeWidth={2}
                  dot={{ fill: '#d946ef' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6">
          {/* Privacy Mechanisms */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Mechanism Usage</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={mechanismUsage}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mechanismUsage.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {mechanismUsage.map((mechanism, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: mechanism.color }}
                    ></div>
                    <span className="text-gray-700">{mechanism.name}</span>
                  </div>
                  <span className="text-gray-600">{mechanism.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Privacy Alerts */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy Alerts</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-yellow-800">
                    High Budget Usage
                  </div>
                  <div className="text-xs text-yellow-700">
                    Privacy budget usage is approaching 25%
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <InformationCircleIcon className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-blue-800">
                    Compliance Check Due
                  </div>
                  <div className="text-xs text-blue-700">
                    FedRAMP audit scheduled for next month
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="card mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {complianceStatus.map((compliance, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{compliance.framework}</h4>
                <span className={`badge ${getStatusColor(compliance.status)}`}>
                  {compliance.status === 'compliant' && <ShieldCheckIcon className="w-3 h-3 mr-1" />}
                  {compliance.status.replace('_', ' ')}
                </span>
              </div>
              {compliance.lastAudit && (
                <div className="text-xs text-gray-600">
                  <div>Last audit: {new Date(compliance.lastAudit).toLocaleDateString()}</div>
                  <div>Next audit: {new Date(compliance.nextAudit).toLocaleDateString()}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Access Logs */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Access Logs</h3>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="hour">Last Hour</option>
            <option value="day">Last Day</option>
            <option value="week">Last Week</option>
          </select>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Silo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Privacy Budget
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {accessLogs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <UserIcon className="w-4 h-4 text-gray-600" />
                      </div>
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">
                          {log.user.split('@')[0]}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.action}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.silo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.privacyBudget.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${
                      log.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reset Budget Modal */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl max-w-md w-full p-6"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Reset Privacy Budget</h3>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-600 mb-4">
                Are you sure you want to reset the privacy budget? This action will:
              </p>
              <ul className="text-sm text-gray-600 space-y-1 ml-4">
                <li>• Reset the used budget to 0</li>
                <li>• Void all previous privacy guarantees</li>
                <li>• Allow new queries with fresh privacy budget</li>
                <li>• Create an audit log entry</li>
              </ul>
              <div className="mt-4 p-3 bg-red-50 rounded-lg">
                <p className="text-sm text-red-800 font-medium">
                  ⚠️ This action cannot be undone and may impact compliance status.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button 
                onClick={handleResetBudget}
                className="btn-primary bg-red-600 hover:bg-red-700 flex-1"
              >
                Reset Budget
              </button>
              <button 
                onClick={() => setShowResetModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}