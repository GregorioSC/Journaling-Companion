import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Sun, Moon } from "lucide-react"
import { useEffect, useState } from "react"

export function Topbar() {
  const { user, logout } = useAuth()
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const root = document.documentElement
    if (dark) root.classList.add("dark")
    else root.classList.remove("dark")
  }, [dark])

  return (
    <header className="flex h-14 items-center gap-3 border-b px-4">
      <div className="font-semibold">Welcome{user?.username ? `, ${user.username}` : ""}</div>
      <div className="ml-auto flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => setDark((d) => !d)}>
          {dark ? <Sun size={16}/> : <Moon size={16}/>}
        </Button>
        {user && <Button variant="outline" size="sm" onClick={logout}>Logout</Button>}
      </div>
    </header>
  )
}
