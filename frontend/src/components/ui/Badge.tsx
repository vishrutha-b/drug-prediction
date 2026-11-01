import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "safe" | "hospitalization" | "death" | "monitor"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-slate-100 text-slate-700",
    safe: "bg-emerald-50 text-emerald-700 border border-emerald-100",
    monitor: "bg-amber-50 text-amber-700 border border-amber-100",
    hospitalization: "bg-orange-50 text-orange-700 border border-orange-100",
    death: "bg-rose-50 text-rose-700 border border-rose-100",
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider transition-colors",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
