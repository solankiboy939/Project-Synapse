import React, { useState } from 'react';
import { 
  PlayIcon, 
  ArrowPathIcon,
  CheckCircleIcon,
  ClockIcon,
  ServerIcon,
  ShieldCheckIcon,
  SparklesIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';

const demoScenarios = [
  {
    id: 'basic',
    title: 'Basic Federated Search',
    description: 'Demonstrate simple cross-silo search with privacy preservation',
    steps: [
      'Initialize 3 organizational silos (Engineering, Security, Support)',
      'Index documents with differential privacy',
      'Execute federated query: "API authentication best practices"',
      'Show results from multiple silos with access control',
      'Display privacy budget consumption'
    ]
  },
  {
    id: 'enterprise',
    title: 'Enterprise Scale Simulation',
    description: 'Large-scale demonstration with multiple organizations and users',
    steps: [
      'Create enterprise setup: AWS, Google, Microsoft organizations',
      'Generate 60+ silos across different teams',
      'Simulate 4 user personas with different access levels',
      'Execute complex queries across organizational boundaries',
      'Calculate ROI: $375M annual savings for 10k engineers'
    ]
  },
  {
    id: 'synthesis',
    title: 'Knowledge Synthesis',
    description: 'Show AI-powered knowledge synthesis from multiple sources',
    steps: [
      'Search for "microservices deployment patterns"',
      'Retrieve results from Engineering, DevOps, and Security teams',
      'Synthesize knowledge while maintaining source attribution',
      'Show confidence scoring and access limitations',
      'Generate follow-up questions'
    ]
  }
];

const mockLogs = [
  { time: '10:30:15', level: 'INFO', message: 'Initializing Synapse demo environment...' },
  { time: '10:30:16', level: 'INFO', message: 'Creating organizational silos...' },
  { time: '10:30:17', level: 'SUCCESS', message: '✅ Engineering silo created (100 documents)' },
  { time: '10:30:18', level: 'SUCCESS', message: '✅ Security silo created (75 documents)' },
  { time: '10:30:19', level: 'SUCCESS', message: '✅ Support silo created (120 documents)' },
  { time: '10:30:20', level: 'INFO', message: 'Generating embeddings with privacy noise...' },
  { time: '10:30:22', level: 'SUCCESS', message: '✅ Federated index built successfully' },
  { time: '10:30:23', level: 'INFO', message: 'Privacy budget: 8.5/10.0 remaining' },
  { time: '10:30:24', level: 'INFO', message: 'Executing query: "API authentication best practices"' },
  { time: '10:30:25', level: 'INFO', message: 'Checking permissions for user: john.doe@company.com' },
  { time: '10:30:26', level: 'SUCCESS', message: '✅ Found 8 results across 3 silos' },
  { time: '10:30:27', level: 'INFO', message: 'Synthesizing knowledge from multiple sources...' },
  { time: '10:30:29', level: 'SUCCESS', message: '✅ Synthesis completed (confidence: 89%)' },
  { time: '10:30:30', level: 'INFO', message: 'Demo completed successfully! 🎉' }
];

const enterpriseStats = {
  organizations: 3,
  totalSilos: 60,
  totalDocuments: 600000,
  users: 4,
  queriesExecuted: 20,
  privacyBudgetUsed: 15.2,
  avgResponseTime: 245,
  roiCalculation: {
    engineers: 10000,
    avgSalary: 150000,
    timeSavings: 0.25,
    annualSavings: 375000000,
    fiveYearROI: 1875000000
  }
};

export default function Demo() {
  const [selectedScenario, setSelectedScenario] = useState('basic');
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [logs, setLogs] = useState([]);
  const [showStats, setShowStats] = useState(false);

  const runDemo = async () => {
    setIsRunning(true);
    setCurrentStep(0);
    setLogs([]);
    setShowStats(false);

    const scenario = demoScenarios.find(s => s.id === selectedScenario);
    
    // Simulate demo execution
    for (let i = 0; i < scenario.steps.length; i++) {
      setCurrentStep(i);
      
      // Add relevant logs for each step
      const stepLogs = mockLogs.slice(i * 2, (i + 1) * 3);
      for (const log of stepLogs) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setLogs(prev => [...prev, log]);
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    if (selectedScenario === 'enterprise') {
      setShowStats(true);
    }

    setIsRunning(false);
  };

  const resetDemo = () => {
    setIsRunning(false);
    setCurrentStep(0);
    setLogs([]);
    setShowStats(false);
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'SUCCESS': return 'text-green-600';
      case 'INFO': return 'text-blue-600';
      case 'WARNING': return 'text-yellow-600';
      case 'ERROR': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Interactive Demo
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Experience Project Synapse in action with interactive demonstrations 
          showcasing federated search, privacy preservation, and knowledge synthesis
        </p>
      </div>

      {/* Scenario Selection */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Choose Demo Scenario</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {demoScenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => setSelectedScenario(scenario.id)}
              className={`text-left p-6 rounded-xl border-2 transition-all duration-200 ${
                selectedScenario === scenario.id
                  ? 'border-synapse-500 bg-synapse-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {scenario.title}
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                {scenario.description}
              </p>
              <div className="text-xs text-gray-500">
                {scenario.steps.length} steps
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Demo Controls */}
      <div className="flex items-center justify-center space-x-4 mb-8">
        <button
          onClick={runDemo}
          disabled={isRunning}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <ArrowPathIcon className="w-5 h-5 animate-spin" />
              <span>Running Demo...</span>
            </>
          ) : (
            <>
              <PlayIcon className="w-5 h-5" />
              <span>Run Demo</span>
            </>
          )}
        </button>
        
        <button
          onClick={resetDemo}
          className="btn-secondary flex items-center space-x-2"
        >
          <ArrowPathIcon className="w-5 h-5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Demo Progress */}
      {(isRunning || currentStep > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Steps Progress */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Demo Progress</h3>
            <div className="space-y-4">
              {demoScenarios.find(s => s.id === selectedScenario).steps.map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                    index < currentStep 
                      ? 'bg-green-100 text-green-600' 
                      : index === currentStep && isRunning
                      ? 'bg-synapse-100 text-synapse-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}>
                    {index < currentStep ? (
                      <CheckCircleIcon className="w-4 h-4" />
                    ) : index === currentStep && isRunning ? (
                      <ArrowPathIcon className="w-4 h-4 animate-spin" />
                    ) : (
                      <span className="text-xs font-medium">{index + 1}</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm ${
                      index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {step}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Logs */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Logs</h3>
            <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
              <AnimatePresence>
                {logs.map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="mb-1"
                  >
                    <span className="text-gray-400">[{log.time}]</span>
                    <span className={`ml-2 ${getLogLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className="ml-2 text-gray-300">{log.message}</span>
                  </motion.div>
                ))}
              </AnimatePresence>
              {logs.length === 0 && (
                <div className="text-gray-500 text-center py-8">
                  Logs will appear here when demo is running...
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Enterprise Stats */}
      {showStats && selectedScenario === 'enterprise' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Enterprise Demo Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="card text-center">
              <ServerIcon className="w-8 h-8 text-synapse-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900">{enterpriseStats.totalSilos}</div>
              <div className="text-sm text-gray-600">Total Silos</div>
            </div>
            
            <div className="card text-center">
              <ChartBarIcon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900">
                {enterpriseStats.totalDocuments.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Documents Indexed</div>
            </div>
            
            <div className="card text-center">
              <ClockIcon className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900">{enterpriseStats.avgResponseTime}ms</div>
              <div className="text-sm text-gray-600">Avg Response Time</div>
            </div>
            
            <div className="card text-center">
              <ShieldCheckIcon className="w-8 h-8 text-privacy-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900">{enterpriseStats.privacyBudgetUsed}%</div>
              <div className="text-sm text-gray-600">Privacy Budget Used</div>
            </div>
          </div>

          {/* ROI Calculation */}
          <div className="card gradient-bg text-white">
            <h4 className="text-xl font-semibold mb-4">Enterprise ROI Calculation</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h5 className="font-semibold mb-3">Assumptions:</h5>
                <ul className="space-y-2 text-sm opacity-90">
                  <li>• {enterpriseStats.roiCalculation.engineers.toLocaleString()} engineers</li>
                  <li>• ${enterpriseStats.roiCalculation.avgSalary.toLocaleString()} average salary</li>
                  <li>• {enterpriseStats.roiCalculation.timeSavings * 100}% time savings on search/discovery</li>
                  <li>• Reduced duplicate work and faster onboarding</li>
                </ul>
              </div>
              <div>
                <h5 className="font-semibold mb-3">Financial Impact:</h5>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Annual Savings:</span>
                    <span className="font-bold">
                      ${(enterpriseStats.roiCalculation.annualSavings / 1000000).toFixed(0)}M
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>5-Year ROI:</span>
                    <span className="font-bold">
                      ${(enterpriseStats.roiCalculation.fiveYearROI / 1000000000).toFixed(1)}B
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Payback Period:</span>
                    <span className="font-bold">6-9 months</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Demo Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-synapse-100 rounded-lg flex items-center justify-center">
              <ServerIcon className="w-6 h-6 text-synapse-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Federated Indexing</h3>
          </div>
          <p className="text-gray-600 text-sm">
            See how Synapse creates secure, privacy-preserving indexes across 
            organizational silos without centralizing sensitive data.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-privacy-100 rounded-lg flex items-center justify-center">
              <ShieldCheckIcon className="w-6 h-6 text-privacy-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Privacy Protection</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Experience differential privacy in action with formal privacy guarantees 
            and permission-aware access controls.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Knowledge Synthesis</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Watch AI-powered synthesis combine insights from multiple sources 
            while maintaining clear attribution and provenance.
          </p>
        </div>
      </div>
    </div>
  );
}