import React, { useState } from 'react';
import { 
  ServerIcon, 
  PlusIcon, 
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  ChatBubbleLeftRightIcon,
  BugAntIcon
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const mockSilos = [
  {
    id: 'eng-docs',
    name: 'Engineering Documentation',
    type: 'documentation',
    organization: 'ACME Corp',
    team: 'Engineering',
    status: 'healthy',
    documents: 1250,
    lastIndexed: '2024-01-09T08:30:00Z',
    accessLevel: 'Internal',
    indexingProgress: 100,
    description: 'Technical documentation, API specs, and architecture guides'
  },
  {
    id: 'code-repo',
    name: 'Main Code Repository',
    type: 'code_repository', 
    organization: 'ACME Corp',
    team: 'Engineering',
    status: 'indexing',
    documents: 8500,
    lastIndexed: '2024-01-09T09:15:00Z',
    accessLevel: 'Confidential',
    indexingProgress: 67,
    description: 'Source code, commit messages, and pull request discussions'
  },
  {
    id: 'support-kb',
    name: 'Customer Support KB',
    type: 'knowledge_base',
    organization: 'ACME Corp', 
    team: 'Support',
    status: 'healthy',
    documents: 890,
    lastIndexed: '2024-01-09T07:45:00Z',
    accessLevel: 'Internal',
    indexingProgress: 100,
    description: 'Customer issues, solutions, and troubleshooting guides'
  },
  {
    id: 'security-docs',
    name: 'Security Documentation',
    type: 'documentation',
    organization: 'ACME Corp',
    team: 'Security',
    status: 'error',
    documents: 340,
    lastIndexed: '2024-01-08T16:20:00Z',
    accessLevel: 'Restricted',
    indexingProgress: 0,
    description: 'Security policies, incident reports, and compliance docs'
  },
  {
    id: 'chat-history',
    name: 'Team Chat Archives',
    type: 'chat_history',
    organization: 'ACME Corp',
    team: 'Engineering',
    status: 'healthy',
    documents: 15600,
    lastIndexed: '2024-01-09T06:00:00Z',
    accessLevel: 'Internal',
    indexingProgress: 100,
    description: 'Slack conversations, decisions, and informal knowledge sharing'
  }
];

const siloTypes = [
  { value: 'documentation', label: 'Documentation', icon: DocumentTextIcon },
  { value: 'code_repository', label: 'Code Repository', icon: CodeBracketIcon },
  { value: 'knowledge_base', label: 'Knowledge Base', icon: ServerIcon },
  { value: 'chat_history', label: 'Chat History', icon: ChatBubbleLeftRightIcon },
  { value: 'issue_tracker', label: 'Issue Tracker', icon: BugAntIcon }
];

const accessLevels = [
  { value: 'public', label: 'Public', color: 'green' },
  { value: 'internal', label: 'Internal', color: 'blue' },
  { value: 'confidential', label: 'Confidential', color: 'yellow' },
  { value: 'restricted', label: 'Restricted', color: 'red' }
];

export default function SiloManagement() {
  const [silos, setSilos] = useState(mockSilos);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSilo, setNewSilo] = useState({
    name: '',
    type: 'documentation',
    organization: 'ACME Corp',
    team: '',
    accessLevel: 'internal',
    description: ''
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'indexing': return 'text-blue-600 bg-blue-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAccessLevelColor = (level) => {
    const levelConfig = accessLevels.find(l => l.value === level.toLowerCase());
    const color = levelConfig?.color || 'gray';
    return `text-${color}-600 bg-${color}-100`;
  };

  const getSiloTypeIcon = (type) => {
    const typeConfig = siloTypes.find(t => t.value === type);
    return typeConfig?.icon || ServerIcon;
  };

  const handleAddSilo = () => {
    if (!newSilo.name || !newSilo.team) {
      toast.error('Please fill in all required fields');
      return;
    }

    const silo = {
      id: `${newSilo.type}-${Date.now()}`,
      ...newSilo,
      status: 'indexing',
      documents: 0,
      lastIndexed: new Date().toISOString(),
      indexingProgress: 0
    };

    setSilos(prev => [...prev, silo]);
    setNewSilo({
      name: '',
      type: 'documentation',
      organization: 'ACME Corp',
      team: '',
      accessLevel: 'internal',
      description: ''
    });
    setShowAddModal(false);
    toast.success('Silo added successfully');

    // Simulate indexing progress
    setTimeout(() => {
      setSilos(prev => prev.map(s => 
        s.id === silo.id 
          ? { ...s, status: 'healthy', indexingProgress: 100, documents: Math.floor(Math.random() * 1000) + 100 }
          : s
      ));
      toast.success('Silo indexing completed');
    }, 3000);
  };

  const handleDeleteSilo = (siloId) => {
    setSilos(prev => prev.filter(s => s.id !== siloId));
    toast.success('Silo deleted successfully');
  };

  const handleReindex = (siloId) => {
    setSilos(prev => prev.map(s => 
      s.id === siloId 
        ? { ...s, status: 'indexing', indexingProgress: 0 }
        : s
    ));
    toast.success('Reindexing started');

    // Simulate reindexing progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setSilos(prev => prev.map(s => 
          s.id === siloId 
            ? { ...s, status: 'healthy', indexingProgress: 100, lastIndexed: new Date().toISOString() }
            : s
        ));
        toast.success('Reindexing completed');
      } else {
        setSilos(prev => prev.map(s => 
          s.id === siloId 
            ? { ...s, indexingProgress: Math.floor(progress) }
            : s
        ));
      }
    }, 500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Silo Management</h1>
          <p className="mt-2 text-gray-600">
            Manage organizational data silos and their indexing status
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Add Silo</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card text-center">
          <div className="text-2xl font-bold text-gray-900">{silos.length}</div>
          <div className="text-sm text-gray-600">Total Silos</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-gray-900">
            {silos.reduce((sum, s) => sum + s.documents, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Documents</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {silos.filter(s => s.status === 'healthy').length}
          </div>
          <div className="text-sm text-gray-600">Healthy Silos</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-600">
            {silos.filter(s => s.status === 'indexing').length}
          </div>
          <div className="text-sm text-gray-600">Indexing</div>
        </div>
      </div>

      {/* Silos Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnimatePresence>
          {silos.map((silo) => {
            const TypeIcon = getSiloTypeIcon(silo.type);
            return (
              <motion.div
                key={silo.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-synapse-100 rounded-lg flex items-center justify-center">
                      <TypeIcon className="w-6 h-6 text-synapse-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{silo.name}</h3>
                      <p className="text-sm text-gray-600">{silo.team} • {silo.organization}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`badge ${getStatusColor(silo.status)}`}>
                      {silo.status === 'healthy' && <CheckCircleIcon className="w-3 h-3 mr-1" />}
                      {silo.status === 'error' && <ExclamationTriangleIcon className="w-3 h-3 mr-1" />}
                      {silo.status === 'indexing' && <ClockIcon className="w-3 h-3 mr-1 animate-spin" />}
                      {silo.status}
                    </span>
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-4">{silo.description}</p>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-sm text-gray-500">Documents</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {silo.documents.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Access Level</div>
                    <span className={`badge ${getAccessLevelColor(silo.accessLevel)}`}>
                      {silo.accessLevel}
                    </span>
                  </div>
                </div>

                {silo.status === 'indexing' && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>Indexing Progress</span>
                      <span>{silo.indexingProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-synapse-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${silo.indexingProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span>Last indexed: {new Date(silo.lastIndexed).toLocaleDateString()}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleReindex(silo.id)}
                    disabled={silo.status === 'indexing'}
                    className="btn-secondary text-sm disabled:opacity-50"
                  >
                    Reindex
                  </button>
                  <button
                    onClick={() => {
                      // setEditingSilo(silo); // Commented out for now
                      console.log('Edit silo:', silo.id);
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteSilo(silo.id)}
                    className="p-2 text-gray-400 hover:text-red-600"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Add Silo Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl max-w-md w-full p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Silo</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Silo Name *
                </label>
                <input
                  type="text"
                  value={newSilo.name}
                  onChange={(e) => setNewSilo(prev => ({ ...prev, name: e.target.value }))}
                  className="input-field"
                  placeholder="e.g., Engineering Documentation"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  value={newSilo.type}
                  onChange={(e) => setNewSilo(prev => ({ ...prev, type: e.target.value }))}
                  className="input-field"
                >
                  {siloTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team *
                </label>
                <input
                  type="text"
                  value={newSilo.team}
                  onChange={(e) => setNewSilo(prev => ({ ...prev, team: e.target.value }))}
                  className="input-field"
                  placeholder="e.g., Engineering"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Level
                </label>
                <select
                  value={newSilo.accessLevel}
                  onChange={(e) => setNewSilo(prev => ({ ...prev, accessLevel: e.target.value }))}
                  className="input-field"
                >
                  {accessLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newSilo.description}
                  onChange={(e) => setNewSilo(prev => ({ ...prev, description: e.target.value }))}
                  className="input-field"
                  rows={3}
                  placeholder="Brief description of the silo content..."
                />
              </div>
            </div>

            <div className="flex items-center space-x-3 mt-6">
              <button onClick={handleAddSilo} className="btn-primary flex-1">
                Add Silo
              </button>
              <button 
                onClick={() => setShowAddModal(false)}
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