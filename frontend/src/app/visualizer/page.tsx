"use client"

import React, { useState, useEffect, useMemo, useRef } from "react"
import dynamic from "next/dynamic"
import { 
  Network, 
  Search, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Info, 
  Filter, 
  ShieldAlert,
  Zap,
  Activity,
  ChevronRight
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

// Dynamic import for client-side only rendering
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false })

const mockGraphData = {
  nodes: [
    { id: "Warfarin", group: 1, val: 20, severity: "death" },
    { id: "Aspirin", group: 1, val: 15, severity: "hospitalization" },
    { id: "Lisinopril", group: 2, val: 12, severity: "monitor" },
    { id: "Ibuprofen", group: 2, val: 10, severity: "monitor" },
    { id: "Metformin", group: 3, val: 14, severity: "hospitalization" },
    { id: "Contrast Medium", group: 3, val: 10, severity: "death" },
    { id: "Amoxicillin", group: 4, val: 8, severity: "safe" },
    { id: "Birth Control", group: 4, val: 8, severity: "monitor" },
    { id: "Simvastatin", group: 5, val: 12, severity: "safe" },
    { id: "Grapefruit Juice", group: 5, val: 6, severity: "monitor" },
    { id: "Clopidogrel", group: 1, val: 14, severity: "hospitalization" },
    { id: "Rivaroxaban", group: 1, val: 12, severity: "death" },
  ],
  links: [
    { source: "Warfarin", target: "Aspirin", value: 5, label: "Major Bleeding Risk" },
    { source: "Warfarin", target: "Clopidogrel", value: 4, label: "Severe Hemorrhage" },
    { source: "Lisinopril", target: "Ibuprofen", value: 3, label: "Renal Impairment" },
    { source: "Metformin", target: "Contrast Medium", value: 5, label: "Lactic Acidosis" },
    { source: "Amoxicillin", target: "Birth Control", value: 2, label: "Reduced Efficacy" },
    { source: "Simvastatin", target: "Grapefruit Juice", value: 3, label: "Myopathy Risk" },
    { source: "Warfarin", target: "Rivaroxaban", value: 5, label: "Critical Interaction" },
    { source: "Aspirin", target: "Ibuprofen", value: 2, label: "GI Irritation" },
  ]
}

export default function VisualizerPage() {
  const [filter, setFilter] = useState("")
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [windowLoaded, setWindowLoaded] = useState(false)
  const fgRef = useRef<any>()

  useEffect(() => {
    setWindowLoaded(true)
  }, [])

  const filteredData = useMemo(() => {
    if (!filter) return mockGraphData
    const nodes = mockGraphData.nodes.filter(n => n.id.toLowerCase().includes(filter.toLowerCase()))
    const nodeIds = new Set(nodes.map(n => n.id))
    const links = mockGraphData.links.filter(l => nodeIds.has(l.source as string) || nodeIds.has(l.target as string))
    return { nodes, links }
  }, [filter])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "death": return "#f43f5e"
      case "hospitalization": return "#f97316"
      case "monitor": return "#f59e0b"
      case "safe": return "#10b981"
      default: return "#94a3b8"
    }
  }

  const handleNodeClick = (node: any) => {
    setSelectedNode(node)
    // Center at node
    if (fgRef.current) {
        fgRef.current.centerAt(node.x, node.y, 1000)
        fgRef.current.zoom(3, 1000)
    }
  }

  return (
    <div className="flex h-[calc(100vh-160px)] flex-col space-y-6 fade-up">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Network className="text-sky-600" size={20} />
            <span className="text-xs font-black uppercase tracking-widest text-sky-600">Interactome Mapping</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Topological Drug Graph</h1>
          <p className="text-slate-500 font-medium">Interactive spatial relationships derived from SemanticFusionNet clusters.</p>
        </div>
        
        <div className="flex items-center gap-3">
           <div className="relative group">
              <Search className="absolute left-3 top-2.5 text-slate-400 group-focus-within:text-sky-600" size={16} />
              <input 
                type="text" 
                placeholder="Search interactome..." 
                className="w-64 rounded-xl border border-slate-100 bg-white py-2 pl-10 pr-4 text-sm outline-none shadow-sm focus:ring-4 focus:ring-sky-50 transition-all"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              />
           </div>
           <button className="flex h-10 w-10 items-center justify-center rounded-xl bg-white border border-slate-100 shadow-sm text-slate-500 hover:text-sky-600 transition-colors">
              <Maximize2 size={18} />
           </button>
        </div>
      </div>

      <div className="relative flex-1 rounded-3xl border border-slate-100 bg-slate-900/5 overflow-hidden shadow-inner">
        {/* Background Grid Accent */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
        
        {windowLoaded && (
          <ForceGraph2D
            ref={fgRef}
            graphData={filteredData}
            nodeLabel="id"
            nodeColor={node => getSeverityColor((node as any).severity)}
            nodeRelSize={6}
            linkColor={() => "rgba(51, 65, 85, 0.1)"}
            linkWidth={1.5}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.01}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.id
              const fontSize = 12 / globalScale
              ctx.font = `${fontSize}px Inter, sans-serif`
              const textWidth = ctx.measureText(label).width
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.5)

              ctx.fillStyle = getSeverityColor(node.severity)
              ctx.beginPath()
              ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false)
              ctx.fill()

              ctx.shadowColor = 'rgba(0,0,0,0.1)'
              ctx.shadowBlur = 10
              
              if (globalScale > 2) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
                ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2 - 8, bckgDimensions[0], bckgDimensions[1])
                ctx.textAlign = 'center'
                ctx.textBaseline = 'middle'
                ctx.fillStyle = '#0f172a'
                ctx.fillText(label, node.x, node.y - 8)
              }
            }}
            onNodeClick={handleNodeClick}
            backgroundColor="transparent"
          />
        )}

        {/* Floating Controls */}
        <div className="absolute bottom-6 left-6 flex flex-col gap-2">
           <button className="h-10 w-10 flex items-center justify-center rounded-xl bg-white shadow-xl border border-slate-100 text-slate-600 hover:text-sky-600" onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.5, 400)}>
              <ZoomIn size={18} />
           </button>
           <button className="h-10 w-10 flex items-center justify-center rounded-xl bg-white shadow-xl border border-slate-100 text-slate-600 hover:text-sky-600" onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.5, 400)}>
              <ZoomOut size={18} />
           </button>
        </div>

        {/* Node Detail Panel */}
        {selectedNode && (
          <div className="absolute right-6 top-6 w-80 animate-in slide-in-from-right duration-500">
             <Card className="shadow-2xl border-none overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: getSeverityColor(selectedNode.severity) }}></div>
                <CardHeader className="flex flex-row items-center justify-between pb-2 bg-slate-50/50">
                   <div className="flex flex-col">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Node Analysis</span>
                      <CardTitle className="text-xl">{selectedNode.id}</CardTitle>
                   </div>
                   <button onClick={() => setSelectedNode(null)} className="p-1 text-slate-400 hover:text-slate-900 transition-colors">
                      <ChevronRight size={20} />
                   </button>
                </CardHeader>
                <CardContent className="space-y-6 pt-4">
                   <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-500 uppercase">Interaction Risk</span>
                      <Badge variant={selectedNode.severity as any}>{selectedNode.severity}</Badge>
                   </div>
                   
                   <div className="space-y-3">
                      <h4 className="text-[10px] font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
                        <Activity size={12} /> Live Connections
                      </h4>
                      <div className="space-y-2">
                         {mockGraphData.links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id).map((link, i) => {
                            const otherId = link.source === selectedNode.id ? link.target : link.source
                            return (
                               <div key={i} className="flex items-center justify-between rounded-xl bg-slate-50 p-3 border border-slate-100 transition-all hover:border-sky-200">
                                  <div className="flex flex-col">
                                     <span className="text-xs font-bold text-slate-900">{otherId}</span>
                                     <span className="text-[10px] font-medium text-slate-500 leading-none mt-0.5">{link.label}</span>
                                  </div>
                                  <div className="h-2 w-2 rounded-full bg-sky-500"></div>
                               </div>
                            )
                         })}
                      </div>
                   </div>

                   <button className="w-full py-3 bg-slate-900 text-white rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition-all">
                      View Full interactome Study
                   </button>
                </CardContent>
             </Card>
          </div>
        )}

        {/* Legend Overlay */}
        <div className="absolute bottom-6 right-6">
           <div className="flex flex-wrap gap-4 bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-white shadow-xl shadow-slate-200/50">
              {[
                { label: "Death Risk", color: "#f43f5e" },
                { label: "Hospitalization", color: "#f97316" },
                { label: "Monitor", color: "#f59e0b" },
                { label: "Safe", color: "#10b981" }
              ].map(item => (
                <div key={item.label} className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-[10px] font-bold text-slate-600 uppercase tracking-[0.1em]">{item.label}</span>
                </div>
              ))}
           </div>
        </div>
      </div>
    </div>
  )
}
