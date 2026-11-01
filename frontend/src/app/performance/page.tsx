"use client"

import React from "react"
import { 
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from "recharts"
import { 
  TrendingUp, 
  Zap, 
  ShieldCheck, 
  Target, 
  Scale, 
  Focus, 
  Brain, 
  Cpu, 
  Activity,
  Layers,
  Network
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { StatCard } from "@/components/dashboard/StatCard"

const performanceData = [
  { epoch: "Jan", accuracy: 92.4, precision: 91.2, recall: 94.1, f1: 92.6 },
  { epoch: "Feb", accuracy: 94.8, precision: 93.5, recall: 95.8, f1: 94.6 },
  { epoch: "Mar", accuracy: 93.1, precision: 92.0, recall: 93.4, f1: 92.7 },
  { epoch: "Apr", accuracy: 96.2, precision: 95.1, recall: 97.2, f1: 96.1 },
  { epoch: "May", accuracy: 97.5, precision: 96.8, recall: 98.1, f1: 97.4 },
  { epoch: "Jun", accuracy: 98.7, precision: 98.2, recall: 99.4, f1: 98.8 },
]

export default function PerformancePage() {
  return (
    <div className="space-y-10 pb-20 fade-up">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="bg-sky-600 p-1.5 rounded-lg">
              <Cpu size={18} className="text-white" />
            </div>
            <span className="text-xs font-black uppercase tracking-[0.2em] text-sky-600">Core Neural Engine</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Model Reliability</h1>
          <p className="mt-1 text-slate-500 font-medium">Technical evaluation of SemanticFusionNet v2.4 (GAT-Architecture).</p>
        </div>
        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-2xl border border-slate-100 shadow-sm">
           <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
           <span className="text-xs font-bold text-slate-600 uppercase tracking-widest">Model Online</span>
           <div className="h-4 w-px bg-slate-100"></div>
           <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">v2.4.12-Stable</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5 animate-in slide-in-from-bottom duration-500">
        <StatCard 
          label="Accuracy" 
          value="98.7%" 
          icon={Target} 
          trend="+0.3%" 
          trendUp={true} 
          color="text-emerald-600"
        />
        <StatCard 
          label="Precision" 
          value="98.2%" 
          icon={Focus} 
          trend="+0.1%" 
          trendUp={true} 
          color="text-sky-600"
        />
        <StatCard 
          label="Recall" 
          value="99.4%" 
          icon={ShieldCheck} 
          trend="+0.2%" 
          trendUp={true} 
          color="text-indigo-600"
        />
        <StatCard 
          label="F1-Score" 
          value="98.8%" 
          icon={Scale} 
          trend="+0.15%" 
          trendUp={true} 
          color="text-violet-600"
        />
        <StatCard 
          label="ROC-AUC" 
          value="0.992" 
          icon={TrendingUp} 
          trend="+0.004" 
          trendUp={true} 
          color="text-amber-600"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-8">
           <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              {/* Accuracy Card */}
              <Card className="shadow-xl shadow-slate-100/50 hover:shadow-sky-100/50 transition-shadow duration-500 border-none">
                 <CardHeader className="pb-0">
                   <CardTitle className="flex items-center gap-2 text-sm font-bold text-slate-500">
                      <Target size={16} className="text-emerald-500" />
                      ACCURACY TREND
                   </CardTitle>
                 </CardHeader>
                 <CardContent className="h-48 pt-4 pb-8">
                    <ResponsiveContainer width="100%" height="100%">
                       <BarChart data={performanceData} margin={{ top: 20, right: 0, left: 0, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis 
                            dataKey="epoch" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fill: '#94a3b8', fontSize: 11, fontWeight: 700}} 
                            dy={10}
                          />
                          <YAxis domain={['auto', 'auto']} hide />
                          <Tooltip 
                            contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                            cursor={{fill: '#f8fafc'}}
                          />
                          <Bar 
                            dataKey="accuracy" 
                            fill="#10b981" 
                            radius={[6, 6, 0, 0]} 
                            label={{ position: 'top', fill: '#10b981', fontSize: 10, fontWeight: 'bold', offset: 10 }} 
                          />
                       </BarChart>
                    </ResponsiveContainer>
                 </CardContent>
              </Card>

              {/* F1 Card */}
              <Card className="shadow-xl shadow-slate-100/50 hover:shadow-sky-100/50 transition-shadow duration-500 border-none">
                 <CardHeader className="pb-0">
                   <CardTitle className="flex items-center gap-2 text-sm font-bold text-slate-500">
                      <Scale size={16} className="text-violet-500" />
                      F1-SCORE TREND
                   </CardTitle>
                 </CardHeader>
                 <CardContent className="h-48 pt-4 pb-8">
                    <ResponsiveContainer width="100%" height="100%">
                       <BarChart data={performanceData} margin={{ top: 20, right: 0, left: 0, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis 
                            dataKey="epoch" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fill: '#94a3b8', fontSize: 11, fontWeight: 700}} 
                            dy={10}
                          />
                          <YAxis domain={['auto', 'auto']} hide />
                          <Tooltip 
                            contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                            cursor={{fill: '#f8fafc'}}
                          />
                          <Bar 
                            dataKey="f1" 
                            fill="#8b5cf6" 
                            radius={[6, 6, 0, 0]} 
                            label={{ position: 'top', fill: '#8b5cf6', fontSize: 10, fontWeight: 'bold', offset: 10 }} 
                          />
                       </BarChart>
                    </ResponsiveContainer>
                 </CardContent>
              </Card>
           </div>

           <Card className="shadow-2xl shadow-slate-100/70 border-none overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <Brain size={120} />
              </div>
              <CardHeader className="border-b border-slate-50 pb-6 px-10 pt-10">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-xl">Convergence Metrics</CardTitle>
                    <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Multi-Metric Epoch Analysis</p>
                  </div>
                  <div className="flex gap-4">
                     <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-sky-500"></span>
                        <span className="text-[10px] font-black text-slate-500 uppercase">Precision</span>
                     </div>
                     <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-indigo-500"></span>
                        <span className="text-[10px] font-black text-slate-500 uppercase">Recall</span>
                     </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="h-80 px-4 py-8">
                 <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                       <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                       <XAxis dataKey="epoch" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                       <YAxis domain={['auto', 'auto']} axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} width={40} />
                       <Tooltip 
                        contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                        itemStyle={{fontSize: '12px', fontWeight: 'bold'}}
                       />
                       <Line 
                        type="monotone" 
                        dataKey="precision" 
                        name="Precision" 
                        stroke="#0ea5e9" 
                        strokeWidth={4} 
                        dot={{r: 4, strokeWidth: 2, fill: '#fff'}} 
                        activeDot={{r: 6}} 
                       />
                       <Line 
                        type="monotone" 
                        dataKey="recall" 
                        name="Recall" 
                        stroke="#6366f1" 
                        strokeWidth={4} 
                        dot={{r: 4, strokeWidth: 2, fill: '#fff'}} 
                        activeDot={{r: 6}} 
                       />
                    </LineChart>
                 </ResponsiveContainer>
              </CardContent>
           </Card>
        </div>

        <div className="space-y-6">
           <Card className="bg-slate-900 border-none text-white shadow-2xl overflow-hidden relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-sky-600/20 to-transparent"></div>
              <CardHeader className="relative z-10">
                 <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/20 text-sky-400 mb-4">
                    <Activity size={20} />
                 </div>
                 <CardTitle className="text-white">Analysis Architecture</CardTitle>
                 <p className="text-xs text-slate-400 font-medium">Hybrid GAT-Convolutional Topology</p>
              </CardHeader>
              <CardContent className="relative z-10 space-y-6 pt-4">
                 {[
                   { label: "Attention Heads", value: "8", icon: Network },
                   { label: "Embedding Depth", value: "768d", icon: Layers },
                   { label: "Graph Layers", value: "3", icon: Cpu }
                 ].map((item, i) => (
                   <div key={i} className="flex items-center justify-between border-b border-white/5 pb-4 last:border-0 last:pb-0">
                      <div className="flex items-center gap-3">
                         <div className="bg-white/5 p-2 rounded-lg text-slate-400">
                            <item.icon size={16} />
                         </div>
                         <span className="text-sm font-bold text-slate-300">{item.label}</span>
                      </div>
                      <span className="text-sm font-black text-sky-400">{item.value}</span>
                   </div>
                 ))}
                 
                 <div className="pt-4">
                    <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
                       <p className="text-[10px] leading-relaxed text-slate-400 font-semibold italic">
                         "Utilizing Multi-head Attention to assign weights to neighboring drug nodes, enabling feature propagation across the pharmacophore graph."
                       </p>
                    </div>
                 </div>
              </CardContent>
           </Card>

           <Card className="border-none bg-sky-50/50 shadow-sm border border-sky-100">
              <CardHeader>
                <CardTitle className="text-lg">Deployment Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                 <div className="space-y-1">
                    <div className="flex justify-between text-xs font-bold mb-1">
                       <span className="text-slate-500">COMPUTE USAGE</span>
                       <span className="text-sky-600">42%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                       <div className="h-full bg-sky-500 rounded-full" style={{ width: '42%' }}></div>
                    </div>
                 </div>
                 <div className="space-y-1">
                    <div className="flex justify-between text-xs font-bold mb-1">
                       <span className="text-slate-500">MOCK DATA RECALL</span>
                       <span className="text-emerald-600">99.4%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                       <div className="h-full bg-emerald-500 rounded-full" style={{ width: '99.4%' }}></div>
                    </div>
                 </div>
              </CardContent>
           </Card>
        </div>
      </div>
    </div>
  )
}
