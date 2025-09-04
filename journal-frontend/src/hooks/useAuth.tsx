import { createContext, useContext, useEffect, useState } from "react"
import { getMe, login as apiLogin, registerUser, type User } from "@/services/api"

type AuthCtx = {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (p: {username: string, email: string, password: string, age: number, gender: string}) => Promise<void>
  logout: () => void
}

const Ctx = createContext<AuthCtx | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function boot() {
      try {
        const me = await getMe()
        setUser(me)
      } catch {}
      setLoading(false)
    }
    boot()
  }, [])

  async function login(email: string, password: string) {
    await apiLogin(email, password)
    const me = await getMe()
    setUser(me)
  }

  async function register(p: {username: string, email: string, password: string, age: number, gender: string}) {
    await registerUser(p)
  }

  function logout() {
    localStorage.removeItem("token")
    setUser(null)
    window.location.href = "/login"
  }

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
