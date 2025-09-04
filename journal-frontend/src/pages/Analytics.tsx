import { useEffect, useMemo, useState } from "react"
import {
  getMyEntries,
  getInsightByEntry,
  type Entry,
  getWeeklySummary,
  type WeeklySummary,
} from "@/services/api"
import { SentimentChart } from "@/components/sentiment-chart"
import { ActivityHeatmap } from "@/components/activity-heatmap"
import { Badge } from "@/components/ui/badge"

export default function Analytics() {
  const [data, setData] = useState<{ date: string; sentiment: number }[]>([])
  const [heat, setHeat] = useState<{ date: string; count: number }[]>([])
  const [summary, setSummary] = useState<WeeklySummary | null>(null)
  const [sumErr, setSumErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ; (async () => {
      try {
        setLoading(true)
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
              return {
                date: new Date(e.created_at).toLocaleDateString(),
                sentiment: ins.sentiment,
              }
            } catch {
              return null
            }
          })
        )
        setData((enriched.filter(Boolean) as any) ?? [])

        // Weekly summary
        try {
          const s = await getWeeklySummary()
          setSummary(s)
        } catch (err: any) {
          setSumErr(err?.message || "Failed to load weekly summary")
        }
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const weekRange = useMemo(() => {
    if (!summary?.week_start) return ""
    const start = new Date(summary.week_start)
    const end = new Date(start)
    end.setDate(start.getDate() + 6)
    const fmt = (d: Date) =>
      d.toLocaleDateString(undefined, { month: "short", day: "numeric" })
    return `${fmt(start)} – ${fmt(end)}`
  }, [summary?.week_start])

  return (
    <div className="space-y-8">
      {/* Sentiment trend */}
      <section className="space-y-2">
        <div>
          <h2 className="text-lg font-semibold">Sentiment over time</h2>
          <p className="text-sm text-muted-foreground">
            Higher (closer to +1) generally means happier; lower (closer to −1) leans sadder.
          </p>
        </div>
        <div className="rounded-lg border p-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading chart…</p>
          ) : data.length ? (
            <SentimentChart data={data} />
          ) : (
            <p className="text-sm text-muted-foreground">No sentiment data yet.</p>
          )}
        </div>
      </section>

      {/* Activity */}
      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Activity (last ~12 weeks)</h2>
        <div className="rounded-lg border p-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading activity…</p>
          ) : (
            <ActivityHeatmap days={heat} />
          )}
        </div>
      </section>

      {/* Weekly Summary */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Weekly reflection</h2>
            <p className="text-sm text-muted-foreground">{weekRange || "This week"}</p>
          </div>

          {/* Sentiment chip */}
          {summary && (
            <div
              className="rounded-full px-3 py-1 text-sm font-medium"
              style={{
                background:
                  (summary.insights.avg_sentiment ?? 0) >= 0
                    ? "rgba(16,185,129,0.12)" // emerald
                    : "rgba(239,68,68,0.12)", // red
                color:
                  (summary.insights.avg_sentiment ?? 0) >= 0
                    ? "rgb(5,150,105)"
                    : "rgb(220,38,38)",
              }}
              title="Average sentiment (−1 to +1)"
            >
              {(summary.insights.avg_sentiment ?? 0).toFixed(2)}
            </div>
          )}
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm space-y-4">
          {/* Error/loading */}
          {sumErr && <p className="text-sm text-red-500">{sumErr}</p>}
          {!sumErr && !summary && (
            <p className="text-sm text-muted-foreground">Loading summary…</p>
          )}

          {/* Narrative */}
          {summary && (
            <div className="space-y-3 text-base leading-relaxed text-foreground">
              <p>
                🌱{" "}
                {summary.insights.avg_sentiment >= 0
                  ? "This week generally felt positive — nice work staying grounded."
                  : "This week felt a bit heavier — thanks for showing up anyway."}
              </p>

              {summary.insights.themes?.length ? (
                <div>
                  <p className="mb-2">✨ Recurring themes:</p>
                  <div className="flex flex-wrap gap-2">
                    {summary.insights.themes.map((t: string, i: number) => (
                      <Badge
                        key={i}
                        className="px-3 py-1 rounded-full bg-muted text-sm font-medium text-muted-foreground"
                      >
                        {t}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}

              <p>📝 You logged {summary.insights.count} entries. That consistency matters.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
