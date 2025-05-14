import type React from "react"
import { DashboardSidebar } from "./dashboard-sidebar"
import { SidebarInset } from "./ui/sidebar"

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <DashboardSidebar />
      <SidebarInset>
        <div className="flex flex-col">{children}</div>
      </SidebarInset>
    </div>
  )
}
