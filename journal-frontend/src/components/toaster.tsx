import React, { useEffect, useState } from "react"
import { ToastProvider, ToastViewport, Toast, ToastTitle, ToastDescription, ToastClose } from "@/components/ui/toast"

type Item = { id: number; title: string; description?: string }

export function Toaster() {
  const [items, setItems] = useState<Item[]>([])

  useEffect(() => {
    let id = 1
    const handler = (e: any) => {
      setItems((prev) => [...prev, { id: id++, ...e.detail }])
      setTimeout(() => {
        setItems((prev) => prev.slice(1))
      }, 3500)
    }
    window.addEventListener("app_toast", handler as any)
    return () => window.removeEventListener("app_toast", handler as any)
  }, [])

  return (
    <ToastProvider swipeDirection="right">
      <ToastViewport />
      <div className="fixed right-4 bottom-4 space-y-2 z-[101]">
        {items.map((it) => (
          <Toast key={it.id}>
            <div className="grid gap-1">
              <ToastTitle>{it.title}</ToastTitle>
              {it.description && <ToastDescription>{it.description}</ToastDescription>}
            </div>
            <ToastClose />
          </Toast>
        ))}
      </div>
    </ToastProvider>
  )
}
