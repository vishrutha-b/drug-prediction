"use client"

import React from "react"
import { 
  User, 
  Settings as SettingsIcon, 
  Shield, 
  Bell, 
  Database, 
  LogOut, 
  ChevronRight,
  Monitor,
  Key
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"

export default function SettingsPage() {
  const handleLogout = () => {
    // In a real app, clear session/cookies here
    window.location.href = "/"
  }

  return (
    <div className="mx-auto max-w-4xl space-y-10 pb-20 fade-up">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">System Configuration</h1>
        <p className="mt-1 text-slate-500">Manage professional profile, clinical preferences, and security protocols.</p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <Card>
          <CardHeader className="border-b border-slate-50 pb-6">
            <CardTitle className="flex items-center gap-3">
              <User size={20} className="text-sky-600" /> Professional Identity
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-8 space-y-8">
            <div className="flex items-center gap-6">
               <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-sky-100 font-black text-2xl text-sky-700 shadow-xl shadow-sky-50 transition-transform hover:scale-105 active:scale-95 cursor-pointer">
                  MP
               </div>
               <div>
                  <h3 className="text-xl font-bold text-slate-900">Authorized Medical Professional</h3>
                  <p className="text-sm font-semibold text-slate-400">ID: CDS-INST-8829 | Region: clinical-ca-01</p>
                  <button className="mt-2 text-xs font-black uppercase tracking-widest text-sky-600 hover:text-sky-700 transition-colors">Change Profile Photo</button>
               </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Institutional Email</label>
                  <input type="text" value="researcher.admin@hospital.org" readOnly className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm font-bold text-slate-500 outline-none" />
               </div>
               <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Primary Role</label>
                  <input type="text" value="Clinical Decision Analyst" readOnly className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm font-bold text-slate-500 outline-none" />
               </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="border-b border-slate-50 pb-6">
            <CardTitle className="flex items-center gap-3 text-rose-600">
              <Shield size={20} /> Security & Session
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-8 space-y-4">
             <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4 transition-all hover:bg-slate-100 cursor-pointer group">
                <div className="flex items-center gap-4">
                   <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-white shadow-sm text-slate-400 group-hover:text-sky-600 transition-colors">
                      <Key size={18} />
                   </div>
                   <div>
                      <h4 className="text-sm font-bold text-slate-800">Credential Management</h4>
                      <p className="text-xs text-slate-400">Updated 12 days ago</p>
                   </div>
                </div>
                <ChevronRight size={18} className="text-slate-300" />
             </div>

             <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4 transition-all hover:bg-slate-100 cursor-pointer group">
                <div className="flex items-center gap-4">
                   <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-white shadow-sm text-slate-400 group-hover:text-sky-600 transition-colors">
                      <Monitor size={18} />
                   </div>
                   <div>
                      <h4 className="text-sm font-bold text-slate-800">Active Sessions</h4>
                      <p className="text-xs text-slate-400">Currently active on 2 devices</p>
                   </div>
                </div>
                <ChevronRight size={18} className="text-slate-300" />
             </div>

             <div className="pt-8">
               <button 
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-3 bg-rose-50 py-4 text-sm font-black text-rose-600 rounded-2xl border border-rose-100 hover:bg-rose-100 transition-all active:scale-[0.98]"
               >
                 <LogOut size={20} /> Terminate Current Session (Logout)
               </button>
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
