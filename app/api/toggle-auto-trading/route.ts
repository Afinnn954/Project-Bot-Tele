import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { enabled } = await request.json()

    // Dalam implementasi nyata, Anda akan mengubah konfigurasi bot yang sebenarnya
    console.log(`Auto trading ${enabled ? "enabled" : "disabled"}`)

    // Simulasi delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    return NextResponse.json({ success: true, autoTrading: enabled })
  } catch (error) {
    console.error("Error toggling auto trading:", error)
    return NextResponse.json({ error: "Failed to toggle auto trading" }, { status: 500 })
  }
}
