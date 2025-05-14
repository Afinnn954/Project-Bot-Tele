"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowDown, ArrowUp, RefreshCw } from "lucide-react"

export function BnbPredictor() {
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchPrediction = async () => {
    setLoading(true)
    try {
      const response = await fetch("/api/bnb-trading")
      const data = await response.json()
      setPrediction(data.data)
      setLastUpdated(new Date())
    } catch (error) {
      console.error("Error fetching prediction:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPrediction()

    // Refresh prediction every 5 minutes
    const interval = setInterval(fetchPrediction, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const executeTrade = async (orderType: string) => {
    try {
      const response = await fetch("/api/bnb-trading", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          orderType,
          amount: 0.5, // This would come from user settings in a real app
        }),
      })

      const result = await response.json()

      // Send notification to Telegram
      await fetch("/api/telegram-notify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: `${orderType} order executed for 0.5 BNB at $${prediction?.currentPrice}`,
        }),
      })

      alert(`${orderType} order executed successfully!`)
    } catch (error) {
      console.error("Error executing trade:", error)
      alert("Failed to execute trade. Please try again.")
    }
  }

  if (!prediction) {
    return (
      <Card className="bg-slate-900 text-white border-slate-800">
        <CardContent className="pt-6">
          <div className="flex justify-center">
            <RefreshCw className="h-8 w-8 animate-spin text-yellow-400" />
          </div>
          <p className="mt-4 text-center text-slate-400">Loading prediction data...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-slate-900 text-white border-slate-800">
      <CardHeader>
        <CardTitle>BNB Prediction</CardTitle>
        <CardDescription className="text-slate-400">
          {lastUpdated ? `Last updated: ${lastUpdated.toLocaleTimeString()}` : "Updating..."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-lg bg-slate-800 p-4">
          <div className="mb-2 text-sm text-slate-400">Current Signal</div>
          <div className="flex items-center gap-2">
            {prediction.prediction === "BUY" ? (
              <ArrowUp className="h-5 w-5 text-green-500" />
            ) : (
              <ArrowDown className="h-5 w-5 text-red-500" />
            )}
            <span
              className={`text-xl font-bold ${prediction.prediction === "BUY" ? "text-green-500" : "text-red-500"}`}
            >
              {prediction.prediction}
            </span>
            <span className="ml-2 rounded bg-slate-700 px-2 py-1 text-xs">
              {Math.round(prediction.confidence * 100)}% confidence
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-slate-800 p-4">
            <div className="mb-1 text-sm text-slate-400">Price Target</div>
            <div className="text-lg font-semibold text-yellow-400">${prediction.nextPriceTarget}</div>
          </div>
          <div className="rounded-lg bg-slate-800 p-4">
            <div className="mb-1 text-sm text-slate-400">Stop Loss</div>
            <div className="text-lg font-semibold text-red-400">${prediction.stopLoss}</div>
          </div>
        </div>

        <div className="rounded-lg bg-slate-800 p-4">
          <div className="mb-2 text-sm text-slate-400">Technical Indicators</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-slate-400">RSI:</span> {prediction.indicators.rsi}
            </div>
            <div>
              <span className="text-slate-400">MACD:</span> {prediction.indicators.macd}
            </div>
            <div>
              <span className="text-slate-400">MA:</span> {prediction.indicators.movingAverages}
            </div>
            <div>
              <span className="text-slate-400">Volume:</span> {prediction.indicators.volume}
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button className="flex-1 bg-green-600 hover:bg-green-700" onClick={() => executeTrade("BUY")}>
          <ArrowUp className="mr-2 h-4 w-4" />
          Buy BNB
        </Button>
        <Button className="flex-1 bg-red-600 hover:bg-red-700" onClick={() => executeTrade("SELL")}>
          <ArrowDown className="mr-2 h-4 w-4" />
          Sell BNB
        </Button>
      </CardFooter>
    </Card>
  )
}
