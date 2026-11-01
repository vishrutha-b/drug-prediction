"use client"

import React from "react"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line,
  Legend
} from "recharts"
import { TrendingUp, Activity, BarChart3, PieChart as PieChartIcon, Zap, ShieldCheck, Target, Scale, Focus, Brain, Award } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { StatCard } from "@/components/dashboard/StatCard"

const severityData = [
  { name: "Safe", value: 1110, color: "#10b981" },
  { name: "Monitor", value: 312, color: "#f59e0b" },
  { name: "Hospitalization", value: 122, color: "#f97316" },
  { name: "Death Risk", value: 45, color: "#f43f5e" },
]

const monthlyTrend = [
  { month: "Jan", alerts: 400, safe: 2400 },
  { month: "Feb", alerts: 300, safe: 1398 },
  { month: "Mar", alerts: 200, safe: 9800 },
  { month: "Apr", alerts: 278, safe: 3908 },
  { month: "May", alerts: 189, safe: 4800 },
  { month: "Jun", alerts: 239, safe: 3800 },
]

const topDrugs = [
  { name: "Warfarin", count: 452 },
  { name: "Aspirin", count: 398 },
  { name: "Lisinopril", count: 312 },
  { name: "Metformin", count: 284 },
  { name: "Simvastatin", count: 210 },
]

const performanceData = [
  { epoch: "Jan", accuracy: 96.5, precision: 95.8, recall: 97.2, f1: 96.5 },
  { epoch: "Feb", accuracy: 97.2, precision: 96.5, recall: 97.8, f1: 97.1 },
  { epoch: "Mar", accuracy: 97.8, precision: 97.1, recall: 98.4, f1: 97.7 },
  { epoch: "Apr", accuracy: 98.1, precision: 97.8, recall: 98.9, f1: 98.3 },
  { epoch: "May", accuracy: 98.5, precision: 98.0, recall: 99.2, f1: 98.6 },
  { epoch: "Jun", accuracy: 98.7, precision: 98.2, recall: 99.4, f1: 98.8 },
]

export default function AnalyticsPage() {
  return (
    <div className="space-y-10 pb-20 fade-up">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Population Analytics</h1>
        <p className="mt-1 text-slate-500">Cross-institutional drug interaction patterns and severity distribution.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <StatCard 
          label="Monthly Scan Volume" 
          value="14,204" 
          icon={Activity} 
          trend="+18%" 
          trendUp={true} 
          color="text-sky-600"
        />
        <StatCard 
          label="Clinician Alignment" 
          value="88.0%" 
          icon={Zap} 
          trend="-2%" 
          trendUp={false} 
          color="text-amber-600"
        />
        <StatCard 
          label="Active Institutions" 
          value="42" 
          icon={Award} 
          trend="+4" 
          trendUp={true} 
          color="text-indigo-600"
        />
      </div>

      <div className="pt-6">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-sky-600" size={24} />
          <h2 className="text-2xl font-bold text-slate-900">Population Trends & Distribution</h2>
        </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <Card className="shadow-xl shadow-slate-100/50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
               <PieChartIcon size={18} className="text-slate-400" />
               Severity Distribution
            </CardTitle>
          </CardHeader>
          <CardContent className="h-80 pt-6">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={8}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                  itemStyle={{fontSize: '12px', fontWeight: 'bold'}}
                />
                <Legend iconType="circle" wrapperStyle={{fontSize: '12px', fontWeight: '600', paddingTop: '20px'}} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="shadow-xl shadow-slate-100/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
               <TrendingUp size={18} className="text-slate-400" />
               Institutional Safety Trends
            </CardTitle>
          </CardHeader>
          <CardContent className="h-80 pt-6">
             <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyTrend}>
                   <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                   <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                   <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                   <Tooltip 
                      cursor={{fill: '#f8fafc'}}
                      contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                   />
                   <Bar dataKey="alerts" fill="#f43f5e" radius={[4, 4, 0, 0]} barSize={20} name="High Risk Flagged" />
                   <Bar dataKey="safe" fill="#e2e8f0" radius={[4, 4, 0, 0]} barSize={20} name="Safe Scans" />
                </BarChart>
             </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-xl shadow-slate-100/50">
         <CardHeader>
            <CardTitle className="flex items-center gap-2">
               <BarChart3 size={18} className="text-slate-400" />
               Top Flagged Medications (Institutional)
            </CardTitle>
         </CardHeader>
         <CardContent className="h-96 pt-10">
            <ResponsiveContainer width="100%" height="100%">
               <BarChart layout="vertical" data={topDrugs}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" hide />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fill: '#475569', fontSize: 12, fontWeight: 'bold'}} 
                    width={100} 
                  />
                  <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'}}
                  />
                  <Bar dataKey="count" fill="#0ea5e9" radius={[0, 4, 4, 0]} barSize={30} label={{ position: 'right', fill: '#64748b', fontSize: 11, fontWeight: 'bold' }} />
               </BarChart>
            </ResponsiveContainer>
         </CardContent>
      </Card>
    </div>
    </div>
  )
}
