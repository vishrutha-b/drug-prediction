"use client"

import React, { useState, useEffect, useCallback } from "react"
import {
  Search,
  Filter,
  FileText,
  Eye,
  ChevronRight,
  ChevronLeft,
  X,
  RefreshCw,
  AlertTriangle,
  SlidersHorizontal,
  Calendar,
  Beaker,
  Globe,
  User,
} from "lucide-react"
import { Card, CardHeader, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Prediction {
  id: number
  drug_a: string
  drug_b: string
  indication: string | null
  substance: string | null
  severity_label: string
  confidence_score: number
  risk_score: number
  explanation: string
  recommendation: string | null
  alternatives: string[]
  risk_factors: string[]
  created_at: string
}

interface PaginatedHistory {
  items: Prediction[]
  total: number
  page: number
  limit: number
  pages: number
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getSeverityVariant(label: string) {
  const l = label.toLowerCase()
  if (l.includes("death")) return "death"
  if (l.includes("hospital")) return "hospitalization"
  if (l.includes("safe") || l.includes("none")) return "safe"
  return "monitor"
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  })
}

const SEVERITY_OPTIONS = [
  { label: "All Severities", value: "" },
  { label: "🔴 Death Risk", value: "DEATH RISK" },
  { label: "🟠 Hospital Admission", value: "HOSPITAL ADMISSION" },
  { label: "🟡 Monitoring Required", value: "MONITORING REQUIRED" },
  { label: "🟢 Safe", value: "Safe" },
]

const SORT_OPTIONS = [
  { label: "Newest First", value: "created_at", order: "desc" },
  { label: "Oldest First", value: "created_at", order: "asc" },
  { label: "Highest Risk", value: "risk_score", order: "desc" },
  { label: "Lowest Risk", value: "risk_score", order: "asc" },
  { label: "Highest Confidence", value: "confidence_score", order: "desc" },
]

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function HistoryPage() {
  // Filter state
  const [drugA, setDrugA] = useState("")
  const [drugB, setDrugB] = useState("")
  const [severity, setSeverity] = useState("")
  const [riskMin, setRiskMin] = useState("")
  const [riskMax, setRiskMax] = useState("")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [sortKey, setSortKey] = useState("created_at")
  const [sortOrder, setSortOrder] = useState("desc")

  // Pagination state
  const [page, setPage] = useState(1)
  const LIMIT = 8

  // Data state
  const [data, setData] = useState<PaginatedHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Scope toggle: false = my data only, true = all data in DB
  const [scopeAll, setScopeAll] = useState(false)

  // Panel state
  const [showFilters, setShowFilters] = useState(false)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  // ----- Fetch -----
  const fetchHistory = useCallback(async () => {
    setLoading(true)
    setError(null)

    const token = localStorage.getItem("token")
    if (!token) {
      setError("You are not logged in. Please log in first.")
      setLoading(false)
      return
    }

    // Build query string from active filters
    const params = new URLSearchParams()
    params.set("page", String(page))
    params.set("limit", String(LIMIT))
    params.set("sort_by", sortKey)
    params.set("order", sortOrder)
    if (drugA.trim())   params.set("drug_a__contains", drugA.trim())
    if (drugB.trim())   params.set("drug_b__contains", drugB.trim())
    if (severity)       params.set("severity_label", severity)
    if (riskMin)        params.set("risk_score__gte", riskMin)
    if (riskMax)        params.set("risk_score__lte", riskMax)
    if (dateFrom)       params.set("created_at__gte", dateFrom)
    if (dateTo)         params.set("created_at__lte", dateTo)

    try {
      const endpoint = scopeAll ? "/api/v1/history/all" : "/api/v1/history"
      const res = await fetch(`${endpoint}?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (res.status === 401) {
        setError("Session expired. Please log in again.")
        setLoading(false)
        return
      }
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        setError(body.detail || `Server error ${res.status}`)
        setLoading(false)
        return
      }

      const json: PaginatedHistory = await res.json()
      setData(json)
    } catch (e) {
      setError("Cannot reach the backend. Make sure the server is running.")
    } finally {
      setLoading(false)
    }
  }, [page, sortKey, sortOrder, drugA, drugB, severity, riskMin, riskMax, dateFrom, dateTo, scopeAll])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  // Reset page to 1 when filters change
  const applyFilters = () => {
    setPage(1)
    setShowFilters(false)
  }

  const clearFilters = () => {
    setDrugA(""); setDrugB(""); setSeverity("")
    setRiskMin(""); setRiskMax(""); setDateFrom(""); setDateTo("")
    setPage(1)
  }

  const hasActiveFilters = drugA || drugB || severity || riskMin || riskMax || dateFrom || dateTo

  // ----- Render -----
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Review History</h1>
          <p className="mt-1 text-slate-500">
            {scopeAll
              ? "Global research view — all DDI assessments across every account."
              : "Your personal audit trail of DDI interaction assessments."}
          </p>
        </div>
        <div className="flex items-center gap-3">

          {/* Scope Toggle */}
          <div className="flex items-center rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
            <button
              onClick={() => { setScopeAll(false); setPage(1) }}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition-all ${
                !scopeAll ? "bg-slate-900 text-white shadow" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <User size={13} /> My Data
            </button>
            <button
              onClick={() => { setScopeAll(true); setPage(1) }}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold transition-all ${
                scopeAll ? "bg-sky-600 text-white shadow" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <Globe size={13} /> All Data
            </button>
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-bold transition-all
              ${showFilters || hasActiveFilters
                ? "border-sky-500 bg-sky-50 text-sky-700"
                : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"}`}
          >
            <SlidersHorizontal size={16} />
            Filters
            {hasActiveFilters && (
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-600 text-[10px] font-black text-white">
                {[drugA, drugB, severity, riskMin, riskMax, dateFrom, dateTo].filter(Boolean).length}
              </span>
            )}
          </button>
          <button
            onClick={fetchHistory}
            className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white shadow-xl shadow-slate-200 transition-all hover:bg-slate-800 active:scale-95"
          >
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <Card className="border-sky-100 shadow-xl shadow-sky-50/50 animate-in slide-in-from-top duration-300">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {/* Drug A */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Drug A (contains)</label>
                <div className="relative">
                  <Beaker size={14} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    value={drugA}
                    onChange={e => setDrugA(e.target.value)}
                    placeholder="e.g. Warfarin"
                    className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 pl-9 pr-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                  />
                </div>
              </div>
              {/* Drug B */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Drug B (contains)</label>
                <div className="relative">
                  <Beaker size={14} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    value={drugB}
                    onChange={e => setDrugB(e.target.value)}
                    placeholder="e.g. Aspirin"
                    className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 pl-9 pr-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                  />
                </div>
              </div>
              {/* Severity */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Severity Label</label>
                <select
                  value={severity}
                  onChange={e => setSeverity(e.target.value)}
                  className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 px-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                >
                  {SEVERITY_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              {/* Sort */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Sort By</label>
                <select
                  value={`${sortKey}:${sortOrder}`}
                  onChange={e => {
                    const [k, o] = e.target.value.split(":")
                    setSortKey(k); setSortOrder(o)
                  }}
                  className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 px-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                >
                  {SORT_OPTIONS.map(o => (
                    <option key={`${o.value}:${o.order}`} value={`${o.value}:${o.order}`}>{o.label}</option>
                  ))}
                </select>
              </div>
              {/* Risk Min */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Risk Score ≥</label>
                <input
                  type="number" min="0" max="100"
                  value={riskMin}
                  onChange={e => setRiskMin(e.target.value)}
                  placeholder="0"
                  className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 px-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                />
              </div>
              {/* Risk Max */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Risk Score ≤</label>
                <input
                  type="number" min="0" max="100"
                  value={riskMax}
                  onChange={e => setRiskMax(e.target.value)}
                  placeholder="100"
                  className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 px-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                />
              </div>
              {/* Date From */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Date From</label>
                <div className="relative">
                  <Calendar size={14} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="date"
                    value={dateFrom}
                    onChange={e => setDateFrom(e.target.value)}
                    className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 pl-9 pr-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                  />
                </div>
              </div>
              {/* Date To */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Date To</label>
                <div className="relative">
                  <Calendar size={14} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="date"
                    value={dateTo}
                    onChange={e => setDateTo(e.target.value)}
                    className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2.5 pl-9 pr-3 text-sm font-semibold outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-50"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-3">
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-bold text-slate-500 hover:text-rose-600 hover:border-rose-200 transition-all"
                >
                  <X size={15} /> Clear All
                </button>
              )}
              <button
                onClick={applyFilters}
                className="flex items-center gap-2 rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-sky-100 hover:bg-sky-700 transition-all active:scale-95"
              >
                <Filter size={15} /> Apply Filters
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <div className="flex items-center gap-4 rounded-2xl border border-rose-100 bg-rose-50 p-6">
          <AlertTriangle size={24} className="shrink-0 text-rose-500" />
          <div>
            <p className="font-bold text-rose-700">{error}</p>
            {error.includes("log in") && (
              <a href="/login" className="mt-1 block text-sm font-bold text-sky-600 underline">Go to Login →</a>
            )}
          </div>
        </div>
      )}

      {/* Main Table Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b border-slate-50 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
              <FileText size={18} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-900">Prediction Records</p>
              {data && (
                <p className="text-[11px] text-slate-400 font-medium">
                  {data.total} total · page {data.page} of {data.pages}
                </p>
              )}
            </div>
          </div>
          {hasActiveFilters && (
            <div className="flex items-center gap-2 rounded-full bg-sky-50 px-4 py-1.5 text-xs font-bold text-sky-700 border border-sky-100">
              <Filter size={12} /> Filtered results
            </div>
          )}
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4">
              <div className="h-12 w-12 rounded-full border-4 border-sky-100 border-t-sky-600 animate-spin" />
              <p className="text-sm font-bold text-slate-400">Loading records…</p>
            </div>
          ) : !data || data.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
              <div className="rounded-3xl bg-slate-50 p-8 text-slate-200">
                <Search size={64} strokeWidth={1} />
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900">No records found</p>
                <p className="text-sm text-slate-400 mt-1">
                  {hasActiveFilters ? "Try adjusting or clearing your filters." : "Run your first interaction scan to see history here."}
                </p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50/50">
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">#</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Medications</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Severity</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Risk</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Confidence</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Date</th>
                    <th className="px-6 py-4 text-right text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {data.items.map((item) => {
                    const variant = getSeverityVariant(item.severity_label)
                    const isExpanded = expandedId === item.id
                    return (
                      <React.Fragment key={item.id}>
                        <tr
                          className="group cursor-pointer hover:bg-slate-50/70 transition-all"
                          onClick={() => setExpandedId(isExpanded ? null : item.id)}
                        >
                          <td className="px-6 py-4 text-xs font-bold text-slate-300">#{item.id}</td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <span className="rounded-md bg-slate-900 px-2 py-0.5 text-[11px] font-bold text-white">{item.drug_a}</span>
                              <span className="text-slate-300 text-xs">+</span>
                              <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-700">{item.drug_b}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={variant as any}>{item.severity_label}</Badge>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <div className="h-1.5 w-20 rounded-full bg-slate-100 overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all ${
                                    variant === "death" ? "bg-rose-500" :
                                    variant === "hospitalization" ? "bg-orange-500" :
                                    variant === "safe" ? "bg-emerald-500" : "bg-amber-500"
                                  }`}
                                  style={{ width: `${item.risk_score}%` }}
                                />
                              </div>
                              <span className="text-xs font-black text-slate-600">{item.risk_score}%</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-xs font-bold text-sky-600">{Math.round(item.confidence_score * 100)}%</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-[11px] font-semibold text-slate-500">{formatDate(item.created_at)}</span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Eye
                              size={16}
                              className={`ml-auto transition-colors ${isExpanded ? "text-sky-600" : "text-slate-300 group-hover:text-slate-600"}`}
                            />
                          </td>
                        </tr>

                        {/* Expanded Detail Row */}
                        {isExpanded && (
                          <tr>
                            <td colSpan={7} className="bg-sky-50/40 px-6 py-6 border-t border-sky-100">
                              <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                                {/* Explanation */}
                                <div className="lg:col-span-2 space-y-3">
                                  <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Clinical Explanation</h4>
                                  <p className="text-sm font-medium leading-relaxed text-slate-700 bg-white rounded-xl p-4 border border-slate-100">
                                    {item.explanation}
                                  </p>
                                  {item.recommendation && (
                                    <>
                                      <h4 className="text-[10px] font-black uppercase tracking-widest text-sky-600 mt-4">Recommendation</h4>
                                      <p className="text-sm font-semibold text-slate-800">{item.recommendation}</p>
                                    </>
                                  )}
                                </div>
                                {/* Badges */}
                                <div className="space-y-4">
                                  {item.risk_factors.length > 0 && (
                                    <div>
                                      <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">Risk Factors</h4>
                                      <div className="flex flex-wrap gap-1.5">
                                        {item.risk_factors.map(rf => (
                                          <span key={rf} className="rounded-lg border border-rose-100 bg-rose-50 px-2.5 py-1 text-[11px] font-bold text-rose-600">{rf}</span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  {item.alternatives.length > 0 && (
                                    <div>
                                      <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">Alternatives</h4>
                                      <div className="flex flex-wrap gap-1.5">
                                        {item.alternatives.map(a => (
                                          <span key={a} className="rounded-lg border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-700">{a}</span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2 py-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="rounded-lg p-2 text-slate-400 hover:bg-white hover:text-slate-900 transition-all disabled:opacity-30"
          >
            <ChevronLeft size={18} />
          </button>

          {Array.from({ length: Math.min(data.pages, 7) }, (_, i) => {
            const p = i + 1
            return (
              <button
                key={p}
                onClick={() => setPage(p)}
                className={`h-8 w-8 rounded-lg text-xs font-bold transition-all ${
                  p === page
                    ? "bg-slate-900 text-white shadow-lg shadow-slate-200"
                    : "text-slate-400 hover:bg-white hover:text-slate-900"
                }`}
              >
                {p}
              </button>
            )
          })}

          {data.pages > 7 && <span className="text-slate-400 font-bold px-1">…</span>}

          <button
            onClick={() => setPage(p => Math.min(data.pages, p + 1))}
            disabled={page === data.pages}
            className="rounded-lg p-2 text-slate-400 hover:bg-white hover:text-slate-900 transition-all disabled:opacity-30"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}
    </div>
  )
}
