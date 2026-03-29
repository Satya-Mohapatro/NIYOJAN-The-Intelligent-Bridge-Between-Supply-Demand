import React, { useState } from 'react'
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'

interface AgentResponse {
  generated_at?: string
  query?: string
  intent?: string
  simulation_scenario?: string
  using_defaults?: boolean
  executive_summary?: string
  high_risk_products?: Array<{
    product: string
    risk_level: string
    reason: string
    urgency: string
  }>
  key_risk_drivers?: string[]
  recommended_actions?: Array<{
    action: string
    target_skus: string[]
    priority: string
  }>
  four_week_plan?: Record<string, string>
  monitoring_strategy?: string
}

function sectionLabel(text: string) {
  return (
    <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-3">{text}</p>
  )
}

function RiskPill({ level }: { level: string }) {
  const map: Record<string, string> = {
    High: 'bg-red-500/20 text-red-400 border-red-500/30',
    Medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    Low: 'bg-green-500/20 text-green-400 border-green-500/30',
  }
  const cls = map[level] || map.Low
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${cls}`}>{level}</span>
  )
}

function PriorityTag({ priority }: { priority: string }) {
  const isHigh = priority === 'High'
  return (
    <span className={`text-xs font-semibold px-1.5 py-0.5 rounded border ${
      isHigh
        ? 'bg-red-500/10 text-red-400 border-red-500/30'
        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    }`}>
      {priority.toUpperCase()}
    </span>
  )
}

function UrgencyText({ urgency }: { urgency: string }) {
  const map: Record<string, string> = {
    Immediate: 'text-red-400',
    Soon: 'text-amber-400',
    Monitor: 'text-green-400',
  }
  return <span className={`text-xs font-medium ${map[urgency] || 'text-gray-400'}`}>{urgency}</span>
}

const INTENT_LABEL: Record<string, string> = {
  analysis: 'Analysis',
  simulation: 'Simulation',
  strategy: 'Strategy',
  retrieval: 'Retrieval',
  error: 'Error',
}

const WEEK_ACCENTS = [
  'border-t-blue-500',
  'border-t-purple-500',
  'border-t-green-500',
  'border-t-amber-500',
]

const WEEK_LABELS = ['WEEK 1', 'WEEK 2', 'WEEK 3', 'WEEK 4']

export default function AgentResponseCard({ response }: { response: Record<string, unknown> }) {
  const r = response as AgentResponse
  const [collapsed, setCollapsed] = useState(false)

  const intent = r.intent || 'strategy'
  const weekEntries = Object.values(r.four_week_plan || {}).slice(0, 4)

  return (
    <div className="bg-[#111811] border-l-2 border-l-green-600 border border-gray-800 rounded-xl overflow-hidden">
      {/* ── Report Header ──────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-800 bg-[#0d140d]">
        <div>
          <p className="text-xs font-semibold tracking-widest uppercase text-gray-500">Intelligence Report</p>
          <div className="flex items-center gap-3 mt-0.5">
            <span className="text-xs text-gray-400">
              Intent: <span className="text-white font-medium">{INTENT_LABEL[intent] ?? intent}</span>
            </span>
            {r.simulation_scenario && r.simulation_scenario !== 'N/A' && (
              <span className="text-xs text-gray-400">
                Scenario: <span className="text-purple-300 font-medium">{r.simulation_scenario}</span>
              </span>
            )}
            {r.generated_at && (
              <span className="text-xs text-gray-600 hidden sm:inline">Generated: {r.generated_at}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {r.using_defaults && (
            <div className="flex items-center gap-1 text-amber-400/70">
              <AlertTriangle size={12} />
              <span className="text-xs hidden sm:inline">Estimated stock</span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(v => !v)}
            className="text-gray-600 hover:text-gray-400 transition-colors"
          >
            {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
          </button>
        </div>
      </div>

      {!collapsed && (
        <div className="divide-y divide-gray-800">
          {/* ── Executive Summary ───────────────────────────────────────────── */}
          {r.executive_summary && (
            <div className="px-5 py-4">
              {sectionLabel('Executive Summary')}
              <p className="text-sm leading-relaxed text-gray-200">{r.executive_summary}</p>
            </div>
          )}

          {/* ── High-Risk Products ──────────────────────────────────────────── */}
          {r.high_risk_products && r.high_risk_products.length > 0 && (
            <div className="px-5 py-4">
              {sectionLabel('High-Risk Products')}
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 pr-4 text-xs font-semibold tracking-wider uppercase text-gray-600">Product</th>
                      <th className="text-left py-2 pr-4 text-xs font-semibold tracking-wider uppercase text-gray-600">Risk</th>
                      <th className="text-left py-2 pr-4 text-xs font-semibold tracking-wider uppercase text-gray-600">Reason</th>
                      <th className="text-left py-2 text-xs font-semibold tracking-wider uppercase text-gray-600">Urgency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {r.high_risk_products.map((p, i) => (
                      <tr key={i} className={`border-b border-gray-800/50 ${i % 2 === 0 ? '' : 'bg-gray-900/30'}`}>
                        <td className="py-2.5 pr-4 text-white font-medium text-xs">{p.product}</td>
                        <td className="py-2.5 pr-4"><RiskPill level={p.risk_level} /></td>
                        <td className="py-2.5 pr-4 text-gray-400 text-xs leading-relaxed">{p.reason}</td>
                        <td className="py-2.5"><UrgencyText urgency={p.urgency} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── Key Risk Drivers ────────────────────────────────────────────── */}
          {r.key_risk_drivers && r.key_risk_drivers.length > 0 && (
            <div className="px-5 py-4">
              {sectionLabel('Key Risk Drivers')}
              <ul className="space-y-1.5">
                {r.key_risk_drivers.map((d, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-gray-600 font-bold text-xs mt-0.5 flex-shrink-0">—</span>
                    <span className="text-sm leading-relaxed text-gray-300">{d}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* ── Recommended Actions ─────────────────────────────────────────── */}
          {r.recommended_actions && r.recommended_actions.length > 0 && (
            <div className="px-5 py-4">
              {sectionLabel('Recommended Actions')}
              <div className="space-y-2">
                {r.recommended_actions.map((a, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <PriorityTag priority={a.priority} />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm text-gray-200">{a.action}</span>
                      {a.target_skus?.length > 0 && (
                        <span className="text-gray-600 text-xs ml-2">
                          {' '}— {a.target_skus.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── 4-Week Plan ─────────────────────────────────────────────────── */}
          {weekEntries.length > 0 && (
            <div className="px-5 py-4">
              {sectionLabel('4-Week Action Plan')}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {weekEntries.map((plan, i) => (
                  <div
                    key={i}
                    className={`bg-gray-900 border-t-2 ${WEEK_ACCENTS[i] || WEEK_ACCENTS[0]} border border-gray-800 rounded-lg p-3`}
                  >
                    <p className="text-xs font-semibold tracking-widest uppercase text-gray-500 mb-2">
                      {WEEK_LABELS[i]}
                    </p>
                    <p className="text-xs leading-relaxed text-gray-300">{plan}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Monitoring Strategy ─────────────────────────────────────────── */}
          {r.monitoring_strategy && (
            <div className="px-5 py-4">
              {sectionLabel('Monitoring Strategy')}
              <p className="text-sm leading-relaxed text-gray-200">{r.monitoring_strategy}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
