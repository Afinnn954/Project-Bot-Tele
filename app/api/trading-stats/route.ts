import { NextResponse } from "next/server"

// Fungsi untuk menghasilkan statistik trading yang realistis
function generateTradingStats() {
  // Jumlah total trades
  const totalTrades = Math.floor(Math.random() * 50) + 30

  // Win rate antara 55% dan 75%
  const winRate = 55 + Math.random() * 20

  // Hitung jumlah trades yang berhasil dan gagal
  const successfulTrades = Math.round(totalTrades * (winRate / 100))
  const failedTrades = totalTrades - successfulTrades

  // Hitung profit
  const averageTradeSize = 0.5 // BNB
  const averagePrice = 380 // USD
  const averageProfitPercent = 3 + Math.random() * 5 // 3-8%

  const totalValue = totalTrades * averageTradeSize * averagePrice
  const totalProfit = totalValue * (averageProfitPercent / 100)
  const averageProfit = totalProfit / totalTrades

  return {
    totalTrades,
    successfulTrades,
    failedTrades,
    winRate,
    totalProfit,
    averageProfit,
    // Tambahkan beberapa metadata tambahan
    profitFactor: 1.5 + Math.random() * 0.5,
    maxDrawdown: 5 + Math.random() * 10,
    sharpeRatio: 1.2 + Math.random() * 0.8,
    bestTrade: {
      symbol: "BNBUSDT",
      profit: 12 + Math.random() * 8,
      date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    },
    worstTrade: {
      symbol: "BNBUSDT",
      loss: 5 + Math.random() * 5,
      date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    },
  }
}

// Statistik trading yang dihasilkan
const mockStats = generateTradingStats()

export async function GET() {
  try {
    return NextResponse.json(mockStats)
  } catch (error) {
    console.error("Error fetching trading stats:", error)
    return NextResponse.json({ error: "Failed to fetch trading stats" }, { status: 500 })
  }
}
