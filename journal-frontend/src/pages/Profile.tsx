import { useAuth } from "@/hooks/useAuth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export default function Profile() {
  const { user } = useAuth()
  if (!user) return null
  const initials = user.username?.slice(0,2)?.toUpperCase() || "U"
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-4">
          <Avatar><AvatarFallback>{initials}</AvatarFallback></Avatar>
          <div>
            <div className="font-medium">{user.username}</div>
            <div className="text-sm text-muted-foreground">{user.email}</div>
            <div className="text-sm text-muted-foreground">Age: {user.age} • Gender: {user.gender}</div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Streak</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">Last entry: {user.last_entry_date || "—"}</div>
          <div className="text-2xl font-semibold mt-2">{user.current_streak || 0} day streak</div>
          <div className="text-sm text-muted-foreground">Longest: {user.longest_streak || 0} days</div>
        </CardContent>
      </Card>
    </div>
  )
}
