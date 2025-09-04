import { useEffect, useState } from "react"
import { getMyEntries, getInsightByEntry, type Entry, getWeeklySummary, type WeeklySummary } from "@/services/api"
import { SentimentChart } from "@/components/sentiment-chart"
import { ActivityHeatmap } from "@/components/activity-heatmap"

export default function Analytics() {
  const [data, setData] = useState<{ date: string; sentiment: number }[]>([])
  const [heat, setHeat] = useState<{ date: string; count: number }[]>([])
  const [summary, setSummary] = useState<WeeklySummary | null>(null)
  const [sumErr, setSumErr] = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      const entries = await getMyEntries()

      // Heatmap data: count entries per day
      const byDate = new Map<string, number>()
      entries.forEach((e: Entry) => {
        const d = new Date(e.created_at)
        const key = new Date(d.getFullYear(), d.getMonth(), d.getDate()).toISOString()
        byDate.set(key, (byDate.get(key) || 0) + 1)
      })
      setHeat(Array.from(byDate.entries()).map(([date, count]) => ({ date, count })))

      // Sentiment series
      const enriched = await Promise.all(
        entries.map(async (e: Entry) => {
          try {
            const ins = await getInsightByEntry(e.id)
            return { date: new Date(e.created_at).toLocaleDateString(), sentiment: ins.sentiment }
          } catch {
            return null
          }
        })
      )
      setData(enriched.filter(Boolean) as any)

      // Weekly summary (AI)
      try {
        const s = await getWeeklySummary()
        setSummary(s)
      } catch (err: any) {
        setSumErr(err?.message || "Failed to load weekly summary")
      }
    })()
  }, [])

  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Sentiment over time</h2>
        <SentimentChart data={data} />
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Activity (last ~12 weeks)</h2>
        <ActivityHeatmap days={heat} />
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Weekly Summary</h2>
        {sumErr && <p className="text-sm text-red-500">{sumErr}</p>}
        {!summary && !sumErr && <p className="text-sm text-muted-foreground">Loading…</p>}
        {summary && (
          <div className="rounded-lg border p-4">
            <p className="text-xs text-muted-foreground mb-2">{summary.week_start}</p>
            <pre className="whitespace-pre-wrap text-sm">{summary.summary}</pre>
          </div>
        )}
      </section>
    </div>
  )
}
