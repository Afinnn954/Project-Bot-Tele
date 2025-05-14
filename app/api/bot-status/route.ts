import { NextResponse } from "next/server"

// Ambil nilai dari environment variables
const analysisInterval = Number.parseInt(process.env.ANALYSIS_INTERVAL || "60")
const signalThreshold = Number.parseInt(process.env.SIGNAL_THRESHOLD || "65")
const enableAutoTrading = process.env.ENABLE_AUTO_TRADING === "true"

// Status bot (dalam implementasi nyata, ini akan berasal dari status bot yang sebenarnya)
const botStatus = {
  running: true,
  lastAnalysis: new Date(Date.now() - 1000 * 60 * Math.floor(Math.random() * 15)).toISOString(),
  analysisInterval,
  signalThreshold,
  autoTrading: enableAutoTrading,
  // Tambahkan beberapa metadata tambahan
  version: "1.0.0",
  uptime: Math.floor(Math.random() * 24 * 60) + " minutes",
  activeSymbols: ["BNBUSDT", "BTCUSDT"],
  lastSignal: Math.random() > 0.5 ? "BUY" : "SELL",
  lastSignalConfidence: Math.floor(Math.random() * 30) + 65,
}

export async function GET() {
  try {
    return NextResponse.json(botStatus)
  } catch (error) {
    console.error("Error fetching bot status:", error)
    return NextResponse.json({ error: "Failed to fetch bot status" }, { status: 500 })
  }
}
