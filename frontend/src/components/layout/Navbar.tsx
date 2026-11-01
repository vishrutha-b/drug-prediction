"use client"

import React from "react"
import { Bell, Search, User, ChevronDown } from "lucide-react"

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 flex h-20 items-center justify-between border-b border-slate-100 bg-white/80 px-8 backdrop-blur-md">
      <div className="flex max-w-xl flex-1 items-center">
        <div className="group relative w-full">
          <Search
            className="absolute left-3 top-2.5 text-slate-400 transition-colors group-focus-within:text-sky-600"
            size={18}
          />
          <input
            type="text"
            placeholder="Search patient records or drug interactomes..."
            className="w-full rounded-xl border border-slate-100 bg-slate-50 py-2 pl-10 pr-4 text-sm outline-none transition-all focus:border-sky-500 focus:bg-white focus:ring-2 focus:ring-sky-100 placeholder:text-slate-400"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        <button className="group relative rounded-xl p-2 text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-900">
          <Bell size={20} />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full border-2 border-white bg-rose-500"></span>
        </button>

        <div className="mx-2 h-8 w-px bg-slate-100"></div>

        <button className="flex items-center gap-2 rounded-xl p-1.5 transition-all hover:bg-slate-50">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-600 text-xs font-bold text-white shadow-md shadow-sky-200">
            AU
          </div>
          <div className="hidden flex-col items-start lg:flex">
             <span className="text-xs font-bold text-slate-900 leading-none">Authorized User</span>
             <span className="text-[10px] text-slate-400 mt-0.5">Medical Professional</span>
          </div>
          <ChevronDown size={14} className="text-slate-400" />
        </button>
      </div>
    </header>
  )
}
