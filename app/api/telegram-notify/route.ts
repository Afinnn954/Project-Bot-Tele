import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const body = await request.json()

    // Dalam implementasi nyata, ini akan mengirim notifikasi ke Telegram
    // menggunakan Telegram Bot API

    console.log("Sending Telegram notification:", body.message)

    return NextResponse.json({
      status: "success",
      message: "Notification sent to Telegram",
    })
  } catch (error) {
    return NextResponse.json({ status: "error", message: "Failed to send Telegram notification" }, { status: 400 })
  }
}
