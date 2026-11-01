"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, ShieldCheck, History as HistoryIcon, BarChart2, Laptop, Settings, Zap, Network } from "lucide-react"
import { cn } from "@/lib/utils"

const sidebarItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/checker", icon: ShieldCheck, label: "Prescription Checker" },
  { href: "/history", icon: HistoryIcon, label: "Review History" },
  { href: "/analytics", icon: BarChart2, label: "Medical Analytics" },
  { href: "/performance", icon: Zap, label: "Model Performance" },
  { href: "/visualizer", icon: Network, label: "Interactome Visualizer" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-72 flex-col border-r border-slate-200 bg-white shadow-sm">
      <div className="flex h-20 items-center px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-600 shadow-lg shadow-sky-200">
            <ShieldCheck className="text-white" size={24} />
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-slate-900">IntelliInteraction</span>
            <span className="text-[10px] font-bold uppercase tracking-widest text-sky-600">Healthcare AI</span>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-1 px-4 pt-6">
        <div className="mb-4 px-4 text-[10px] font-bold uppercase tracking-widest text-slate-400">
          Main Management
        </div>
        {sidebarItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-4 py-3.5 text-sm font-semibold transition-all duration-300",
                isActive
                  ? "bg-sky-50 text-sky-700 border border-sky-100 shadow-sm"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-950"
              )}
            >
              <item.icon
                size={20}
                className={cn(
                  "transition-transform group-hover:scale-110",
                  isActive ? "text-sky-700" : "text-slate-400 group-hover:text-slate-600"
                )}
              />
              {item.label}
            </Link>
          )
        })}

        <div className="mb-4 mt-10 px-4 text-[10px] font-bold uppercase tracking-widest text-slate-400">
          Support & Config
        </div>
        <Link
          href="/settings"
          className="group flex items-center gap-3 rounded-xl px-4 py-3.5 text-sm font-semibold text-slate-500 transition-all hover:bg-slate-50 hover:text-slate-950"
        >
          <Settings size={20} className="text-slate-400" />
          Settings
        </Link>
      </div>

      <div className="border-t border-slate-100 p-6">
        <div className="flex items-center gap-3 rounded-2xl bg-slate-50 p-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-100 font-bold text-sky-700 shadow-sm">
            MP
          </div>
          <div className="flex min-w-0 flex-1 flex-col">
            <span className="truncate text-sm font-bold text-slate-900">Medical Professional</span>
            <span className="truncate text-[10px] text-slate-500">Authorized User</span>
          </div>
        </div>
      </div>
    </div>
  )
}
