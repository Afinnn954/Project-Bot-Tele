import { type NextRequest, NextResponse } from "next/server"

// Fungsi untuk menghasilkan sinyal trading yang realistis
function generateSignals(count: number, type?: string) {
  const signals = []
  const now = Date.now()

  for (let i = 0; i < count; i++) {
    // Tentukan tipe sinyal
    let signalType = type
    if (!signalType) {
      const rand = Math.random()
      signalType = rand > 0.6 ? "BUY" : rand > 0.2 ? "SELL" : "NEUTRAL"
    }

    // Tentukan confidence berdasarkan tipe
    let confidence = 0
    if (signalType === "BUY" || signalType === "SELL") {
      confidence = Math.floor(Math.random() * 30) + 60 // 60-90%
    } else {
      confidence = Math.floor(Math.random() * 20) + 40 // 40-60%
    }

    // Harga BNB yang realistis
    const price = 370 + Math.random() * 30

    // Timestamp yang realistis (dalam 24 jam terakhir)
    const timestamp = new Date(now - Math.random() * 24 * 60 * 60 * 1000).toISOString()

    signals.push({
      id: `signal-${i + 1}`,
      timestamp,
      symbol: "BNBUSDT",
      type: signalType,
      price,
      confidence,
      // Tambahkan beberapa metadata tambahan
      source: Math.random() > 0.5 ? "Technical Analysis" : "AI Prediction",
      indicators: {
        rsi: Math.floor(Math.random() * 100),
        macd: Math.random() > 0.5 ? "bullish" : "bearish",
        ma: Math.random() > 0.5 ? "above" : "below",
      },
    })
  }

  // Urutkan berdasarkan timestamp (terbaru dulu)
  return signals.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const limit = Number.parseInt(searchParams.get("limit") || "10")
  const type = searchParams.get("type") || undefined

  try {
    // Hasilkan sinyal palsu
    const signals = generateSignals(limit, type)
    return NextResponse.json(signals)
  } catch (error) {
    console.error("Error fetching signals:", error)
    return NextResponse.json({ error: "Failed to fetch signals" }, { status: 500 })
  }
}
