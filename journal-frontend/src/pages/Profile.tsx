import { useEffect, useMemo, useState } from "react"
import { useAuth } from "@/hooks/useAuth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/use-toast"
import { updateMe } from "@/services/api"

export default function Profile() {
  const { user, refresh } = useAuth() as any
  const { toast } = useToast()

  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  // Form state
  const [username, setUsername] = useState("")
  const [age, setAge] = useState<string>("")
  const [gender, setGender] = useState<string>("")

  useEffect(() => {
    if (!user) return
    setUsername(user.username ?? "")
    setAge(user.age != null ? String(user.age) : "")
    setGender(user.gender ?? "")
  }, [user])

  const initials = useMemo(
    () => (user?.username?.slice(0, 2)?.toUpperCase() || "U"),
    [user?.username]
  )

  if (!user) return null

  async function saveProfile() {
    setErr(null)
    if (!username.trim()) {
      setErr("Username cannot be empty.")
      return
    }
    const numAge = age.trim() === "" ? null : Number(age)
    if (numAge != null && (isNaN(numAge) || numAge < 10 || numAge > 120)) {
      setErr("Please enter a valid age between 10 and 120.")
      return
    }

    setSaving(true)
    try {
      const payload = {
        username: username.trim(),
        age: numAge,
        gender: gender || null,
      }

      await updateMe(payload)

      toast("Profile updated", "Your changes have been saved.")
      setEditing(false)

      if (typeof refresh === "function") {
        await refresh()
      }
    } catch (e: any) {
      setErr(e?.message || "Failed to save profile")
    } finally {
      setSaving(false)
    }
  }

  function cancelEdit() {
    setErr(null)
    setEditing(false)
    setUsername(user.username ?? "")
    setAge(user.age != null ? String(user.age) : "")
    setGender(user.gender ?? "")
  }

  const hasChanges =
    (user.username ?? "") !== username.trim() ||
    String(user.age ?? "") !== (age.trim() === "" ? "" : String(Number(age))) ||
    String(user.gender ?? "") !== String(gender ?? "")

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Profile card */}
      <Card className="border-muted shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Profile</CardTitle>
            <p className="text-sm text-muted-foreground">Manage your personal info</p>
          </div>
          {!editing ? (
            <Button variant="outline" onClick={() => setEditing(true)}>
              Edit
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button onClick={saveProfile} disabled={saving || !hasChanges}>
                {saving ? "Saving…" : "Save"}
              </Button>
              <Button variant="ghost" onClick={cancelEdit} disabled={saving}>
                Cancel
              </Button>
            </div>
          )}
        </CardHeader>

        <CardContent className="space-y-5">
          {/* Header row */}
          <div className="flex items-center gap-4">
            <Avatar className="h-14 w-14">
              <AvatarFallback className="text-base">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <div className="font-medium text-lg">{user.username}</div>
              <div className="text-sm text-muted-foreground">{user.email}</div>
            </div>
          </div>

          {/* Editable fields */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm text-muted-foreground">Username</label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your display name"
                disabled={!editing || saving}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm text-muted-foreground">Email</label>
              <Input value={user.email || ""} disabled />
              <p className="text-xs text-muted-foreground">
                Email changes are managed by support.
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm text-muted-foreground">Age</label>
              <Input
                type="number"
                min={10}
                max={120}
                value={editing ? age : user.age ?? ""}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g., 24"
                disabled={!editing || saving}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm text-muted-foreground">Gender</label>
              <select
                className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                value={editing ? gender : (user.gender ?? "")}
                onChange={(e) => setGender(e.target.value)}
                disabled={!editing || saving}
              >
                <option value="">Prefer not to say</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="non-binary">Non-binary</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {err && <p className="text-sm text-red-500">{err}</p>}
        </CardContent>
      </Card>

      {/* Streak card */}
      <Card className="border-muted shadow-sm">
        <CardHeader>
          <CardTitle>Streak</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="text-sm text-muted-foreground">
            Last entry: {user.last_entry_date || "—"}
          </div>
          <div className="text-2xl font-semibold">
            {user.current_streak || 0} day streak
          </div>
          <div className="text-sm text-muted-foreground">
            Longest: {user.longest_streak || 0} days
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
