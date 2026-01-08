// Mock API service for demo purposes
// In production, this would connect to the actual Synapse backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Mock data for demo
const mockData = {
  stats: {
    totalSilos: 47,
    totalDocuments: 125000,
    queriesThisWeek: 2847,
    privacyBudgetUsed: 23.5,
    avgResponseTime: 245,
    activeUsers: 156
  },
  
  queryResults: [
    {
      id: 1,
      title: "OAuth2 Implementation Guide",
      content: "Comprehensive guide for implementing OAuth2 authentication in microservices architecture. Covers token validation, refresh mechanisms, and security best practices...",
      source: "Engineering Documentation",
      silo: "AWS Engineering Team",
      relevance: 0.95,
      accessLevel: "Internal",
      timestamp: "2024-01-08T10:30:00Z"
    },
    {
      id: 2,
      title: "Microservices Security Patterns",
      content: "Security patterns and practices for microservices including authentication, authorization, and inter-service communication security...",
      source: "Security Knowledge Base", 
      silo: "Security Team",
      relevance: 0.87,
      accessLevel: "Confidential",
      timestamp: "2024-01-07T15:45:00Z"
    }
  ],

  synthesis: {
    answer: `Based on the available sources, here's a comprehensive approach to implementing OAuth2 in microservices:

**[Source: Engineering Team]** The recommended implementation follows a centralized authentication pattern with JWT tokens for stateless authentication across services.

**[Source: Security Team]** Key security considerations include proper token validation, secure token storage, and implementing refresh token rotation to prevent token theft.

**[Source: Platform Team]** The API gateway should handle initial authentication and token validation, then pass validated user context to downstream services.

The synthesis shows consistency across teams regarding JWT-based authentication, with each team contributing specialized knowledge in their domain.`,
    confidence: 0.89,
    sources: 3,
    limitations: [
      "Some highly classified security documentation was not accessible",
      "Recent updates from the DevOps team may not be included"
    ]
  }
};

class ApiService {
  constructor() {
    this.isDemo = true; // Set to false when backend is available
  }

  async checkHealth() {
    if (this.isDemo) {
      return { status: 'healthy', service: 'synapse-demo' };
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.warn('Backend not available, using demo mode');
      this.isDemo = true;
      return { status: 'demo', service: 'synapse-demo' };
    }
  }

  async getStats() {
    if (this.isDemo) {
      return mockData.stats;
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/stats`);
    return await response.json();
  }

  async executeQuery(queryRequest) {
    if (this.isDemo) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      return {
        results: mockData.queryResults,
        total_results: mockData.queryResults.length,
        query_time_ms: 245,
        privacy_budget_used: queryRequest.privacy_budget || 0.1
      };
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(queryRequest)
    });
    
    return await response.json();
  }

  async synthesizeKnowledge(synthesisRequest) {
    if (this.isDemo) {
      // Simulate synthesis delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return {
        ...mockData.synthesis,
        query: synthesisRequest.query,
        synthesis_id: `synth_${Date.now()}`
      };
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(synthesisRequest)
    });
    
    return await response.json();
  }

  async getSilos() {
    if (this.isDemo) {
      return [
        {
          id: 'eng-docs',
          name: 'Engineering Documentation',
          type: 'documentation',
          organization: 'ACME Corp',
          team: 'Engineering',
          status: 'healthy',
          documents: 1250,
          lastIndexed: '2024-01-09T08:30:00Z',
          accessLevel: 'Internal'
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
          accessLevel: 'Confidential'
        }
      ];
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/silos`);
    return await response.json();
  }

  async getPrivacyReport() {
    if (this.isDemo) {
      return {
        global_budget: 50.0,
        used_budget: 12.3,
        remaining_budget: 37.7,
        usage_percentage: 24.6,
        mechanism_usage: {
          gaussian_noise: { count: 15, total_budget: 5.2 },
          laplace_noise: { count: 8, total_budget: 3.1 }
        }
      };
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/privacy/report`);
    return await response.json();
  }
}

const apiService = new ApiService();
export default apiService;