"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from "react"

interface TradingStats {
  totalTrades: number
  successfulTrades: number
  failedTrades: number
  winRate: number
  totalProfit: number
  averageProfit: number
}

export function TradingStats() {
  const [stats, setStats] = useState<TradingStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("/api/trading-stats")
        if (!response.ok) throw new Error("Failed to fetch trading stats")
        const data = await response.json()
        setStats(data)
        setLoading(false)
      } catch (error) {
        console.error("Error fetching trading stats:", error)
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Statistik Trading</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-4 w-3/4 animate-pulse rounded-md bg-muted"></div>
            <div className="h-4 w-1/2 animate-pulse rounded-md bg-muted"></div>
            <div className="h-4 w-2/3 animate-pulse rounded-md bg-muted"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!stats) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Statistik Trading</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Tidak ada data statistik</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Statistik Trading</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="space-y-2">
          <div className="flex justify-between">
            <dt className="text-sm font-medium text-muted-foreground">Total Trades</dt>
            <dd className="text-sm">{stats.totalTrades}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-sm font-medium text-muted-foreground">Win Rate</dt>
            <dd className="text-sm">{stats.winRate.toFixed(2)}%</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-sm font-medium text-muted-foreground">Total Profit</dt>
            <dd className={`text-sm ${stats.totalProfit >= 0 ? "text-green-500" : "text-red-500"}`}>
              ${stats.totalProfit.toFixed(2)}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-sm font-medium text-muted-foreground">Average Profit</dt>
            <dd className={`text-sm ${stats.averageProfit >= 0 ? "text-green-500" : "text-red-500"}`}>
              ${stats.averageProfit.toFixed(2)}
            </dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}
