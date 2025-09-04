import { useCallback } from "react"
import { Toast } from "@/components/ui/toast"

// Minimal utility: we won't implement full queue, just a simple window event
export function useToast() {
  const toast = useCallback((title: string, description?: string) => {
    const event = new CustomEvent("app_toast", { detail: { title, description }})
    window.dispatchEvent(event)
  }, [])
  return { toast }
}
