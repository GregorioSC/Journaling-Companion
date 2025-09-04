// src/App.tsx
import { Outlet } from "react-router-dom"
import { Sidebar } from "@/components/sidebar"
import { Topbar } from "@/components/topbar"
import { Toaster } from "@/components/toaster"
import { useAuth } from "@/hooks/useAuth"

export default function AppShell() {
  const { user } = useAuth()
  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex flex-1">
        {user && <Sidebar />}
        <main className="flex-1 flex flex-col">
          <Topbar />
          {/* grow pushes content down, so it fills screen height */}
          <div className="flex-1 p-4 md:p-6">
            <Outlet />
          </div>
        </main>
      </div>
      <Toaster />
    </div>
  )
}
