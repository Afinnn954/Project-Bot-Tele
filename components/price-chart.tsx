"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from "react"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface PriceData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface PriceChartProps {
  symbol: string
}

export function PriceChart({ symbol }: PriceChartProps) {
  const [data, setData] = useState<PriceData[]>([])
  const [timeframe, setTimeframe] = useState<string>("1d")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPriceData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`/api/historical?symbol=${symbol}&interval=${timeframe}`)

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`)
        }

        const data = await response.json()

        if (!Array.isArray(data)) {
          throw new Error("Invalid data format received")
        }

        setData(data)
      } catch (error) {
        console.error("Error fetching price data:", error)
        setError("Failed to load chart data. Using fallback data.")

        // Gunakan data fallback jika terjadi error
        const fallbackData = generateFallbackData(symbol, timeframe)
        setData(fallbackData)
      } finally {
        setLoading(false)
      }
    }

    fetchPriceData()
  }, [symbol, timeframe])

  // Fungsi untuk menghasilkan data fallback jika terjadi error
  const generateFallbackData = (symbol: string, interval: string): PriceData[] => {
    const now = Date.now()
    const intervalMs = getIntervalInMs(interval)
    const limit = 30

    const basePrice = symbol.includes("BNB") ? 380 : 60000
    const volatility = 0.02

    const data: PriceData[] = []
    let lastClose = basePrice

    for (let i = 0; i < limit; i++) {
      const timestamp = now - (limit - i) * intervalMs
      const changePercent = (Math.random() * 2 - 1) * volatility
      const close = lastClose * (1 + changePercent)
      const high = close * (1 + Math.random() * volatility)
      const low = close * (1 - Math.random() * volatility)
      const open = lastClose
      const volume = basePrice * 10 * (0.8 + Math.random() * 0.4)

      data.push({
        timestamp,
        open,
        high,
        low,
        close,
        volume,
      })

      lastClose = close
    }

    return data
  }

  // Fungsi untuk mengkonversi interval ke milidetik
  const getIntervalInMs = (interval: string): number => {
    const unit = interval.charAt(interval.length - 1)
    const value = Number.parseInt(interval.substring(0, interval.length - 1))

    switch (unit) {
      case "h":
        return value * 60 * 60 * 1000 // jam
      case "d":
        return value * 24 * 60 * 60 * 1000 // hari
      case "w":
        return value * 7 * 24 * 60 * 60 * 1000 // minggu
      default:
        return value * 60 * 1000 // menit (default)
    }
  }

  // Format timestamp untuk label pada sumbu X
  const formatXAxis = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" })
  }

  // Format harga untuk tooltip
  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded p-2 shadow-md text-sm">
          <p className="font-medium">{new Date(label).toLocaleDateString()}</p>
          <p className="text-primary">Open: ${data.open.toFixed(2)}</p>
          <p className="text-green-500">High: ${data.high.toFixed(2)}</p>
          <p className="text-red-500">Low: ${data.low.toFixed(2)}</p>
          <p className="text-primary font-medium">Close: ${data.close.toFixed(2)}</p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="col-span-3">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">{symbol} Chart</CardTitle>
          <Tabs defaultValue="1d" value={timeframe} onValueChange={setTimeframe}>
            <TabsList>
              <TabsTrigger value="1h">1H</TabsTrigger>
              <TabsTrigger value="4h">4H</TabsTrigger>
              <TabsTrigger value="1d">1D</TabsTrigger>
              <TabsTrigger value="1w">1W</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex h-[350px] items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
          </div>
        ) : error ? (
          <div className="flex h-[350px] flex-col items-center justify-center text-muted-foreground">
            <p className="text-yellow-500 mb-2">{error}</p>
            {data.length > 0 && (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                  <XAxis dataKey="timestamp" tickFormatter={formatXAxis} />
                  <YAxis domain={["auto", "auto"]} tickFormatter={formatPrice} />
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="close" stroke="#3b82f6" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={data}>
              <XAxis dataKey="timestamp" tickFormatter={formatXAxis} />
              <YAxis domain={["auto", "auto"]} tickFormatter={formatPrice} />
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="close" stroke="#3b82f6" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
