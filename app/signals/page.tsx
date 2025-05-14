import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function SignalsPage() {
  return (
    <DashboardLayout>
      <DashboardHeader title="Sinyal Trading" description="Lihat dan analisis sinyal trading BNB" />
      <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
        <Tabs defaultValue="all">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="all">Semua Sinyal</TabsTrigger>
              <TabsTrigger value="buy">Buy</TabsTrigger>
              <TabsTrigger value="sell">Sell</TabsTrigger>
              <TabsTrigger value="neutral">Neutral</TabsTrigger>
            </TabsList>
          </div>
          <TabsContent value="all" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Semua Sinyal Trading</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Implementasi tabel sinyal trading akan ditampilkan di sini.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="buy" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Sinyal Buy</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Implementasi tabel sinyal buy akan ditampilkan di sini.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="sell" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Sinyal Sell</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Implementasi tabel sinyal sell akan ditampilkan di sini.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="neutral" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Sinyal Neutral</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Implementasi tabel sinyal neutral akan ditampilkan di sini.</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
