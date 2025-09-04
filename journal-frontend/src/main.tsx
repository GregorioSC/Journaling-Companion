import React from "react"
import ReactDOM from "react-dom/client"
import { createBrowserRouter, RouterProvider, redirect } from "react-router-dom"
import AppShell from "./App"
import "./index.css"
import { AuthProvider, useAuth } from "@/hooks/useAuth"
import Login from "@/pages/Login"
import Register from "@/pages/Register"
import Dashboard from "@/pages/Dashboard"
import Profile from "@/pages/Profile"
import EntryDetails from "@/pages/EntryDetails"
import Analytics from "@/pages/Analytics"

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="p-6">Loading...</div>
  if (!user) {
    window.location.href = "/login"
    return null
  }
  return <>{children}</>
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { path: "/", loader: () => redirect("/dashboard") },
      { path: "/dashboard", element: <Protected><Dashboard /></Protected> },
      { path: "/entries/:id", element: <Protected><EntryDetails /></Protected> },
      { path: "/profile", element: <Protected><Profile /></Protected> },
      { path: "/analytics", element: <Protected><Analytics /></Protected> },
    ],
  },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
])

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>
)
