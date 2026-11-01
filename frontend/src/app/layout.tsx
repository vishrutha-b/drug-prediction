"use client"

import React from "react"
import { usePathname } from "next/navigation"
import { Sidebar } from "@/components/layout/Sidebar"
import { Navbar } from "@/components/layout/Navbar"
import "@/app/globals.css"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  
  // High-fidelity flow control: Hide persistent navigation on public landing and login screens
  const isPublicPage = pathname === "/" || pathname === "/login"

  return (
    <html lang="en">
      <body className="bg-slate-50 font-sans antialiased text-slate-900">
        <div className="flex bg-white min-h-screen">
          {!isPublicPage && <Sidebar />}
          <div className={`flex flex-1 flex-col overflow-hidden ${isPublicPage ? 'bg-white' : 'bg-slate-50'}`}>
            {!isPublicPage && <Navbar />}
            <main className={`flex-1 overflow-y-auto ${isPublicPage ? 'p-0' : 'p-10'}`}>
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
