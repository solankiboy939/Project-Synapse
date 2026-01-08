import React, { useState, useRef } from 'react';
import { 
  MagnifyingGlassIcon, 
  SparklesIcon, 
  ClockIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  ServerIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import apiService from '../services/api';

const mockSuggestions = [
  "How to implement OAuth2 in microservices?",
  "Database migration best practices",
  "Container security scanning tools", 
  "API rate limiting strategies",
  "Kubernetes deployment patterns",
  "React performance optimization techniques",
  "Machine learning model deployment",
  "Distributed system monitoring"
];

export default function QueryInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [synthesis, setSynthesis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1);
  const inputRef = useRef(null);

  const filteredSuggestions = mockSuggestions.filter(suggestion =>
    suggestion.toLowerCase().includes(query.toLowerCase()) && query.length > 0
  );

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResults([]);
    setSynthesis(null);
    setShowSuggestions(false);

    try {
      const queryRequest = {
        query: query,
        user_context: {
          user_id: "demo.user@company.com",
          organization_id: "demo_org",
          team_ids: ["engineering"],
          access_levels: ["internal"]
        },
        max_results: 10,
        privacy_budget: 0.1
      };

      const response = await apiService.executeQuery(queryRequest);
      setResults(response.results || []);
      setLoading(false);
      
      if (response.results && response.results.length > 0) {
        toast.success(`Found ${response.results.length} results across multiple silos`);
      } else {
        toast.error('No results found');
      }
    } catch (error) {
      console.error('Query failed:', error);
      setLoading(false);
      toast.error('Query failed. Please try again.');
    }
  };

  const handleSynthesize = async () => {
    if (results.length === 0) return;

    setSynthesizing(true);
    
    try {
      const synthesisRequest = {
        query: query,
        user_context: {
          user_id: "demo.user@company.com",
          organization_id: "demo_org",
          team_ids: ["engineering"],
          access_levels: ["internal"]
        },
        result_ids: results.map(r => r.id)
      };

      const synthesis = await apiService.synthesizeKnowledge(synthesisRequest);
      setSynthesis(synthesis);
      setSynthesizing(false);
      toast.success('Knowledge synthesis completed');
    } catch (error) {
      console.error('Synthesis failed:', error);
      setSynthesizing(false);
      toast.error('Synthesis failed. Please try again.');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (selectedSuggestion >= 0 && filteredSuggestions.length > 0) {
        setQuery(filteredSuggestions[selectedSuggestion]);
        setShowSuggestions(false);
        setSelectedSuggestion(-1);
      } else {
        handleSearch();
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedSuggestion(prev => 
        prev < filteredSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedSuggestion(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedSuggestion(-1);
    }
  };

  const getAccessLevelColor = (level) => {
    switch (level) {
      case 'Public': return 'bg-green-100 text-green-800';
      case 'Internal': return 'bg-blue-100 text-blue-800';
      case 'Confidential': return 'bg-yellow-100 text-yellow-800';
      case 'Restricted': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Federated Knowledge Search
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Search across all organizational silos with privacy-preserving, 
          permission-aware federated retrieval
        </p>
      </div>

      {/* Search Interface */}
      <div className="relative mb-8">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(e.target.value.length > 0);
              setSelectedSuggestion(-1);
            }}
            onKeyDown={handleKeyPress}
            onFocus={() => setShowSuggestions(query.length > 0)}
            className="block w-full pl-10 pr-12 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-synapse-500 focus:border-synapse-500"
            placeholder="Ask anything across your organization..."
          />
          <div className="absolute inset-y-0 right-0 flex items-center">
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="mr-3 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <ArrowPathIcon className="w-5 h-5 animate-spin" />
              ) : (
                'Search'
              )}
            </button>
          </div>
        </div>

        {/* Suggestions Dropdown */}
        <AnimatePresence>
          {showSuggestions && filteredSuggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              {filteredSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(suggestion);
                    setShowSuggestions(false);
                    setSelectedSuggestion(-1);
                  }}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                    selectedSuggestion === index ? 'bg-synapse-50' : ''
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <MagnifyingGlassIcon className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-700">{suggestion}</span>
                  </div>
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-flex items-center space-x-2">
            <ArrowPathIcon className="w-6 h-6 animate-spin text-synapse-600" />
            <span className="text-lg text-gray-600">
              Searching across silos<span className="loading-dots">...</span>
            </span>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            Checking permissions and applying privacy filters
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results ({results.length})
            </h2>
            <button
              onClick={handleSynthesize}
              disabled={synthesizing}
              className="btn-primary flex items-center space-x-2"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>{synthesizing ? 'Synthesizing...' : 'Synthesize Knowledge'}</span>
            </button>
          </div>

          <div className="space-y-6">
            {results.map((result, index) => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {result.title}
                  </h3>
                  <div className="flex items-center space-x-2">
                    <span className={`badge ${getAccessLevelColor(result.accessLevel)}`}>
                      {result.accessLevel}
                    </span>
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <span>{Math.round(result.relevance * 100)}%</span>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4 leading-relaxed">
                  {result.content}
                </p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <ServerIcon className="w-4 h-4" />
                      <span>{result.silo}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <DocumentTextIcon className="w-4 h-4" />
                      <span>{result.source}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ClockIcon className="w-4 h-4" />
                    <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Synthesis */}
      {synthesizing && (
        <div className="card mb-8">
          <div className="text-center py-8">
            <SparklesIcon className="w-8 h-8 animate-pulse text-privacy-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Synthesizing Knowledge
            </h3>
            <p className="text-gray-600">
              Combining insights from multiple sources while preserving privacy...
            </p>
          </div>
        </div>
      )}

      {synthesis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card privacy-gradient text-white"
        >
          <div className="flex items-center space-x-2 mb-4">
            <SparklesIcon className="w-6 h-6" />
            <h3 className="text-xl font-semibold">Knowledge Synthesis</h3>
          </div>
          
          <div className="prose prose-invert max-w-none mb-6">
            <div className="whitespace-pre-line text-gray-100 leading-relaxed">
              {synthesis.answer}
            </div>
          </div>
          
          <div className="border-t border-white/20 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{Math.round(synthesis.confidence * 100)}%</div>
                <div className="text-sm opacity-80">Confidence Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{synthesis.sources}</div>
                <div className="text-sm opacity-80">Sources Used</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  <ShieldCheckIcon className="w-6 h-6 mx-auto" />
                </div>
                <div className="text-sm opacity-80">Privacy Protected</div>
              </div>
            </div>
            
            {synthesis.limitations.length > 0 && (
              <div className="bg-white/10 rounded-lg p-4">
                <h4 className="font-semibold mb-2">Access Limitations:</h4>
                <ul className="text-sm space-y-1 opacity-90">
                  {synthesis.limitations.map((limitation, index) => (
                    <li key={index}>• {limitation}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!loading && results.length === 0 && query && (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">
            Try adjusting your search terms or check your access permissions
          </p>
        </div>
      )}
    </div>
  );
}