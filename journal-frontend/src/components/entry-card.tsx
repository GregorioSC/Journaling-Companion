import { Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function EntryCard({ id, title, created_at, text }: { id: number, title: string, created_at: string, text: string }) {
  return (
    <Link to={`/entries/${id}`}>
      <Card className="hover:shadow-md transition-shadow h-full">
        <CardHeader>
          <CardTitle className="line-clamp-1">{title || "Untitled"}</CardTitle>
          <p className="text-xs text-muted-foreground">{new Date(created_at).toLocaleString()}</p>
        </CardHeader>
        <CardContent>
          <p className="text-sm line-clamp-3">{text}</p>
        </CardContent>
      </Card>
    </Link>
  )
}
