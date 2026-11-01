"use client"

import React from "react"
import { 
  FileText, 
  ShieldAlert, 
  AlertCircle, 
  CheckCircle2, 
  Search, 
  Download, 
  Eye, 
  MoreVertical 
} from "lucide-react"
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from "recharts"
import { StatCard } from "@/components/dashboard/StatCard"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

const chartData = [
  { name: "Mon", interaction: 45 },
  { name: "Tue", interaction: 52 },
  { name: "Wed", interaction: 48 },
  { name: "Thu", interaction: 61 },
  { name: "Fri", interaction: 35 },
  { name: "Sat", interaction: 24 },
  { name: "Sun", interaction: 18 },
]

const recentHistory = [
  { id: "R-101", patient: "Clinical Subject A", meds: "Warfarin + Aspirin", severity: "death", confidence: 98 },
  { id: "R-102", patient: "Clinical Subject B", meds: "Lisinopril + Ibuprofen", severity: "hospitalization", confidence: 85 },
  { id: "R-103", patient: "Clinical Subject C", meds: "Metformin + Contrast", severity: "hospitalization", confidence: 92 },
  { id: "R-104", patient: "Clinical Subject D", meds: "Amoxicillin + Pill", severity: "monitor", confidence: 76 },
  { id: "R-105", patient: "Clinical Subject E", meds: "Atorvastatin + Grapefruit", severity: "safe", confidence: 100 },
]

export default function DashboardPage() {
  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Clinical Overview</h1>
        <p className="mt-1 text-slate-500">Institutional DDI risk assessment monitoring system.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          label="Total Analyses" 
          value="1,284" 
          icon={FileText} 
          trend="+12%" 
          trendUp={true} 
          color="text-sky-600"
        />
        <StatCard 
          label="Critical Risks" 
          value="45" 
          icon={ShieldAlert} 
          trend="+2%" 
          trendUp={false} 
          color="text-rose-600"
        />
        <StatCard 
          label="Hospitalization" 
          value="122" 
          icon={AlertCircle} 
          trend="-5%" 
          trendUp={true} 
          color="text-orange-600"
        />
        <StatCard 
          label="Safe Profiles" 
          value="1,110" 
          icon={CheckCircle2} 
          trend="+8%" 
          trendUp={true} 
          color="text-emerald-600"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Interaction Sensitivity Trends</CardTitle>
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-sky-600/20 border border-sky-400"></span>
              <span className="text-[10px] font-bold uppercase text-slate-400">Model v2.4 Intelligence</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-80 w-full mt-6">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorInter" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0284c7" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#0284c7" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                    itemStyle={{fontSize: '12px', fontWeight: 'bold'}}
                  />
                  <Area type="monotone" dataKey="interaction" stroke="#0284c7" strokeWidth={3} fillOpacity={1} fill="url(#colorInter)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
             <div className="flex items-center justify-between border-b border-slate-50 pb-4">
                <span className="text-sm font-bold text-slate-600">High Risk (Level IV)</span>
                <Badge variant="death">45 Cases</Badge>
             </div>
             <div className="flex items-center justify-between border-b border-slate-50 pb-4">
                <span className="text-sm font-bold text-slate-600">Moderate Risk</span>
                <Badge variant="hospitalization">122 Cases</Badge>
             </div>
             <div className="flex items-center justify-between border-b border-slate-50 pb-4">
                <span className="text-sm font-bold text-slate-600">Observations Required</span>
                <Badge variant="monitor">312 Cases</Badge>
             </div>
             <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-600">Asymptomatic / Safe</span>
                <Badge variant="safe">1,110 Cases</Badge>
             </div>
             <div className="pt-4">
               <button className="w-full rounded-xl bg-slate-50 py-3 text-xs font-bold text-slate-500 transition-colors hover:bg-slate-100 uppercase tracking-widest">
                 Generate Compliance Report
               </button>
             </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Interaction Reports</CardTitle>
          <div className="flex items-center gap-3">
             <div className="relative">
                <Search className="absolute left-3 top-2 text-slate-400" size={14} />
                <input type="text" placeholder="Filter..." className="bg-slate-50 border border-slate-100 rounded-lg py-1.5 pl-9 pr-4 text-xs focus:ring-2 focus:ring-sky-100 outline-none" />
             </div>
             <button className="p-2 text-slate-400 hover:text-slate-900 rounded-lg hover:bg-slate-50 transition-colors">
                <Download size={18} />
             </button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
             <table className="w-full text-left">
                <thead>
                   <tr className="border-b border-slate-50">
                      <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Patient</th>
                      <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Medications</th>
                      <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Severity</th>
                      <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">AI Confidence</th>
                      <th className="px-8 py-4 text-right text-[10px] font-black uppercase tracking-widest text-slate-400">Actions</th>
                   </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                   {recentHistory.map((row) => (
                     <tr key={row.id} className="group hover:bg-slate-50/50 transition-colors">
                        <td className="px-8 py-5">
                           <span className="text-sm font-bold text-slate-900">{row.patient}</span>
                           <p className="text-[10px] text-slate-400 font-medium">{row.id}</p>
                        </td>
                        <td className="px-8 py-5">
                           <span className="text-xs font-semibold text-slate-700">{row.meds}</span>
                        </td>
                        <td className="px-8 py-5">
                           <Badge variant={row.severity as any}>
                              {row.severity}
                           </Badge>
                        </td>
                        <td className="px-8 py-5">
                           <div className="flex items-center gap-2">
                              <div className="h-1.5 w-16 rounded-full bg-slate-100 overflow-hidden">
                                 <div className="h-full bg-sky-600" style={{ width: `${row.confidence}%` }}></div>
                              </div>
                              <span className="text-xs font-bold text-slate-600">{row.confidence}%</span>
                           </div>
                        </td>
                        <td className="px-8 py-5 text-right">
                           <div className="flex items-center justify-end gap-2">
                              <button className="p-2 text-slate-400 hover:text-sky-600 hover:bg-sky-50 rounded-lg transition-colors"><Eye size={16} /></button>
                              <button className="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors"><MoreVertical size={16} /></button>
                           </div>
                        </td>
                     </tr>
                   ))}
                </tbody>
             </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
