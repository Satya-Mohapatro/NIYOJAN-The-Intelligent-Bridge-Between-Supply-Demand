import React, { useState, useRef, useEffect } from 'react'
import { AlertTriangle, Send, ChevronDown, ChevronUp } from 'lucide-react'
import Layout from '../components/Layout'
import AgentResponseCard from '../components/AgentResponseCard'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000'

// ─── Types ────────────────────────────────────────────────────────────────────
interface ProductSummary {
  id: string
  name: string
  risk: string
  gap: number
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string | Record<string, unknown>
}

// ─── Query Groups ─────────────────────────────────────────────────────────────
const QUERY_GROUPS = [
  {
    label: 'ANALYSIS',
    borderColor: 'border-l-blue-500',
    hoverBg: 'hover:bg-blue-500/10',
    labelColor: 'text-blue-400',
    queries: [
      'Which products have the highest inventory risk right now?',
      'Show me the volatility ranking for all products',
      'What is the overall inventory gap across all SKUs?',
    ],
  },
  {
    label: 'SIMULATION',
    borderColor: 'border-l-purple-500',
    hoverBg: 'hover:bg-purple-500/10',
    labelColor: 'text-purple-400',
    queries: [
      'What if demand increases by 15% next month?',
      'What if demand drops by 20%? Which products will be overstocked?',
      'Simulate a 30% demand surge — which SKUs are critical?',
    ],
  },
  {
    label: 'STRATEGY',
    borderColor: 'border-l-green-500',
    hoverBg: 'hover:bg-green-500/10',
    labelColor: 'text-green-400',
    queries: [
      'What should I do for procurement next month?',
      'Give me a 4-week action plan based on current risk',
    ],
  },
]

// ─── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ risk }: { risk: string }) {
  if (risk === 'High')
    return <span className="text-xs font-semibold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">High</span>
  if (risk.includes('Overstock'))
    return <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">Overstock</span>
  return <span className="text-xs font-semibold px-2 py-0.5 rounded bg-green-500/20 text-green-400 border border-green-500/30">Low</span>
}

// ─── Loading Dots ────────────────────────────────────────────────────────────
function AnalyzingDots() {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="flex items-center gap-1">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-green-400"
            style={{ animation: `analyzeBounce 1.2s ease-in-out ${i * 0.18}s infinite` }}
          />
        ))}
      </div>
      <span className="text-sm text-gray-400">Analyzing your data...</span>
    </div>
  )
}

// ─── Upload Screen ────────────────────────────────────────────────────────────
function UploadScreen({
  csvFile, setCsvFile, pdfFile, setPdfFile,
  onUpload, isUploading, uploadError,
}: {
  csvFile: File | null
  setCsvFile: (f: File | null) => void
  pdfFile: File | null
  setPdfFile: (f: File | null) => void
  onUpload: () => void
  isUploading: boolean
  uploadError: string
}) {
  const [csvDrag, setCsvDrag] = useState(false)

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">AI Intelligence Hub</h1>
        <p className="text-gray-400 text-sm">
          Upload your Niyojan forecast CSV and ask any supply-chain planning question.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        {/* CSV Upload */}
        <div
          className={`rounded-xl border-2 border-dashed p-6 cursor-pointer transition-colors ${
            csvDrag
              ? 'border-green-400 bg-green-500/5'
              : csvFile
              ? 'border-green-600/60 bg-green-500/5'
              : 'border-gray-700 hover:border-gray-600'
          }`}
          onDragOver={e => { e.preventDefault(); setCsvDrag(true) }}
          onDragLeave={() => setCsvDrag(false)}
          onDrop={e => {
            e.preventDefault(); setCsvDrag(false)
            const f = e.dataTransfer.files[0]
            if (f?.name.endsWith('.csv')) setCsvFile(f)
          }}
          onClick={() => document.getElementById('csv-input')?.click()}
        >
          <input id="csv-input" type="file" accept=".csv" className="hidden"
            onChange={e => setCsvFile(e.target.files?.[0] || null)} />
          <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-3">Forecast CSV</p>
          <p className="text-white font-medium mb-1">Required</p>
          <p className="text-gray-500 text-xs mb-4">The NIYOJAN forecast output CSV with Week_N_Forecast columns</p>
          {csvFile ? (
            <div className="flex items-center gap-2 bg-green-500/10 border border-green-600/30 rounded-lg px-3 py-2">
              <div className="w-2 h-2 rounded-full bg-green-400 flex-shrink-0" />
              <span className="text-green-300 text-xs font-medium truncate">{csvFile.name}</span>
            </div>
          ) : (
            <div className="text-center text-gray-600 text-xs border border-dashed border-gray-700 rounded-lg py-3">
              Click or drag to upload
            </div>
          )}
        </div>

        {/* PDF Upload */}
        <div
          className={`rounded-xl border-2 border-dashed p-6 cursor-pointer transition-colors ${
            pdfFile ? 'border-blue-600/50 bg-blue-500/5' : 'border-gray-700 hover:border-gray-600'
          }`}
          onClick={() => document.getElementById('pdf-input')?.click()}
        >
          <input id="pdf-input" type="file" accept=".pdf" className="hidden"
            onChange={e => setPdfFile(e.target.files?.[0] || null)} />
          <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-3">Report PDF</p>
          <p className="text-white font-medium mb-1">Optional</p>
          <p className="text-gray-500 text-xs mb-4">Enables document-aware Q&A on the uploaded report</p>
          {pdfFile ? (
            <div className="flex items-center gap-2 bg-blue-500/10 border border-blue-600/30 rounded-lg px-3 py-2">
              <div className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0" />
              <span className="text-blue-300 text-xs font-medium truncate">{pdfFile.name}</span>
            </div>
          ) : (
            <div className="text-center text-gray-600 text-xs border border-dashed border-gray-700 rounded-lg py-3">
              Click to upload (optional)
            </div>
          )}
        </div>
      </div>

      {uploadError && (
        <div className="mb-4 flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
          <AlertTriangle size={14} className="flex-shrink-0" />
          {uploadError}
        </div>
      )}

      <button
        onClick={onUpload}
        disabled={!csvFile || isUploading}
        className={`w-full py-3.5 rounded-xl font-semibold text-sm transition-all ${
          csvFile && !isUploading
            ? 'bg-green-600 hover:bg-green-500 text-white'
            : 'bg-gray-800 text-gray-600 cursor-not-allowed'
        }`}
      >
        {isUploading ? 'Processing CSV and building index...' : 'Start AI Hub Session'}
      </button>
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function AgenticHub() {
  const token = localStorage.getItem('token')

  useEffect(() => {
    if (!token) window.location.href = '/login'
  }, [token])

  const [sessionId, setSessionId] = useState<string | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [products, setProducts] = useState<ProductSummary[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [query, setQuery] = useState('')
  const [uploadError, setUploadError] = useState('')
  const [showAllProducts, setShowAllProducts] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  const chatEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    return () => {
      if (sessionId) {
        fetch(`${API_BASE}/intelligence/session/${sessionId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => {})
      }
    }
  }, [sessionId])

  // ── Upload ──────────────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!csvFile) return
    setIsUploading(true)
    setUploadError('')
    try {
      const formData = new FormData()
      formData.append('forecast_csv', csvFile)
      if (pdfFile) formData.append('report_pdf', pdfFile)

      const res = await fetch(`${API_BASE}/intelligence/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const data = await res.json()
      setSessionId(data.session_id)
      setProducts(data.products || [])
      setWarnings(data.warnings || [])
    } catch (e: any) {
      setUploadError(e.message || 'Upload failed. Check your CSV format.')
    } finally {
      setIsUploading(false)
    }
  }

  // ── Send Query ──────────────────────────────────────────────────────────────
  const handleSend = async (queryText?: string) => {
    const q = (queryText ?? query).trim()
    if (!q || !sessionId || isLoading) return
    setQuery('')

    setMessages(prev => [...prev, { role: 'user', content: q }])
    setIsLoading(true)
    setMobileSidebarOpen(false)

    try {
      const res = await fetch(`${API_BASE}/intelligence/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ session_id: sessionId, query: q }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Query failed')
      }
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data }])
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: {
            executive_summary: `Error: ${e.message}`,
            high_risk_products: [], key_risk_drivers: [],
            recommended_actions: [], four_week_plan: {},
            monitoring_strategy: '', intent: 'error',
            query: q, generated_at: new Date().toISOString(),
          } as Record<string, unknown>,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleChipClick = (chipText: string) => {
    setQuery(chipText)
    handleSend(chipText)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewSession = () => {
    setSessionId(null)
    setProducts([])
    setWarnings([])
    setMessages([])
    setCsvFile(null)
    setPdfFile(null)
  }

  const visibleProducts = showAllProducts ? products : products.slice(0, 5)

  // ── Upload Screen ───────────────────────────────────────────────────────────
  if (!sessionId) {
    return (
      <Layout>
        <UploadScreen
          csvFile={csvFile} setCsvFile={setCsvFile}
          pdfFile={pdfFile} setPdfFile={setPdfFile}
          onUpload={handleUpload}
          isUploading={isUploading}
          uploadError={uploadError}
        />
        <style>{`
          @keyframes analyzeBounce {
            0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
            40% { transform: translateY(-5px); opacity: 1; }
          }
        `}</style>
      </Layout>
    )
  }

  // ── Chat Screen — Two-column layout ────────────────────────────────────────
  return (
    <Layout>
      {/* Mobile sidebar toggle */}
      <div className="md:hidden flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <span className="text-sm font-semibold text-white">AI Intelligence Hub</span>
        <button
          onClick={() => setMobileSidebarOpen(v => !v)}
          className="text-xs text-gray-400 border border-gray-700 rounded px-2 py-1"
        >
          {mobileSidebarOpen ? 'Hide panel' : 'Queries & Products'}
        </button>
      </div>

      <div className="flex h-[calc(100vh-130px)]">
        {/* ── LEFT PANEL ──────────────────────────────────────────────────── */}
        <aside
          className={`
            flex-shrink-0 w-[280px] border-r border-gray-800 flex flex-col overflow-y-auto
            bg-[#0d140d]
            ${mobileSidebarOpen ? 'block absolute z-10 h-full' : 'hidden md:flex'}
          `}
        >
          <div className="p-4 space-y-5 flex-1">
            {/* Section 1: Session Status */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400" />
                </span>
                <span className="text-xs font-semibold tracking-widest uppercase text-green-400">Session Active</span>
              </div>
              <p className="text-xs text-gray-500 pl-4">{products.length} products loaded</p>
              {warnings.length > 0 && (
                <div className="mt-2 flex items-start gap-1.5 pl-4">
                  <AlertTriangle size={12} className="text-amber-400 mt-0.5 flex-shrink-0" />
                  <span className="text-xs text-amber-400/80">Stock values estimated</span>
                </div>
              )}
            </div>

            <div className="border-t border-gray-800" />

            {/* Section 2: Products */}
            <div>
              <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-2">Loaded Products</p>
              <div className="space-y-1.5">
                {visibleProducts.map(p => (
                  <div key={p.id} className="flex items-center justify-between gap-2">
                    <span className="text-xs text-gray-300 truncate">{p.name !== p.id ? p.name : p.id}</span>
                    <RiskBadge risk={p.risk} />
                  </div>
                ))}
              </div>
              {products.length > 5 && (
                <button
                  onClick={() => setShowAllProducts(v => !v)}
                  className="mt-2 flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showAllProducts
                    ? <><ChevronUp size={12} /> Show less</>
                    : <><ChevronDown size={12} /> Show all ({products.length})</>
                  }
                </button>
              )}
            </div>

            <div className="border-t border-gray-800" />

            {/* Section 3: Suggested Queries — ALWAYS VISIBLE */}
            <div>
              <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-3">Suggested Queries</p>
              <div className="space-y-4">
                {QUERY_GROUPS.map(group => (
                  <div key={group.label}>
                    <p className={`text-xs font-semibold tracking-widest mb-1.5 ${group.labelColor}`}>
                      {group.label}
                    </p>
                    <div className="space-y-1">
                      {group.queries.map(q => (
                        <button
                          key={q}
                          onClick={() => handleChipClick(q)}
                          disabled={isLoading}
                          className={`
                            w-full text-left text-xs text-gray-100 border-l-2 pl-2.5 py-1.5 pr-1
                            ${group.borderColor} ${group.hoverBg}
                            hover:text-white transition-colors duration-150 rounded-r
                            disabled:opacity-40 disabled:cursor-not-allowed
                          `}
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-gray-800" />
          </div>

          {/* Section 4: New Session */}
          <div className="p-4 flex-shrink-0">
            <button
              onClick={handleNewSession}
              className="w-full text-xs text-gray-500 border border-gray-700 hover:border-gray-600 hover:text-gray-300 transition-colors rounded-lg py-2 px-3"
            >
              Upload New File / New Session
            </button>
          </div>
        </aside>

        {/* ── RIGHT PANEL — Chat area ──────────────────────────────────────── */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <p className="text-lg font-semibold text-white mb-2">Ask a planning question</p>
                <p className="text-sm text-gray-500">Select a query from the left panel or type your own</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'user' ? (
                  <div className="max-w-sm bg-gray-800 text-white rounded-xl rounded-tr-sm px-4 py-2.5 text-sm font-medium">
                    {msg.content as string}
                  </div>
                ) : (
                  <div className="w-full">
                    <AgentResponseCard response={msg.content as Record<string, unknown>} />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-[#111811] border border-gray-800 rounded-xl">
                  <AnalyzingDots />
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input bar */}
          <div className="flex-shrink-0 border-t border-gray-800 p-4">
            <div className="flex items-end gap-3 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 focus-within:border-gray-600 transition-colors">
              <textarea
                ref={textareaRef}
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a planning question... (Enter to send, Shift+Enter for newline)"
                rows={1}
                disabled={isLoading}
                className="flex-1 bg-transparent text-white placeholder-gray-600 text-sm resize-none outline-none leading-6 disabled:opacity-50"
                style={{ maxHeight: '80px', overflowY: 'auto' }}
              />
              <button
                onClick={() => handleSend()}
                disabled={!query.trim() || isLoading}
                className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  query.trim() && !isLoading
                    ? 'bg-green-600 hover:bg-green-500 text-white'
                    : 'bg-gray-800 text-gray-600 cursor-not-allowed'
                }`}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes analyzeBounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
          40% { transform: translateY(-5px); opacity: 1; }
        }
      `}</style>
    </Layout>
  )
}
