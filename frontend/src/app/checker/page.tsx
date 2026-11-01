"use client"

import React, { useState } from "react"
import { 
  Plus, 
  Trash2, 
  ShieldAlert, 
  CheckCircle2, 
  Activity, 
  FileCheck, 
  ChevronRight, 
  Info,
  RefreshCw,
  AlertTriangle
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { cn } from "@/lib/utils"

interface Medicine {
  id: string
  name: string
}

export default function CheckerPage() {
  const [medicines, setMedicines] = useState<Medicine[]>([
    { id: "1", name: "" },
    { id: "2", name: "" }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const addMedicine = () => {
    setMedicines([...medicines, { id: Math.random().toString(), name: "" }])
  }

  const removeMedicine = (id: string) => {
    if (medicines.length > 2) {
      setMedicines(medicines.filter(m => m.id !== id))
    }
  }

  const handleCheck = async () => {
    if (medicines.some(m => !m.name)) return
    
    setIsLoading(true)
    setResult(null)
    setError(null)
    
    try {
      // In a real app, we'd get the token from a context or localStorage
      const token = localStorage.getItem("token")
      
      const response = await fetch("/api/v1/check-interaction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          drug_a: medicines[0].name,
          drug_b: medicines[1].name,
          indication: "General Clinical Check",
          substance: "Tablet"
        })
      })

      if (response.status === 401) {
        throw new Error("Unauthorized")
      }
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      const data = await response.json()
      
      // Map API response to UI model
      const severity = data.severity_label
      const variant = severity.toLowerCase().includes("death") ? "death" : 
                      severity.toLowerCase().includes("hospital") ? "hospitalization" :
                      severity.toLowerCase().includes("safe") ? "safe" : "monitor"

      setResult({
        severity: severity,
        variant: variant,
        confidence: Math.round(data.confidence_score * 1000) / 10,
        explanation: data.explanation,
        riskFactors: data.risk_factors || [],
        riskScore: data.risk_score || 0,
        drugPairs: [data.drug_a, data.drug_b],
        recommendation: data.recommendation || "Maintain standard clinical observation protocols.",
        alternatives: data.alternatives || ["Clinical Consultation Required"]
      })
    } catch (err: any) {
      console.error(err)
      if (err.message.includes("401") || err.message.includes("Unauthorized")) {
        setError("Your clinical session has expired. Please log in again to access the scanner.")
      } else {
        setError("Unable to reach the clinical analysis service. Please ensure the backend is running.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-10 pb-20 fade-up">
      <div className="flex flex-col space-y-2 text-center lg:text-left">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Safety Protocol Scanner</h1>
        <p className="text-slate-500">Live clinical interaction assessment utilizing SemanticFusionNet architecture.</p>
      </div>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12">
        {/* Input Controls */}
        <div className="lg:col-span-5 space-y-6">
           <Card className="border-sky-100 shadow-xl shadow-sky-50/50">
              <CardHeader>
                 <CardTitle className="text-xl">Medication Cross-Scan</CardTitle>
                 <p className="text-xs font-medium text-slate-400">Add medicines to check for critical DDI risk.</p>
              </CardHeader>
              <CardContent className="space-y-6">
                 {medicines.map((med, index) => (
                   <div key={med.id} className="flex items-center gap-3 animate-in slide-in-from-left duration-300">
                      <div className="flex-1 space-y-1">
                         <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 px-1">Medication {String.fromCharCode(65 + index)}</label>
                         <div className="relative group">
                            <input 
                              type="text" 
                              placeholder="e.g. Warfarin"
                              className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm font-semibold outline-none focus:bg-white focus:border-sky-500 transition-all focus:ring-4 focus:ring-sky-50"
                              value={med.name}
                              onChange={(e) => {
                                const newMeds = [...medicines]
                                newMeds[index].name = e.target.value
                                setMedicines(newMeds)
                              }}
                            />
                         </div>
                      </div>
                      {medicines.length > 2 && (
                        <button 
                          onClick={() => removeMedicine(med.id)}
                          className="mt-5 p-3 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all"
                        >
                           <Trash2 size={18} />
                        </button>
                      )}
                   </div>
                 ))}

                 <div className="pt-2 flex gap-3">
                    <button 
                      onClick={addMedicine}
                      className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-dashed border-slate-200 py-3 text-xs font-bold text-slate-400 transition-all hover:bg-slate-50 hover:border-slate-300 hover:text-slate-600"
                    >
                      <Plus size={16} /> Add Medication
                    </button>
                 </div>

                 <div className="pt-6">
                    <button 
                      onClick={handleCheck}
                      disabled={isLoading || medicines.some(m => !m.name)}
                      className="w-full flex items-center justify-center gap-3 bg-sky-600 py-4 text-sm font-bold text-white shadow-xl shadow-sky-100 rounded-2xl hover:bg-sky-700 transition-all active:scale-[0.98] disabled:opacity-50 disabled:grayscale"
                    >
                      {isLoading ? <RefreshCw className="animate-spin" size={20} /> : <FileCheck size={20} />}
                      {isLoading ? "Analyzing Clinical Pathways..." : "Run Interaction Scan"}
                    </button>
                 </div>
              </CardContent>
           </Card>

           <div className="rounded-3xl bg-sky-50 border border-sky-100 p-6 flex gap-4">
              <div className="h-10 w-10 shrink-0 flex items-center justify-center rounded-xl bg-white shadow-sm text-sky-600">
                 <Info size={20} />
              </div>
              <p className="text-[11px] font-medium leading-relaxed text-slate-600">
                <span className="font-bold text-sky-700">Clinical Focus:</span> Our hybrid GAT architecture utilizes topological drug relationships derived from modern clinical trials. Always cross-verify with institutional guidelines.
              </p>
           </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-7">
           {!result && !isLoading && !error && (
             <div className="h-full min-h-[500px] flex flex-col items-center justify-center space-y-6 rounded-3xl border-2 border-dashed border-slate-200 bg-white/50 p-20 text-center">
                <div className="rounded-3xl bg-slate-50 p-8 text-slate-200">
                   <ShieldAlert size={80} strokeWidth={1} />
                </div>
                <div className="max-w-xs space-y-2">
                   <h3 className="text-xl font-bold text-slate-900">System Ready</h3>
                   <p className="text-sm text-slate-400">Input primary and secondary medications to initiate interaction simulation.</p>
                </div>
             </div>
           )}

           {error && !isLoading && (
             <div className="h-full min-h-[500px] flex flex-col items-center justify-center space-y-6 rounded-3xl border-2 border-rose-100 bg-rose-50/30 p-20 text-center animate-in zoom-in duration-300">
                <div className="rounded-3xl bg-rose-100 p-8 text-rose-500">
                   <AlertTriangle size={80} strokeWidth={1} />
                </div>
                <div className="max-w-md space-y-4">
                   <h3 className="text-xl font-bold text-slate-900">Analysis Halted</h3>
                   <p className="text-sm text-slate-600 font-medium">{error}</p>
                   {error.includes("log in") && (
                      <button 
                        onClick={() => window.location.href = "/login"}
                        className="mt-4 px-8 py-3 bg-slate-900 text-white text-xs font-bold rounded-xl hover:bg-slate-800 transition-all active:scale-95 uppercase tracking-widest"
                      >
                         Go to Login Portal
                      </button>
                   )}
                </div>
             </div>
           )}

           {isLoading && (
              <div className="h-full min-h-[500px] flex flex-col items-center justify-center space-y-6 glass-light rounded-3xl border border-slate-100 p-20 animate-pulse">
                 <div className="relative">
                    <div className="h-24 w-24 border-4 border-sky-100 border-t-sky-600 rounded-full animate-spin"></div>
                    <Activity size={32} className="absolute inset-0 m-auto text-sky-600 animate-pulse" />
                 </div>
                 <div className="text-center">
                    <p className="text-lg font-bold text-slate-900">Synthesizing Model Data</p>
                    <p className="text-sm text-slate-400 text-[10px] uppercase font-bold tracking-widest mt-1">GAT Multi-head Attention Processing...</p>
                 </div>
              </div>
           )}

           {result && !isLoading && (
             <div className="space-y-6 animate-in fade-in slide-in-from-right duration-700">
                <Card className={cn(
                  "overflow-hidden border-l-4 shadow-2xl transition-all",
                  result.variant === "death" ? "border-l-rose-500 shadow-rose-100/50" : 
                  result.variant === "hospitalization" ? "border-l-orange-500 shadow-orange-100/50" :
                  result.variant === "safe" ? "border-l-emerald-500 shadow-emerald-100/50" :
                  "border-l-amber-500 shadow-amber-100/50"
                )}>
                   <CardHeader className="flex flex-row items-start justify-between bg-slate-50/30">
                      <div className="space-y-1">
                         <Badge variant={result.variant}>
                            {result.severity.toUpperCase()} Detected
                         </Badge>
                         <CardTitle className="text-3xl font-black tracking-tight text-slate-900 mt-2">Interaction Profile</CardTitle>
                      </div>
                       <div className="flex gap-4">
                         <div className="flex flex-col items-center rounded-2xl bg-white p-3 shadow-sm border border-slate-100">
                            <span className="text-[10px] font-black uppercase text-slate-400">Confidence</span>
                            <span className="text-2xl font-black text-sky-600">{result.confidence}%</span>
                         </div>
                         <div className="flex flex-col items-center rounded-2xl bg-white p-3 shadow-sm border border-slate-100">
                            <span className="text-[10px] font-black uppercase text-rose-400">Risk Intensity</span>
                            <span className="text-2xl font-black text-rose-600">{result.riskScore}%</span>
                         </div>
                       </div>
                   </CardHeader>
                   <CardContent className="space-y-8 pt-8">
                      <div className="flex gap-4 rounded-2xl bg-slate-50 p-6 border border-slate-100">
                         <AlertTriangle className="text-rose-500 shrink-0" size={28} />
                         <p className="text-sm font-semibold leading-relaxed text-slate-700">
                            {result.explanation}
                         </p>
                      </div>

                          <div className="space-y-2">
                             <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Medications Involved</h4>
                             <div className="flex flex-wrap gap-2">
                                {result.drugPairs.map((d: any) => (
                                  <span key={d} className="rounded-lg bg-slate-900 text-white px-3 py-1.5 text-xs font-bold leading-none">{d}</span>
                                ))}
                             </div>
                          </div>
                          
                          <div className="space-y-2">
                             <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Clinical Risk Factors</h4>
                             <div className="flex flex-wrap gap-2">
                                {result.riskFactors.map((rf: any) => (
                                  <span key={rf} className="rounded-lg border border-rose-100 bg-rose-50 text-rose-600 px-3 py-1.5 text-xs font-bold leading-none">{rf}</span>
                                ))}
                             </div>
                          </div>

                          <div className="space-y-2 col-span-2 mt-4">
                            <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Clinical Alternatives</h4>
                            <div className="flex flex-wrap gap-2">
                                {result.alternatives.map((a: any) => (
                                  <span key={a} className="rounded-lg border border-emerald-100 bg-emerald-50 text-emerald-700 px-3 py-1.5 text-xs font-bold leading-none">{a}</span>
                                ))}
                             </div>
                          </div>

                      <div className="space-y-3 px-2 pt-4">
                         <h4 className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-sky-600">
                            <CheckCircle2 size={12} /> Institutional Protocol
                         </h4>
                         <p className="text-md font-extrabold leading-snug text-slate-800">
                            {result.recommendation}
                         </p>
                      </div>

                      <div className="-mx-6 -mb-6 mt-10 flex items-center justify-between border-t border-slate-100 bg-slate-50/50 p-6">
                         <button className="flex items-center gap-2 text-sm font-bold text-sky-600 hover:text-sky-700 transition-colors">
                            <FileCheck size={18} /> Export Clinical Factsheet
                         </button>
                         <button onClick={() => setResult(null)} className="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors uppercase tracking-[0.2em]">
                            Reset Scanner
                         </button>
                      </div>
                   </CardContent>
                </Card>
             </div>
           )}
        </div>
      </div>
    </div>
  )
}
