"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useEffect, useState } from "react"

interface Signal {
  id: string
  timestamp: string
  symbol: string
  type: string
  price: number
  confidence: number
}

export function SignalsTable() {
  const [signals, setSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSignals = async () => {
      try {
        const response = await fetch("/api/signals?limit=10")
        if (!response.ok) throw new Error("Failed to fetch signals")
        const data = await response.json()
        setSignals(data)
        setLoading(false)
      } catch (error) {
        console.error("Error fetching signals:", error)
        setLoading(false)
      }
    }

    fetchSignals()
  }, [])

  const getSignalBadge = (type: string) => {
    switch (type.toLowerCase()) {
      case "buy":
        return <Badge className="bg-green-500">BUY</Badge>
      case "sell":
        return <Badge className="bg-red-500">SELL</Badge>
      case "neutral":
        return <Badge variant="outline">NEUTRAL</Badge>
      default:
        return <Badge variant="secondary">{type}</Badge>
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-500"
    if (confidence >= 60) return "text-yellow-500"
    return "text-red-500"
  }

  if (loading) {
    return (
      <div className="flex h-[300px] items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading signals...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Waktu</TableHead>
            <TableHead>Symbol</TableHead>
            <TableHead>Tipe</TableHead>
            <TableHead className="text-right">Harga</TableHead>
            <TableHead className="text-right">Confidence</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {signals.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center">
                Tidak ada sinyal trading terbaru
              </TableCell>
            </TableRow>
          ) : (
            signals.map((signal) => (
              <TableRow key={signal.id}>
                <TableCell>{new Date(signal.timestamp).toLocaleString()}</TableCell>
                <TableCell>{signal.symbol}</TableCell>
                <TableCell>{getSignalBadge(signal.type)}</TableCell>
                <TableCell className="text-right">${signal.price.toFixed(2)}</TableCell>
                <TableCell className={`text-right ${getConfidenceColor(signal.confidence)}`}>
                  {signal.confidence}%
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
