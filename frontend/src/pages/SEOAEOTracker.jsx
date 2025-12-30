import { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Search, 
  Users, 
  Globe, 
  Loader2, 
  RefreshCw, 
  Play,
  CheckCircle2,
  XCircle,
  ExternalLink,
  BarChart3,
  Target,
  AlertCircle
} from 'lucide-react'
import { api } from '../utils/api'

function SEOAEOTracker() {
  const [brandName, setBrandName] = useState('')
  const [brandUrl, setBrandUrl] = useState('')
  const [competitors, setCompetitors] = useState('')
  const [topics, setTopics] = useState('')
  const [numPrompts, setNumPrompts] = useState(100)
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all') // 'all', 'mentioned', 'not_mentioned'
  const [loadingContext, setLoadingContext] = useState(true)

  // Load brand context data on component mount
  useEffect(() => {
    loadBrandContext()
  }, [])

  const loadBrandContext = async () => {
    try {
      setLoadingContext(true)
      
      // Load competitors from localStorage (same as BrandContext component)
      const savedCompetitors = localStorage.getItem('videohook_competitors')
      if (savedCompetitors) {
        try {
          const competitorsList = JSON.parse(savedCompetitors)
          if (Array.isArray(competitorsList) && competitorsList.length > 0) {
            setCompetitors(competitorsList.join(', '))
          }
        } catch (e) {
          console.error('Error parsing competitors:', e)
        }
      }

      // Try to get brand name and URL from user context
      try {
        const contextResponse = await api.get('/api/user/context')
        const contextStr = contextResponse.data?.context || ''
        
        // Try to extract brand name and URL from context
        if (contextStr) {
          let context = contextStr
          // If it's a JSON string, parse it
          try {
            context = JSON.parse(contextStr)
            // Extract from parsed JSON if it's an object
            if (typeof context === 'object') {
              // Look for brand name in various fields
              const brandNameFields = [
                context?.preferences?.brand_voice,
                context?.brand_insights?.extracted_brand_voice,
                context?.social_profiles?.extracted_brand_elements?.brand_name
              ]
              for (const field of brandNameFields) {
                if (field && !brandName) {
                  setBrandName(String(field).trim())
                  break
                }
              }
              
              // Convert back to string for regex matching
              context = JSON.stringify(context)
            }
          } catch (e) {
            // Not JSON, use as string
          }
          
          // Look for common patterns like "company name is X" or "brand: X"
          const brandMatch = context.match(/(?:brand|company|organization|name)[\s:]+(?:is|:)?[\s]*([A-Z][A-Za-z0-9\s&]+)/i)
          if (brandMatch && !brandName) {
            setBrandName(brandMatch[1].trim())
          }

          // Look for URL patterns (with or without protocol)
          // First try with protocol
          let urlMatch = context.match(/(https?:\/\/[^\s\)\"]+)/i)
          if (!urlMatch) {
            // Then try without protocol (domain pattern)
            urlMatch = context.match(/([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.?[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\/[^\s\)\"]*)?)/i)
          }
          if (urlMatch && !brandUrl) {
            let url = urlMatch[1] || urlMatch[0]
            // Add protocol if missing
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
              url = 'https://' + url
            }
            setBrandUrl(url.trim())
          }
        }
      } catch (err) {
        console.log('Could not load user context, will use manual input')
      }

      // Try to extract brand info from brand context summary if available
      try {
        const brandSummary = localStorage.getItem('videohook_brand_context_summary')
        if (brandSummary && !brandName) {
          const summary = JSON.parse(brandSummary)
          // Try to extract brand name from summary
          const nameMatch = summary.match(/(?:brand|company|organization)[\s:]+(?:is|:)?[\s]*([A-Z][A-Za-z0-9\s&]+)/i)
          if (nameMatch) {
            setBrandName(nameMatch[1].trim())
          }
        }
      } catch (e) {
        console.log('Could not extract brand info from summary')
      }

    } catch (err) {
      console.error('Error loading brand context:', err)
    } finally {
      setLoadingContext(false)
    }
  }

  const handleRunAnalysis = async (e) => {
    e.preventDefault()
    if (!brandName.trim()) {
      setError('Please enter a brand name')
      return
    }

    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      const requestData = {
        brand_name: brandName.trim(),
        brand_url: brandUrl.trim() || undefined,
        competitors: competitors.split(',').map(c => c.trim()).filter(c => c),
        topics: topics.split(',').map(t => t.trim()).filter(t => t),
        num_prompts: numPrompts
      }

      console.log('[SEO/AEO] Starting analysis with data:', requestData)
      console.log('[SEO/AEO] Making API call to /api/seo-aeo/full-analysis')

      const response = await api.post('/api/seo-aeo/full-analysis', requestData, {
        timeout: 300000 // 5 minutes timeout for full analysis
      })

      console.log('[SEO/AEO] Analysis complete, received response:', response.data)
      setAnalysis(response.data)
    } catch (err) {
      console.error('[SEO/AEO] Error running analysis:', err)
      console.error('[SEO/AEO] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        code: err.code
      })
      
      let errorMessage = 'Failed to run analysis'
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. The analysis may take longer than expected.'
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000'
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    if (brandName) {
      handleRunAnalysis({ preventDefault: () => {} })
    }
  }

  const filteredResults = analysis?.recent_results?.filter(result => {
    if (filter === 'mentioned') return result.brand_mentioned
    if (filter === 'not_mentioned') return !result.brand_mentioned
    return true
  }) || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Brand Analytics</h1>
          <p className="text-gray-600">Track your brand mentions across AI responses</p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          {loadingContext && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <p className="text-sm text-blue-800">Loading brand context...</p>
            </div>
          )}
          {(brandName || brandUrl || competitors) && !loadingContext && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                ✓ Form auto-filled from Brand Context. You can edit any field as needed.
              </p>
              <p className="text-xs text-green-700 mt-1">
                To update your brand context, go to the <strong>Brand Context</strong> page.
              </p>
            </div>
          )}
          <form onSubmit={handleRunAnalysis} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter your brand name *
                </label>
                <input
                  type="text"
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  placeholder="e.g., Railway, Cursor, Vercel"
                  className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${brandName ? 'bg-gray-50' : ''}`}
                  required
                />
                {brandName && (
                  <p className="text-xs text-gray-500 mt-1">
                    {brandName.includes(' ') ? '✓ Auto-filled from Brand Context' : 'Enter your brand name'}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brand URL (auto-filled from Brand Context)
                </label>
                <input
                  type="url"
                  value={brandUrl}
                  onChange={(e) => {
                    let value = e.target.value.trim()
                    // Auto-add protocol if missing
                    if (value && !value.startsWith('http://') && !value.startsWith('https://') && value.includes('.')) {
                      value = 'https://' + value
                    }
                    setBrandUrl(value)
                  }}
                  placeholder="https://yourbrand.com"
                  className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${brandUrl ? 'bg-gray-50' : ''}`}
                />
                {brandUrl && (
                  <p className="text-xs text-gray-500 mt-1">
                    ✓ Auto-filled from Brand Context. Click to edit.
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Competitors {competitors && <span className="text-xs text-gray-500">(auto-filled from Brand Context)</span>}
                </label>
                <input
                  type="text"
                  value={competitors}
                  onChange={(e) => setCompetitors(e.target.value)}
                  placeholder="e.g., Kubernetes, Docker, AWS"
                  className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${competitors ? 'bg-gray-50' : ''}`}
                />
                {competitors && (
                  <p className="text-xs text-gray-500 mt-1">
                    ✓ Auto-filled from Brand Context
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topics (comma-separated, optional)
                </label>
                <input
                  type="text"
                  value={topics}
                  onChange={(e) => setTopics(e.target.value)}
                  placeholder="e.g., deployment, hosting, infrastructure"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Prompts to Test
                </label>
                <input
                  type="number"
                  value={numPrompts}
                  onChange={(e) => setNumPrompts(parseInt(e.target.value) || 100)}
                  min="10"
                  max="200"
                  className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={loadBrandContext}
                  disabled={loadingContext}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                  title="Reload brand context from Brand Context page"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingContext ? 'animate-spin' : ''}`} />
                  Reload Context
                </button>
                <button
                  type="button"
                  onClick={handleRefresh}
                  disabled={loading || !brandName}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  Refresh Analysis
                </button>
                <button
                  type="submit"
                  disabled={loading || !brandName}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Running Analysis...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Run Analysis
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <Loader2 className="w-12 h-12 animate-spin text-purple-600 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Analyzing brand mentions... This may take a few minutes.</p>
            <p className="text-sm text-gray-500">Testing prompts with ChatGPT and analyzing responses...</p>
            <p className="text-xs text-gray-400 mt-4">Check the browser console (F12) for detailed progress logs.</p>
          </div>
        )}

        {/* Results Dashboard */}
        {analysis && !loading && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Brand Mentions</h3>
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {analysis.brand_mention_rate}%
                </div>
                <p className="text-sm text-gray-500">
                  {analysis.total_mentions}/{analysis.total_prompts_tested} mention rate
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Total Prompts Tested</h3>
                  <Search className="w-5 h-5 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {analysis.total_prompts_tested}
                </div>
                <p className="text-sm text-gray-500">Analysis complete</p>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Top Competitor</h3>
                  <Users className="w-5 h-5 text-yellow-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {analysis.top_competitor || 'N/A'}
                </div>
                <p className="text-sm text-gray-500">
                  {analysis.top_competitor_rate ? `${analysis.top_competitor_rate}% mention rate` : 'No competitors'}
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">Sources Found</h3>
                  <Globe className="w-5 h-5 text-green-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {analysis.total_sources}
                </div>
                <p className="text-sm text-gray-500">Across {analysis.total_sources} domains</p>
              </div>
            </div>

            {/* Detailed Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Brand Mentions by Topic */}
              {analysis.topics && analysis.topics.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Brand Mentions by Topic</h3>
                    <BarChart3 className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="space-y-4">
                    {analysis.topics.slice(0, 5).map((topic, idx) => (
                      <div key={idx}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">{topic.topic}</span>
                          <span className="text-sm text-gray-600">{topic.mention_rate}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${topic.mention_rate}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Competitor Analysis */}
              {analysis.competitors && analysis.competitors.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Competitor Analysis</h3>
                    <Target className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="space-y-3">
                    {analysis.competitors.map((comp, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{comp.competitor}</p>
                          <p className="text-sm text-gray-500">{comp.mentions}/{comp.total_prompts} prompts</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">{comp.mention_rate}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Recent Prompt Results */}
            {analysis.recent_results && analysis.recent_results.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Prompt Results</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setFilter('all')}
                      className={`px-3 py-1 rounded text-sm ${
                        filter === 'all' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      All
                    </button>
                    <button
                      onClick={() => setFilter('mentioned')}
                      className={`px-3 py-1 rounded text-sm ${
                        filter === 'mentioned' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      Mentioned
                    </button>
                    <button
                      onClick={() => setFilter('not_mentioned')}
                      className={`px-3 py-1 rounded text-sm ${
                        filter === 'not_mentioned' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      Not Mentioned
                    </button>
                  </div>
                </div>
                <div className="space-y-4">
                  {filteredResults.slice(0, 10).map((result, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 mb-1">"{result.prompt}"</p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>{result.topic}</span>
                            <span>•</span>
                            <span>Sources: {result.sources?.length || 0}</span>
                            <span>•</span>
                            <span>Competitors: {result.competitors_mentioned?.length || 0}</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          {result.brand_mentioned ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-600" />
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">{result.response}</p>
                      {result.sources && result.sources.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {result.sources.slice(0, 3).map((source, sIdx) => (
                            <a
                              key={sIdx}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-purple-600 hover:underline flex items-center gap-1"
                            >
                              {source.domain}
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Sources */}
            {analysis.top_sources && analysis.top_sources.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Top Sources</h3>
                  <a href="#" className="text-sm text-purple-600 hover:underline">View All</a>
                </div>
                <div className="space-y-3">
                  {analysis.top_sources.slice(0, 10).map((source, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Globe className="w-4 h-4 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">{source.domain}</p>
                          <p className="text-xs text-gray-500">
                            {source.source_type || 'Website'} • {source.mention_count} mentions
                          </p>
                        </div>
                      </div>
                      <a
                        href={`https://${source.domain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:text-purple-700"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!analysis && !loading && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Start Your Brand Analysis</h3>
            <p className="text-gray-600 mb-6">
              Enter your brand name and run an analysis to see how your brand appears in AI responses.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SEOAEOTracker

