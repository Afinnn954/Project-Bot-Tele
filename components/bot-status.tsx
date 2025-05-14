"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useEffect, useState } from "react"
import { toast } from "@/components/ui/use-toast"

interface BotStatus {
  running: boolean
  lastAnalysis: string
  analysisInterval: number
  signalThreshold: number
  autoTrading: boolean
}

export function BotStatus() {
  const [status, setStatus] = useState<BotStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch("/api/bot-status")
        if (!response.ok) throw new Error("Failed to fetch bot status")
        const data = await response.json()
        setStatus(data)
        setLoading(false)
      } catch (error) {
        console.error("Error fetching bot status:", error)
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  const toggleAutoTrading = async () => {
    if (!status) return

    try {
      const response = await fetch("/api/toggle-auto-trading", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ enabled: !status.autoTrading }),
      })

      if (!response.ok) throw new Error("Failed to toggle auto trading")

      setStatus({
        ...status,
        autoTrading: !status.autoTrading,
      })

      toast({
        title: "Auto Trading",
        description: `Auto trading has been ${!status.autoTrading ? "enabled" : "disabled"}.`,
      })
    } catch (error) {
      console.error("Error toggling auto trading:", error)
      toast({
        title: "Error",
        description: "Failed to toggle auto trading.",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Status Bot</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-4 w-1/2 animate-pulse rounded-md bg-muted"></div>
            <div className="h-4 w-3/4 animate-pulse rounded-md bg-muted"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!status) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Status Bot</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Tidak dapat memuat status bot</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Status Bot</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Status:</span>
            <Badge variant={status.running ? "default" : "destructive"}>{status.running ? "Running" : "Stopped"}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Last Analysis:</span>
            <span className="text-sm">
              {status.lastAnalysis ? new Date(status.lastAnalysis).toLocaleString() : "Never"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Analysis Interval:</span>
            <span className="text-sm">{status.analysisInterval} minutes</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Signal Threshold:</span>
            <span className="text-sm">{status.signalThreshold}%</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex flex-col gap-1">
              <Label htmlFor="auto-trading">Auto Trading</Label>
              <span className="text-xs text-muted-foreground">
                {status.autoTrading ? "Trading otomatis diaktifkan" : "Trading otomatis dinonaktifkan"}
              </span>
            </div>
            <Switch id="auto-trading" checked={status.autoTrading} onCheckedChange={toggleAutoTrading} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
