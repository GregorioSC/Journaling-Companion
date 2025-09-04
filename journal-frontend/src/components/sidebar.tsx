import { NavLink } from "react-router-dom"
import { cn } from "@/utils/cn"
import { BookOpen, BarChart3, User2 } from "lucide-react"

export function Sidebar() {
  const link = "flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground"
  const active = "bg-accent text-accent-foreground"
  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 flex-col border-r p-4">
      <div className="text-lg font-semibold px-2 py-2">Journaling</div>
      <nav className="mt-4 grid gap-1">
        <NavLink to="/dashboard" className={({isActive}) => cn(link, isActive && active)}><BookOpen size={18}/>Dashboard</NavLink>
        <NavLink to="/profile" className={({isActive}) => cn(link, isActive && active)}><User2 size={18}/>Profile</NavLink>
        <NavLink to="/analytics" className={({isActive}) => cn(link, isActive && active)}><BarChart3 size={18}/>Analytics</NavLink>
      </nav>
      <div className="mt-auto px-2 text-xs text-muted-foreground">Private & local-first UI</div>
    </aside>
  )
}
