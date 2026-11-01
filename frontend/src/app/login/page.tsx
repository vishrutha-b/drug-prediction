"use client"

import React, { useState, useEffect } from "react"
import { ShieldCheck, Mail, Lock, ArrowRight, Activity, Zap, Shield, Microscope, Fingerprint } from "lucide-react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [authStatus, setAuthStatus] = useState<"idle" | "verifying" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setAuthStatus("verifying")
    setErrorMessage("")
    
    const formData = new FormData(e.currentTarget as HTMLFormElement)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    try {
      const body = new URLSearchParams()
      body.append("username", email)
      body.append("password", password)

      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString()
      })

      if (!response.ok) throw new Error("Invalid institutional credentials.")

      const data = await response.json()
      localStorage.setItem("token", data.access_token)
      
      setAuthStatus("success")
      setTimeout(() => {
        window.location.href = "/dashboard"
      }, 800)
    } catch (error: any) {
      setAuthStatus("error")
      setErrorMessage(error.message || "Authentication failed.")
      setIsLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#020617] font-sans selection:bg-sky-500/30">
      {/* Dynamic Background Elements */}
      <div className="absolute inset-0 z-0">
        <div className="absolute -left-[10%] -top-[10%] h-[600px] w-[600px] rounded-full bg-sky-900/20 blur-[120px] animate-pulse"></div>
        <div className="absolute -right-[10%] -bottom-[10%] h-[600px] w-[600px] rounded-full bg-blue-900/10 blur-[120px]"></div>
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-[0.03]"></div>
        
        {/* Animated Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20"></div>
      </div>

      <main className="relative z-10 flex min-h-screen items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-[1100px] overflow-hidden rounded-[2.5rem] border border-white/5 bg-white/[0.02] shadow-2xl backdrop-blur-2xl lg:flex"
        >
          {/* Brand Panel */}
          <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-slate-900 to-black p-16 lg:flex">
            <div className="relative z-20 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600 shadow-lg shadow-sky-600/20">
                <ShieldCheck className="text-white" size={28} />
              </div>
              <span className="text-2xl font-black tracking-tighter text-white">INTELLI<span className="text-sky-500">INTERACTION</span></span>
            </div>

            <div className="relative z-20 space-y-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
              >
                <div className="mb-6 flex w-fit items-center gap-2 rounded-full border border-sky-500/20 bg-sky-500/10 px-4 py-1 text-[10px] font-bold uppercase tracking-widest text-sky-400">
                  <Activity size={12} className="animate-pulse" />
                  Clinical Protocol v4.2 Ready
                </div>
                <h1 className="font-outfit text-6xl font-black leading-[0.95] tracking-tighter text-white">
                  Predictive <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-blue-600">Pharmacology.</span>
                </h1>
                <p className="mt-8 max-w-md text-lg font-medium leading-relaxed text-slate-400">
                  Access the neural-backbone for drug-drug interaction research and patient safety monitoring.
                </p>
              </motion.div>

              <div className="flex gap-12 pt-4">
                {[
                  { label: "GAT ACCURACY", val: "99.4%", icon: Microscope },
                  { label: "FAERS PAIRS", val: "75K+", icon: Zap }
                ].map((stat, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500">
                      <stat.icon size={12} className="text-sky-500" />
                      {stat.label}
                    </div>
                    <div className="text-2xl font-black text-white">{stat.val}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative z-20">
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600 italic">
                Secure Institutional Gateway • HIPAA Compliant Environment
              </p>
            </div>

            {/* Decorative Pulse Circle */}
            <div className="absolute -right-20 top-1/2 h-[400px] w-[400px] -translate-y-1/2 rounded-full border border-sky-500/10 [mask-image:linear-gradient(to_right,transparent,black)]">
              <div className="absolute inset-4 rounded-full border border-sky-500/5"></div>
              <div className="absolute inset-12 rounded-full border border-sky-500/5"></div>
            </div>
          </div>

          {/* Login Panel */}
          <div className="flex flex-1 flex-col justify-center p-10 lg:p-20">
            <div className="mx-auto w-full max-w-sm space-y-10">
              <div className="space-y-2">
                <h2 className="font-outfit text-4xl font-black tracking-tight text-white">System Access</h2>
                <p className="text-sm font-bold text-slate-500">Authenticate via institutional credentials</p>
              </div>

              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-2">
                  <label className="ml-1 text-[10px] font-black uppercase tracking-widest text-slate-500">Institutional Email</label>
                  <div className="group relative transition-all">
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-sky-500 transition-colors">
                      <Mail size={18} />
                    </div>
                    <input 
                      name="email"
                      type="email" 
                      required 
                      placeholder="researcher@hospital.org"
                      className="h-14 w-full rounded-2xl border border-white/5 bg-white/[0.03] pl-12 pr-6 text-sm font-bold text-white transition-all focus:border-sky-500/50 focus:bg-white/[0.05] focus:outline-none focus:ring-4 focus:ring-sky-500/10 placeholder:text-slate-700"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Access Key</label>
                    <button type="button" className="text-[10px] font-black uppercase tracking-widest text-sky-500 hover:text-sky-400 transition-colors">Recover</button>
                  </div>
                  <div className="group relative transition-all">
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-sky-500 transition-colors">
                      <Lock size={18} />
                    </div>
                    <input 
                      name="password"
                      type="password" 
                      required 
                      placeholder="••••••••••••"
                      className="h-14 w-full rounded-2xl border border-white/5 bg-white/[0.03] pl-12 pr-6 text-sm font-bold text-white transition-all focus:border-sky-500/50 focus:bg-white/[0.05] focus:outline-none focus:ring-4 focus:ring-sky-500/10 placeholder:text-slate-700"
                    />
                  </div>
                </div>

                <button 
                  type="submit"
                  disabled={isLoading}
                  className="group relative flex h-14 w-full items-center justify-center overflow-hidden rounded-2xl bg-sky-600 text-sm font-black text-white transition-all hover:bg-sky-500 hover:shadow-[0_0_20px_rgba(14,165,233,0.3)] active:scale-[0.98] disabled:opacity-70"
                >
                  <AnimatePresence mode="wait">
                    {authStatus === "verifying" ? (
                      <motion.div 
                        key="verifying"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex items-center gap-2"
                      >
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white"></div>
                        INITIALIZING...
                      </motion.div>
                    ) : authStatus === "success" ? (
                      <motion.div 
                        key="success"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex items-center gap-2"
                      >
                        <Fingerprint size={20} />
                        ACCESS GRANTED
                      </motion.div>
                    ) : (
                      <motion.div 
                        key="idle"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-2"
                      >
                        AUTHORIZE ACCESS
                        <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </button>

                {errorMessage && (
                  <motion.p 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="text-center text-[11px] font-bold text-red-500 uppercase tracking-wider"
                  >
                    {errorMessage}
                  </motion.p>
                )}
              </form>

              <div className="flex items-start gap-4 rounded-3xl border border-white/5 bg-white/[0.02] p-6">
                <Shield className="mt-0.5 shrink-0 text-sky-500" size={20} />
                <p className="text-[10px] font-bold leading-relaxed tracking-wider text-slate-500 uppercase">
                  Institutional access requires Multi-Factor Authentication. All biometric data and PHI records are end-to-end encrypted under TLS 1.3.
                </p>
              </div>

              <div className="pt-6 text-center">
                <p className="text-xs font-bold text-slate-600">
                  New Researcher? <Link href="#" className="text-sky-500 hover:underline underline-offset-4">Request Credentials</Link>
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
