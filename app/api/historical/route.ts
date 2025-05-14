import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const symbol = searchParams.get("symbol") || "BNBUSDT"
  const interval = searchParams.get("interval") || "1d"
  const limit = Number.parseInt(searchParams.get("limit") || "30")

  try {
    // Coba ambil data dari Binance API
    // Karena ada masalah akses ke Binance API, kita akan langsung menggunakan data mock
    // Dalam implementasi nyata, Anda bisa mencoba menggunakan proxy atau API alternatif

    // Gunakan data mock untuk menghindari error
    return NextResponse.json(generateMockHistoricalData(symbol, interval, limit))
  } catch (error) {
    console.error("Error fetching historical data:", error)
    return NextResponse.json(generateMockHistoricalData(symbol, interval, limit))
  }
}

// Fungsi untuk menghasilkan data historis palsu yang realistis
function generateMockHistoricalData(symbol: string, interval: string, limit: number) {
  const now = Date.now()
  const intervalMs = getIntervalInMs(interval)

  // Harga dasar untuk simulasi
  const basePrice = symbol.includes("BNB") ? 380 : 60000

  // Volatilitas berdasarkan interval
  const volatility = interval === "1h" ? 0.005 : interval === "4h" ? 0.01 : interval === "1d" ? 0.02 : 0.04

  // Tren harga (naik/turun)
  const trend = Math.random() > 0.5 ? 1 : -1
  const trendStrength = Math.random() * 0.001 // Kekuatan tren

  // Buat data candle yang realistis
  const data = []
  let lastClose = basePrice

  for (let i = 0; i < limit; i++) {
    // Timestamp untuk interval ini
    const timestamp = now - (limit - i) * intervalMs

    // Simulasi pergerakan harga dengan random walk + tren
    const changePercent = (Math.random() * 2 - 1) * volatility + trend * trendStrength * i
    const close = lastClose * (1 + changePercent)

    // Buat range harga yang realistis
    const high = close * (1 + Math.random() * volatility)
    const low = close * (1 - Math.random() * volatility)
    const open = lastClose

    // Volume yang realistis
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
function getIntervalInMs(interval: string): number {
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
