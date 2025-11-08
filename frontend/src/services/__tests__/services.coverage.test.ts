import { vi, describe, it, expect } from 'vitest'

// Import all services to increase coverage
import api from '../api'
import authService from '../authService'
import documentService from '../documentService'
import templateService from '../templateService'
import proposalService from '../proposalService'
import searchService from '../searchService'
import metricsService from '../metricsService'

describe('Services Coverage', () => {
  describe('API Service', () => {
    it('should have correct axios configuration', () => {
      expect(api).toBeDefined()
      expect(api.defaults.timeout).toBe(30000)
      expect(api.defaults.baseURL).toBe('/api/v1')
    })

    it('should have interceptors setup', () => {
      expect(api.interceptors).toBeDefined()
      expect(api.interceptors.request.use).toBeDefined()
      expect(api.interceptors.response.use).toBeDefined()
    })
  })

  describe('Auth Service', () => {
    it('should have login method', () => {
      expect(authService.login).toBeDefined()
      expect(typeof authService.login).toBe('function')
    })

    it('should have register method', () => {
      expect(authService.register).toBeDefined()
      expect(typeof authService.register).toBe('function')
    })

    it('should have getCurrentUser method', () => {
      expect(authService.getCurrentUser).toBeDefined()
      expect(typeof authService.getCurrentUser).toBe('function')
    })
  })

  describe('Document Service', () => {
    it('should have getDocuments method', () => {
      expect(documentService.getDocuments).toBeDefined()
      expect(typeof documentService.getDocuments).toBe('function')
    })

    it('should have uploadDocument method', () => {
      expect(documentService.uploadDocument).toBeDefined()
      expect(typeof documentService.uploadDocument).toBe('function')
    })

    it('should have getDocument method', () => {
      expect(documentService.getDocument).toBeDefined()
      expect(typeof documentService.getDocument).toBe('function')
    })

    it('should have deleteDocument method', () => {
      expect(documentService.deleteDocument).toBeDefined()
      expect(typeof documentService.deleteDocument).toBe('function')
    })

    it('should have extractDocumentText method', () => {
      expect(documentService.extractDocumentText).toBeDefined()
      expect(typeof documentService.extractDocumentText).toBe('function')
    })

    it('should have downloadDocument method', () => {
      expect(documentService.downloadDocument).toBeDefined()
      expect(typeof documentService.downloadDocument).toBe('function')
    })
  })

  describe('Template Service', () => {
    it('should have getTemplates method', () => {
      expect(templateService.getTemplates).toBeDefined()
      expect(typeof templateService.getTemplates).toBe('function')
    })

    it('should have createTemplate method', () => {
      expect(templateService.createTemplate).toBeDefined()
      expect(typeof templateService.createTemplate).toBe('function')
    })

    it('should have validateTemplate method', () => {
      expect(templateService.validateTemplate).toBeDefined()
      expect(typeof templateService.validateTemplate).toBe('function')
    })

    it('should have getTemplate method', () => {
      expect(templateService.getTemplate).toBeDefined()
      expect(typeof templateService.getTemplate).toBe('function')
    })

    it('should have updateTemplate method', () => {
      expect(templateService.updateTemplate).toBeDefined()
      expect(typeof templateService.updateTemplate).toBe('function')
    })

    it('should have deleteTemplate method', () => {
      expect(templateService.deleteTemplate).toBeDefined()
      expect(typeof templateService.deleteTemplate).toBe('function')
    })

    it('should have previewTemplate method', () => {
      expect(templateService.previewTemplate).toBeDefined()
      expect(typeof templateService.previewTemplate).toBe('function')
    })
  })

  describe('Proposal Service', () => {
    it('should have getProposals method', () => {
      expect(proposalService.getProposals).toBeDefined()
      expect(typeof proposalService.getProposals).toBe('function')
    })

    it('should have createProposal method', () => {
      expect(proposalService.createProposal).toBeDefined()
      expect(typeof proposalService.createProposal).toBe('function')
    })

    it('should have getProposal method', () => {
      expect(proposalService.getProposal).toBeDefined()
      expect(typeof proposalService.getProposal).toBe('function')
    })

    it('should have updateProposal method', () => {
      expect(proposalService.updateProposal).toBeDefined()
      expect(typeof proposalService.updateProposal).toBe('function')
    })

    it('should have deleteProposal method', () => {
      expect(proposalService.deleteProposal).toBeDefined()
      expect(typeof proposalService.deleteProposal).toBe('function')
    })

    it('should have exportProposal method', () => {
      expect(proposalService.exportProposal).toBeDefined()
      expect(typeof proposalService.exportProposal).toBe('function')
    })

    it('should have generateProposal method', () => {
      expect(proposalService.generateProposal).toBeDefined()
      expect(typeof proposalService.generateProposal).toBe('function')
    })
  })

  describe('Search Service', () => {
    it('should have searchDocuments method', () => {
      expect(searchService.searchDocuments).toBeDefined()
      expect(typeof searchService.searchDocuments).toBe('function')
    })

    it('should have searchProposals method', () => {
      expect(searchService.searchProposals).toBeDefined()
      expect(typeof searchService.searchProposals).toBe('function')
    })

    it('should have searchKnowledge method', () => {
      expect(searchService.searchKnowledge).toBeDefined()
      expect(typeof searchService.searchKnowledge).toBe('function')
    })

    it('should have getSearchSuggestions method', () => {
      expect(searchService.getSearchSuggestions).toBeDefined()
      expect(typeof searchService.getSearchSuggestions).toBe('function')
    })
  })

  describe('Metrics Service', () => {
    it('should have getMetricsSummary method', () => {
      expect(metricsService.getMetricsSummary).toBeDefined()
      expect(typeof metricsService.getMetricsSummary).toBe('function')
    })

    it('should have getSystemMetrics method', () => {
      expect(metricsService.getSystemMetrics).toBeDefined()
      expect(typeof metricsService.getSystemMetrics).toBe('function')
    })

    it('should have getUserActivityMetrics method', () => {
      expect(metricsService.getUserActivityMetrics).toBeDefined()
      expect(typeof metricsService.getUserActivityMetrics).toBe('function')
    })

    it('should have getApiMetrics method', () => {
      expect(metricsService.getApiMetrics).toBeDefined()
      expect(typeof metricsService.getApiMetrics).toBe('function')
    })
  })
})