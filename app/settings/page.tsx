"use client"

import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState } from "react"
import { toast } from "@/components/ui/use-toast"

export default function SettingsPage() {
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState({
    analysisInterval: "60",
    signalThreshold: "65",
    enableAutoTrading: false,
    telegramNotifications: true,
    binanceApiKey: "••••••••••••••••",
    binanceSecretKey: "••••••••••••••••",
    telegramBotToken: "••••••••••••••••",
    telegramChatId: "••••••••••••••••",
  })

  const handleSaveSettings = async () => {
    setLoading(true)

    try {
      // Simulasi API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      toast({
        title: "Settings saved",
        description: "Your settings have been saved successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save settings.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <DashboardHeader title="Pengaturan" description="Kelola pengaturan bot trading BNB Anda" />
      <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
        <Tabs defaultValue="general">
          <TabsList>
            <TabsTrigger value="general">Umum</TabsTrigger>
            <TabsTrigger value="api">API Keys</TabsTrigger>
            <TabsTrigger value="notifications">Notifikasi</TabsTrigger>
          </TabsList>
          <TabsContent value="general" className="mt-4 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Pengaturan Umum</CardTitle>
                <CardDescription>Kelola pengaturan umum bot trading BNB Anda</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="analysis-interval">Interval Analisis (menit)</Label>
                  <Input
                    id="analysis-interval"
                    value={settings.analysisInterval}
                    onChange={(e) => setSettings({ ...settings, analysisInterval: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signal-threshold">Threshold Sinyal (%)</Label>
                  <Input
                    id="signal-threshold"
                    value={settings.signalThreshold}
                    onChange={(e) => setSettings({ ...settings, signalThreshold: e.target.value })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="auto-trading">Auto Trading</Label>
                    <p className="text-sm text-muted-foreground">Aktifkan trading otomatis berdasarkan sinyal</p>
                  </div>
                  <Switch
                    id="auto-trading"
                    checked={settings.enableAutoTrading}
                    onCheckedChange={(checked) => setSettings({ ...settings, enableAutoTrading: checked })}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleSaveSettings} disabled={loading}>
                  {loading ? "Menyimpan..." : "Simpan Pengaturan"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          <TabsContent value="api" className="mt-4 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>Kelola API keys untuk koneksi dengan Binance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="binance-api-key">Binance API Key</Label>
                  <Input
                    id="binance-api-key"
                    value={settings.binanceApiKey}
                    onChange={(e) => setSettings({ ...settings, binanceApiKey: e.target.value })}
                    type="password"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="binance-secret-key">Binance Secret Key</Label>
                  <Input
                    id="binance-secret-key"
                    value={settings.binanceSecretKey}
                    onChange={(e) => setSettings({ ...settings, binanceSecretKey: e.target.value })}
                    type="password"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleSaveSettings} disabled={loading}>
                  {loading ? "Menyimpan..." : "Simpan API Keys"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          <TabsContent value="notifications" className="mt-4 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Pengaturan Notifikasi</CardTitle>
                <CardDescription>Kelola notifikasi Telegram untuk bot trading BNB Anda</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="telegram-notifications">Notifikasi Telegram</Label>
                    <p className="text-sm text-muted-foreground">Aktifkan notifikasi melalui Telegram</p>
                  </div>
                  <Switch
                    id="telegram-notifications"
                    checked={settings.telegramNotifications}
                    onCheckedChange={(checked) => setSettings({ ...settings, telegramNotifications: checked })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="telegram-bot-token">Telegram Bot Token</Label>
                  <Input
                    id="telegram-bot-token"
                    value={settings.telegramBotToken}
                    onChange={(e) => setSettings({ ...settings, telegramBotToken: e.target.value })}
                    type="password"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="telegram-chat-id">Telegram Chat ID</Label>
                  <Input
                    id="telegram-chat-id"
                    value={settings.telegramChatId}
                    onChange={(e) => setSettings({ ...settings, telegramChatId: e.target.value })}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleSaveSettings} disabled={loading}>
                  {loading ? "Menyimpan..." : "Simpan Pengaturan Notifikasi"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
