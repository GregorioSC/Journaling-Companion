import { useState } from "react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function Register() {
  const { register } = useAuth()
  const [form, setForm] = useState({ username: "", email: "", password: "", age: 18, gender: "unspecified" })
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null)
    try {
      await register(form)
      setMsg("Registered! You can now login.")
    } catch (e: any) {
      setErr(e?.response?.data?.detail || "Registration failed")
    }
  }
  return (
    <div className="grid min-h-screen place-items-center p-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4 rounded-lg border p-6">
        <h1 className="text-2xl font-semibold">Create account</h1>
        {err && <div className="text-sm text-red-600">{err}</div>}
        {msg && <div className="text-sm text-green-600">{msg}</div>}
        <div className="space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input id="username" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required />
        </div>
        <div className="flex gap-3">
          <div className="space-y-2 flex-1">
            <Label htmlFor="age">Age</Label>
            <Input id="age" type="number" value={form.age} onChange={(e) => setForm({...form, age: Number(e.target.value)})} required />
          </div>
          <div className="space-y-2 flex-1">
            <Label htmlFor="gender">Gender</Label>
            <Input id="gender" value={form.gender} onChange={(e) => setForm({...form, gender: e.target.value})} />
          </div>
        </div>
        <Button className="w-full" type="submit">Register</Button>
        <p className="text-sm text-muted-foreground">Have an account? <a className="underline" href="/login">Login</a></p>
      </form>
    </div>
  )
}
