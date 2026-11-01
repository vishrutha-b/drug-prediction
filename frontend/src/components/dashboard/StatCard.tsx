import React from "react"
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react"
import { Card } from "../ui/Card"
import { cn } from "@/lib/utils"

interface StatCardProps {
  label: string
  value: string
  icon: LucideIcon
  trend: string
  trendUp?: boolean
  color?: string
}

export function StatCard({ label, value, icon: Icon, trend, trendUp, color }: StatCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className={cn("rounded-2xl bg-slate-50 p-3", color)}>
          <Icon size={24} />
        </div>
        <div className={cn(
          "flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold",
          trendUp ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
        )}>
          {trendUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {trend}
        </div>
      </div>
      <div className="mt-6">
        <p className="text-xs font-bold uppercase tracking-widest text-slate-400">{label}</p>
        <h3 className="mt-1 text-3xl font-extrabold text-slate-900">{value}</h3>
      </div>
    </Card>
  )
}
