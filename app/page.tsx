import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardLayout } from "@/components/dashboard-layout"
import { PriceCard } from "@/components/price-card"
import { PriceChart } from "@/components/price-chart"
import { SignalsTable } from "@/components/signals-table"
import { TradingStats } from "@/components/trading-stats"
import { BotStatus } from "@/components/bot-status"
import { BnbPredictor } from "@/components/bnb-predictor"

export default function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardHeader title="Dashboard" description="Pantau performa trading BNB Anda" />
      <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <PriceCard symbol="BNBUSDT" />
          <PriceCard symbol="BTCUSDT" />
          <TradingStats />
          <BotStatus />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <PriceChart symbol="BNBUSDT" />
          <div className="space-y-4 lg:col-span-2">
            <BnbPredictor />
            <h2 className="text-lg font-semibold mt-4">Sinyal Terbaru</h2>
            <SignalsTable />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
