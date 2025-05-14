"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from "react"
import { ArrowDown, ArrowUp } from "lucide-react"

interface PriceCardProps {
  symbol: string
}

export function PriceCard({ symbol }: PriceCardProps) {
  const [price, setPrice] = useState<number | null>(null)
  const [previousPrice, setPreviousPrice] = useState<number | null>(null)
  const [change, setChange] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Fungsi untuk mendapatkan harga dari API
    const fetchPrice = async () => {
      try {
        setError(null)
        const response = await fetch(`/api/price?symbol=${symbol}`)

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`)
        }

        const data = await response.json()

        setPreviousPrice(price)
        setPrice(Number.parseFloat(data.price))
        setLoading(false)

        if (previousPrice && price) {
          const changePercent = ((price - previousPrice) / previousPrice) * 100
          setChange(changePercent)
        }
      } catch (error) {
        console.error("Error fetching price:", error)
        setError("Failed to fetch price")
        setLoading(false)
      }
    }

    // Panggil fetchPrice setiap 10 detik
    fetchPrice()
    const interval = setInterval(fetchPrice, 10000)

    return () => clearInterval(interval)
  }, [symbol, price, previousPrice])

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{symbol} Price</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-9 w-24 animate-pulse rounded-md bg-muted"></div>
        ) : error ? (
          <div className="text-sm text-red-500">{error}</div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="text-2xl font-bold">${price?.toFixed(2)}</div>
            {change !== 0 && (
              <div className={`flex items-center text-xs ${change > 0 ? "text-green-500" : "text-red-500"}`}>
                {change > 0 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                {Math.abs(change).toFixed(2)}%
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
