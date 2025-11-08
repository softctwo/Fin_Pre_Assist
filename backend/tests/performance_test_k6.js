// k6 Performance Test Script
// Run with: k6 run tests/performance_test_k6.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '5m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 50 },  // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95% of requests should be below 2s
    http_req_failed: ['rate<0.01'],      // Error rate should be less than 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = 'http://localhost:8000';

// Helper function to get auth token
function getAuthToken() {
  const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, {
    username: 'testuser',
    password: 'Test123456!',
  });

  if (loginRes.status === 200) {
    return loginRes.json().access_token;
  }
  return null;
}

export default function () {
  // Get auth token
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  group('Health Check', function () {
    const res = http.get(`${BASE_URL}/api/v1/health/`);
    const result = check(res, {
      'health check status is 200': (r) => r.status === 200,
    });
    errorRate.add(!result);
    sleep(1);
  });

  group('Proposal Operations', function () {
    // List proposals
    const listRes = http.get(`${BASE_URL}/api/v1/proposals/`, { headers });
    check(listRes, {
      'list proposals status is 200': (r) => r.status === 200,
    });

    // Create proposal
    const createRes = http.post(
      `${BASE_URL}/api/v1/proposals/`,
      JSON.stringify({
        title: 'Performance Test Proposal',
        customer_name: 'Perf Test Customer',
        requirements: '测试性能',
        industry: '金融',
      }),
      { headers }
    );

    check(createRes, {
      'create proposal status is 201': (r) => r.status === 201,
    });

    if (createRes.status === 201) {
      const proposalId = createRes.json().id;

      // Get proposal detail
      const detailRes = http.get(`${BASE_URL}/api/v1/proposals/${proposalId}`, { headers });
      check(detailRes, {
        'get proposal status is 200': (r) => r.status === 200,
      });
    }

    sleep(1);
  });

  group('Document Search', function () {
    const searchRes = http.post(
      `${BASE_URL}/api/v1/search/documents`,
      JSON.stringify({
        query: '金融系统',
        limit: 10,
      }),
      { headers }
    );

    check(searchRes, {
      'search documents status is 200': (r) => r.status === 200,
      'search returns results': (r) => r.json() && r.json().results,
    });
    sleep(1);
  });

  group('Knowledge Base', function () {
    // Search knowledge
    const searchRes = http.post(
      `${BASE_URL}/api/v1/search/knowledge`,
      JSON.stringify({
        query: '金融科技',
        limit: 5,
        category: '技术',
      }),
      { headers }
    );

    check(searchRes, {
      'search knowledge status is 200': (r) => r.status === 200,
    });
    sleep(1);
  });
}

export function handleSummary(data) {
  return {
    'performance_report.html': generateHTMLReport(data),
    'performance_report.json': JSON.stringify(data, null, 2),
  };
}

function generateHTMLReport(data) {
  const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Performance Test Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .metric { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
    .pass { color: green; }
    .fail { color: red; }
  </style>
</head>
<body>
  <h1>Performance Test Report</h1>
  <p>Generated: ${new Date().toISOString()}</p>

  <h2>Summary</h2>
  <div class="metric">
    <strong>VUs:</strong> ${data.metrics.vus?.values?.max || 'N/A'}<br>
    <strong>Iterations:</strong> ${data.metrics.iterations?.values?.count || 'N/A'}<br>
    <strong>Duration:</strong> ${(data.state.duration / 1000000000).toFixed(2)}s
  </div>

  <h2>HTTP Request Duration</h2>
  <div class="metric">
    <strong>Average:</strong> ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)}ms<br>
    <strong>95th percentile:</strong> ${data.metrics.http_req_duration?.values['p(95)']?.toFixed(2)}ms<br>
    <strong>99th percentile:</strong> ${data.metrics.http_req_duration?.values['p(99)']?.toFixed(2)}ms
  </div>

  <h2>Error Rate</h2>
  <div class="metric">
    <strong>Total Errors:</strong> ${data.metrics.http_req_failed?.values?.count || 0}<br>
    <strong>Error Rate:</strong> ${((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%
  </div>
</body>
</html>
`;
  return html;
}
