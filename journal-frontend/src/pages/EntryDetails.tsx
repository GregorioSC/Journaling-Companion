import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import {
  deleteEntry,
  getEntry,
  getInsightByEntry,
  patchEntry,
  type Entry,
  type Insight,
  analyzeEntryAI,
  getAIPrompts,
  type PromptResponse,
} from "@/services/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/components/use-toast"

export default function EntryDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()

  const [entry, setEntry] = useState<Entry | null>(null)
  const [insight, setInsight] = useState<Insight | null>(null)
  const [title, setTitle] = useState("")
  const [text, setText] = useState("")
  const [aiBusy, setAiBusy] = useState(false)
  const [aiErr, setAiErr] = useState<string | null>(null)
  const [aiPrompts, setAiPrompts] = useState<string[]>([])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    (async () => {
      if (!id) return
      const e = await getEntry(Number(id))
      setEntry(e)
      setTitle(e.title)
      setText(e.text)
      // try to load existing insight (will 404 if none yet)
      try {
        const ins = await getInsightByEntry(e.id)
        setInsight(ins)
      } catch {
        setInsight(null)
      }
    })()
  }, [id])

  async function onSave(e: React.FormEvent) {
    e.preventDefault()
    if (!entry) return
    if (!title.trim() || !text.trim()) return
    try {
      setSaving(true)
      const updated = await patchEntry(entry.id, { title, text })
      setEntry(updated)
      toast("Saved", "Your changes have been saved.")
      navigate("/dashboard")
    } catch (err: any) {
      toast("Save failed", err?.message || "Could not save entry")
    } finally {
      setSaving(false)
    }
  }

  async function onDelete() {
    if (!entry) return
    await deleteEntry(entry.id)
    toast("Deleted", "Entry removed.")
    navigate("/dashboard")
  }

  async function handleAnalyze() {
    if (!entry) return
    try {
      setAiErr(null)
      setAiBusy(true)
      await analyzeEntryAI(entry.id) // creates/updates the insight row
      const refreshed = await getInsightByEntry(entry.id)
      setInsight(refreshed)
      toast("Analyzed!", `Sentiment: ${refreshed.sentiment.toFixed(2)}`)
    } catch (e: any) {
      setAiErr(e?.message || "AI analysis failed")
      toast("AI failed", e?.message || "Could not analyze entry")
    } finally {
      setAiBusy(false)
    }
  }

  async function handleAskAI() {
    try {
      setAiErr(null)
      setAiBusy(true)
      const res: PromptResponse = await getAIPrompts("reflect on this entry", 5)
      setAiPrompts(res.prompts ?? [])
    } catch (e: any) {
      setAiErr(e?.message || "Failed to fetch prompts")
      toast("AI failed", e?.message || "Could not fetch prompts")
    } finally {
      setAiBusy(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <section className="lg:col-span-2 rounded-lg border p-4">
        <form onSubmit={onSave} className="space-y-3">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Entry title"
          />
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Write your thoughts..."
          />
          <div className="flex gap-2">
            <Button
              type="submit"
              disabled={saving || !title.trim() || !text.trim()}   // block empty title or text
            >
              {saving ? "Saving..." : "Save"}
            </Button>
            <Button type="button" variant="destructive" onClick={onDelete}>
              Delete
            </Button>
          </div>
        </form>
      </section>

      <aside className="space-y-4">
        <div className="rounded-lg border p-4">
          <h3 className="font-semibold mb-2">Insights</h3>
          {!insight && (
            <p className="text-sm text-muted-foreground">
              No insight yet. Click <b>Analyze with AI</b> to generate one.
            </p>
          )}
          {insight && (
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted-foreground">Sentiment:</span>{" "}
                <b>{insight.sentiment.toFixed(2)}</b>
              </div>
              <div className="flex flex-wrap gap-2">
                {insight.themes?.map((t, i) => (
                  <Badge key={i}>{t}</Badge>
                ))}
              </div>
              <p className="text-muted-foreground">
                Created at: {new Date(insight.created_at).toLocaleString()}
              </p>
            </div>
          )}
          <div className="flex items-center gap-2 mt-3">
            <Button variant="outline" onClick={handleAskAI} disabled={aiBusy}>
              {aiBusy ? "Thinking..." : "Ask AI"}
            </Button>
          </div>
          {aiErr && <p className="text-xs text-red-500 mt-2">{aiErr}</p>}
          {aiPrompts.length > 0 && (
            <ul className="grid gap-2 mt-3">
              {aiPrompts.map((p, i) => (
                <li key={i} className="text-sm rounded-md px-3 py-2 bg-muted">
                  {p}
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>
    </div>
  )
}
