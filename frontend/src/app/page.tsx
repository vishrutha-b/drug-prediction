"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * IntelliInteraction - Entry Redirect
 * As per institutional requirements, the landing page is bypassed 
 * and users are directed straight to the secure login gateway.
 */
export default function RootPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/login")
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="relative">
        {/* Subtle loading state while redirecting */}
        <div className="h-12 w-12 rounded-full border-4 border-sky-500/20 border-t-sky-500 animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-2 w-2 bg-sky-500 rounded-full animate-pulse"></div>
        </div>
      </div>
    </div>
  )
}
