import React, { useState } from 'react';
import { 
  BookOpenIcon, 
  CodeBracketIcon,
  ShieldCheckIcon,
  ServerIcon,
  CogIcon,
  RocketLaunchIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const sections = [
  {
    id: 'overview',
    title: 'Overview',
    icon: BookOpenIcon,
    content: {
      title: 'Project Synapse Overview',
      description: 'Cross-Silo Enterprise Knowledge Fabric',
      sections: [
        {
          title: 'What is Project Synapse?',
          content: `Project Synapse is a privacy-preserving, federated knowledge fabric that enables secure information retrieval across organizational boundaries without violating access controls or creating central data lakes.

**Key Benefits:**
• Reduces information search time by 30-40%
• Enables cross-team knowledge sharing
• Maintains strict privacy and security controls
• Provides formal differential privacy guarantees
• Scales to enterprise-level deployments`
        },
        {
          title: 'Architecture Overview',
          content: `Synapse implements a three-layer architecture:

**Layer 1: Federated Indexing**
- Secure cross-silo indexing with privacy-preserving hashes
- Local vector embeddings with differential privacy noise
- No raw data leaves source silos

**Layer 2: Privacy-Aware Query Routing**
- Permission-aware query routing across silos
- Multi-level access control enforcement
- Privacy budget management and tracking

**Layer 3: Knowledge Synthesis**
- AI-powered synthesis from multiple sources
- Source attribution and provenance tracking
- Confidence scoring and limitation identification`
        }
      ]
    }
  },
  {
    id: 'quickstart',
    title: 'Quick Start',
    icon: RocketLaunchIcon,
    content: {
      title: 'Getting Started',
      description: 'Set up and run Synapse in minutes',
      sections: [
        {
          title: 'Installation',
          content: `**Prerequisites:**
• Python 3.8+
• Docker and Docker Compose
• Git

**Setup Steps:**`,
          code: `# Clone the repository
git clone https://github.com/synapse-ai/project-synapse.git
cd project-synapse

# Install dependencies
pip install -r requirements.txt

# Initialize configuration
python -m synapse.cli init --config-path config/dev.yaml

# Start services
docker-compose up -d

# Start the indexer
python -m synapse.cli indexer start

# Start the API server
python -m synapse.cli server start`
        },
        {
          title: 'First Query',
          content: 'Execute your first federated query:',
          code: `# Using CLI
synapse query search "API authentication best practices" \\
  --user-id john.doe \\
  --org-id acme_corp \\
  --team-ids engineering \\
  --access-levels internal

# Using Python API
from synapse import PrivacyAwareQueryEngine, UserContext, QueryRequest

user_context = UserContext(
    user_id="john.doe",
    organization_id="acme_corp",
    team_ids=["engineering"],
    access_levels=["internal"]
)

query_request = QueryRequest(
    query="API authentication best practices",
    user_context=user_context,
    max_results=10
)

results = await query_engine.route_query(query_request)`
        }
      ]
    }
  },
  {
    id: 'api',
    title: 'API Reference',
    icon: CodeBracketIcon,
    content: {
      title: 'API Reference',
      description: 'Complete REST API documentation',
      sections: [
        {
          title: 'Query Endpoints',
          content: 'Execute federated queries across silos:',
          code: `# POST /api/v1/query
{
  "query": "How to implement OAuth2?",
  "user_context": {
    "user_id": "john.doe",
    "organization_id": "acme_corp",
    "team_ids": ["engineering"],
    "access_levels": ["internal"]
  },
  "max_results": 10,
  "privacy_budget": 0.1
}

# Response
{
  "results": [
    {
      "id": "result_1",
      "title": "OAuth2 Implementation Guide",
      "content": "Comprehensive guide...",
      "source_attribution": {
        "silo": "Engineering Docs",
        "team": "Security Team"
      },
      "relevance_score": 0.95,
      "access_level": "internal"
    }
  ],
  "total_results": 8,
  "query_time_ms": 245,
  "privacy_budget_used": 0.1
}`
        },
        {
          title: 'Synthesis Endpoints',
          content: 'Synthesize knowledge from multiple sources:',
          code: `# POST /api/v1/synthesize
{
  "query": "OAuth2 implementation best practices",
  "user_context": { ... },
  "result_ids": ["result_1", "result_2", "result_3"]
}

# Response
{
  "synthesis_id": "synth_123",
  "query": "OAuth2 implementation best practices",
  "synthesized_answer": "Based on multiple sources...",
  "confidence_score": 0.89,
  "source_results": [...],
  "limitations": [
    "Some security docs were restricted"
  ]
}`
        }
      ]
    }
  },
  {
    id: 'security',
    title: 'Security & Privacy',
    icon: ShieldCheckIcon,
    content: {
      title: 'Security & Privacy',
      description: 'Privacy-preserving architecture and compliance',
      sections: [
        {
          title: 'Differential Privacy',
          content: `Synapse implements formal differential privacy guarantees:

**Privacy Budget Management:**
• Global privacy budget allocation
• Per-query budget consumption tracking
• Automatic noise calibration

**Noise Mechanisms:**
• Gaussian noise for embeddings
• Laplace noise for scores and counts
• Exponential mechanism for top-k selection`,
          code: `# Privacy configuration
privacy:
  global_budget: 10.0
  default_query_budget: 0.1
  
# Noise injection example
noisy_embeddings = privacy_manager.add_noise_to_embeddings(
    embeddings, 
    privacy_budget=0.1,
    sensitivity=1.0
)`
        },
        {
          title: 'Access Control',
          content: `Multi-layered access control system:

**Organizational Boundaries:**
• Cross-org access requires special permissions
• Team-level access controls
• Role-based permissions

**Data Classification:**
• Public → Internal → Confidential → Restricted
• Hierarchical access levels
• Temporal access constraints`,
          code: `# Access control configuration
access_rules:
  organizational_boundaries: true
  data_classification: "confidential"
  allowed_teams: ["engineering", "security"]
  temporal_constraints:
    business_hours_only: true
    max_data_age_days: 30`
        }
      ]
    }
  },
  {
    id: 'deployment',
    title: 'Deployment',
    icon: ServerIcon,
    content: {
      title: 'Deployment Guide',
      description: 'Production deployment configurations',
      sections: [
        {
          title: 'Docker Deployment',
          content: 'Deploy using Docker Compose:',
          code: `# docker-compose.yml
version: '3.8'
services:
  synapse-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SYNAPSE_CONFIG=/app/config/production.yaml
    depends_on:
      - redis
      - elasticsearch
      - postgres

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

# Deploy
docker-compose up -d`
        },
        {
          title: 'Kubernetes Deployment',
          content: 'Deploy to Kubernetes cluster:',
          code: `# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n synapse

# Scale deployment
kubectl scale deployment synapse-api --replicas=5 -n synapse

# Monitor logs
kubectl logs -f deployment/synapse-api -n synapse`
        }
      ]
    }
  },
  {
    id: 'configuration',
    title: 'Configuration',
    icon: CogIcon,
    content: {
      title: 'Configuration Guide',
      description: 'System configuration and customization',
      sections: [
        {
          title: 'Basic Configuration',
          content: 'Core system configuration:',
          code: `# config/production.yaml
synapse:
  privacy:
    global_budget: 50.0
    default_query_budget: 0.1
    
  indexing:
    embedding_model: "all-MiniLM-L6-v2"
    batch_size: 1000
    update_interval: 1800
    
  security:
    encryption_enabled: true
    key_rotation_interval: 43200
    
  api:
    host: "0.0.0.0"
    port: 8080
    cors_origins: ["https://yourdomain.com"]`
        },
        {
          title: 'Silo Configuration',
          content: 'Configure organizational silos:',
          code: `# Silo configuration
silos:
  engineering_docs:
    name: "Engineering Documentation"
    type: "documentation"
    organization_id: "acme_corp"
    team_id: "engineering"
    data_classification: "internal"
    access_rules:
      public_within_org: true
      allowed_teams: ["engineering", "devops"]
      
  security_kb:
    name: "Security Knowledge Base"
    type: "knowledge_base"
    organization_id: "acme_corp"
    team_id: "security"
    data_classification: "restricted"
    access_rules:
      allowed_teams: ["security"]
      min_security_clearance: "confidential"`
        }
      ]
    }
  }
];

export default function Documentation() {
  const [activeSection, setActiveSection] = useState('overview');

  const currentSection = sections.find(s => s.id === activeSection);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:w-64 flex-shrink-0">
          <div className="sticky top-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentation</h2>
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors duration-200 ${
                      activeSection === section.id
                        ? 'bg-synapse-100 text-synapse-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{section.title}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 min-w-0">
          {currentSection && (
            <div>
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {currentSection.content.title}
                </h1>
                <p className="text-lg text-gray-600">
                  {currentSection.content.description}
                </p>
              </div>

              {/* Content Sections */}
              <div className="space-y-8">
                {currentSection.content.sections.map((section, index) => (
                  <div key={index} className="card">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">
                      {section.title}
                    </h2>
                    
                    {section.content && (
                      <div className="prose max-w-none mb-6">
                        {section.content.split('\n').map((paragraph, pIndex) => {
                          if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
                            return (
                              <h3 key={pIndex} className="text-lg font-semibold text-gray-800 mt-4 mb-2">
                                {paragraph.slice(2, -2)}
                              </h3>
                            );
                          } else if (paragraph.startsWith('•')) {
                            return (
                              <li key={pIndex} className="text-gray-700 ml-4">
                                {paragraph.slice(2)}
                              </li>
                            );
                          } else if (paragraph.trim()) {
                            return (
                              <p key={pIndex} className="text-gray-700 mb-3 leading-relaxed">
                                {paragraph}
                              </p>
                            );
                          }
                          return null;
                        })}
                      </div>
                    )}

                    {section.code && (
                      <div className="mt-4">
                        <SyntaxHighlighter
                          language="bash"
                          style={tomorrow}
                          className="rounded-lg"
                          customStyle={{
                            margin: 0,
                            fontSize: '14px'
                          }}
                        >
                          {section.code}
                        </SyntaxHighlighter>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between mt-12 pt-8 border-t border-gray-200">
                <div>
                  {sections.findIndex(s => s.id === activeSection) > 0 && (
                    <button
                      onClick={() => {
                        const currentIndex = sections.findIndex(s => s.id === activeSection);
                        setActiveSection(sections[currentIndex - 1].id);
                      }}
                      className="flex items-center space-x-2 text-synapse-600 hover:text-synapse-700"
                    >
                      <ChevronRightIcon className="w-4 h-4 rotate-180" />
                      <span>Previous</span>
                    </button>
                  )}
                </div>
                <div>
                  {sections.findIndex(s => s.id === activeSection) < sections.length - 1 && (
                    <button
                      onClick={() => {
                        const currentIndex = sections.findIndex(s => s.id === activeSection);
                        setActiveSection(sections[currentIndex + 1].id);
                      }}
                      className="flex items-center space-x-2 text-synapse-600 hover:text-synapse-700"
                    >
                      <span>Next</span>
                      <ChevronRightIcon className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}