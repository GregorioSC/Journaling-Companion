import { useEffect, useMemo, useState, useCallback } from "react"
import { useAuth } from "@/hooks/useAuth"
import {
  createEntry,
  getMyEntries,
  getMe,
  type Entry,
  type User,
  getAIPrompts,
  type PromptResponse,
  getWeeklySummary,
  type WeeklySummary,
  analyzeEntryAI,
} from "@/services/api"
import { EntryCard } from "@/components/entry-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/use-toast"
import { PromptIdeas } from "@/components/prompt-ideas"
import { fireConfetti } from "@/components/confetti"
import { Badge } from "@/components/ui/badge"

const PAGE_SIZE = 6

export default function Dashboard() {
  const { user } = useAuth()
  const [entries, setEntries] = useState<Entry[]>([])
  const [title, setTitle] = useState(localStorage.getItem("draft_title") || "")
  const [text, setText] = useState(localStorage.getItem("draft_text") || "")
  const [search, setSearch] = useState("")
  const [me, setMe] = useState<User | null>(null)
  const { toast } = useToast()

  // AI state
  const [aiBusy, setAiBusy] = useState(false)
  const [aiPrompts, setAiPrompts] = useState<string[]>([])
  const [aiErr, setAiErr] = useState<string | null>(null)
  const [weekly, setWeekly] = useState<WeeklySummary | null>(null)
  const [weeklyBusy, setWeeklyBusy] = useState(false)
  const [weeklyErr, setWeeklyErr] = useState<string | null>(null)

  // View-all state
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    ; (async () => {
      const rows = await getMyEntries()
      setEntries(rows)
      try {
        const profile = await getMe()
        setMe(profile)
      } catch { }
    })()
  }, [])

  // autosave drafts
  useEffect(() => {
    localStorage.setItem("draft_title", title)
  }, [title])
  useEffect(() => {
    localStorage.setItem("draft_text", text)
  }, [text])

  const onUsePrompt = useCallback((p: string) => {
    setText((t) => (t ? `${t}\n\n${p}` : p))
  }, [])

  const filtered = useMemo(() => {
    if (!search) return entries
    const q = search.toLowerCase()
    return entries.filter(
      (e) =>
        (e.title || "").toLowerCase().includes(q) ||
        (e.text || "").toLowerCase().includes(q)
    )
  }, [entries, search])

  // Reset "showAll" when search changes
  useEffect(() => {
    setShowAll(false)
  }, [search])

  const visibleEntries = useMemo(() => {
    if (showAll) return filtered
    return filtered.slice(0, PAGE_SIZE)
  }, [filtered, showAll])

  const words = useMemo(() => {
    const w = text.trim().split(/\s+/).filter(Boolean).length
    return isNaN(w) ? 0 : w
  }, [text])
  const readingMins = Math.max(1, Math.round(words / 200))

  async function onCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!user) return
    const beforeStreak = me?.current_streak || 0
    const saved = await createEntry({ user_id: user.id, title, text })
    setEntries((prev) => [saved, ...prev])
    setTitle("")
    setText("")
    localStorage.removeItem("draft_title")
    localStorage.removeItem("draft_text")
    toast("Entry saved", "Your journal entry has been created.")

    try {
      await analyzeEntryAI(saved.id)
    } catch (err: any) {
      console.warn("AI analyze failed:", err?.message)
    }

    try {
      const after = await getMe()
      setMe(after)
      if ((after.current_streak || 0) > beforeStreak) {
        fireConfetti()
        toast("Streak +1 🎉", `You're on a ${after.current_streak} day streak!`)
      }
    } catch { }
  }

  // Ctrl/Cmd+S to save
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault()
        const fake = { preventDefault() { } } as unknown as React.FormEvent
        onCreate(fake)
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [title, text, user, me])

  const empty = useMemo(() => entries.length === 0, [entries])

  async function handleAskAI() {
    setAiBusy(true)
    setAiErr(null)
    try {
      const res: PromptResponse = await getAIPrompts("daily reflection", 5)
      setAiPrompts(res.prompts ?? [])
    } catch (e: any) {
      setAiErr(e?.message || "Failed to fetch AI prompts")
    } finally {
      setAiBusy(false)
    }
  }

  async function handleWeekly() {
    setWeeklyBusy(true)
    setWeeklyErr(null)
    try {
      const s = await getWeeklySummary()
      setWeekly(s)
    } catch (e: any) {
      setWeeklyErr(e?.message || "Failed to get weekly summary")
    } finally {
      setWeeklyBusy(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* New Entry */}
        <section className="rounded-lg border p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">New Entry</h2>
            <div className="text-xs text-muted-foreground">
              {words} words • ~{readingMins} min read
            </div>
          </div>
          <form onSubmit={onCreate} className="space-y-3">
            <Input
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <Textarea
              placeholder="How are you feeling today?"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <div className="flex justify-between gap-3">
              <Input
                placeholder="Search your entries..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="max-w-xs"
              />
              <Button
                type="submit"
                disabled={!title.trim() || !text.trim()}
              >
                Save Entry
              </Button>
            </div>
          </form>
        </section>

        {/* Recent Entries */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Recent Entries</h2>
            {filtered.length > PAGE_SIZE && (
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">
                  Showing {visibleEntries.length} of {filtered.length}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAll((s) => !s)}
                >
                  {showAll ? "View less" : "View all"}
                </Button>
              </div>
            )}
          </div>

          {empty && (
            <div className="text-sm text-muted-foreground">No entries yet.</div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            {visibleEntries.map((e) => (
              <EntryCard key={e.id} {...e} />
            ))}
          </div>
        </section>
      </div>

      {/* Sidebar */}
      <aside className="space-y-4">
        <div className="rounded-lg border p-4">
          <h3 className="font-semibold mb-2">AI Coach</h3>
          <p className="text-sm text-muted-foreground mb-2">
            Context-aware prompts and weekly reflections from your recent entries.
          </p>
          <div className="flex gap-2 mb-3">
            <Button variant="outline" onClick={handleAskAI} disabled={aiBusy}>
              {aiBusy ? "Thinking..." : "Ask AI"}
            </Button>
            <Button variant="outline" onClick={handleWeekly} disabled={weeklyBusy}>
              {weeklyBusy ? "Summarizing..." : "Summarize week"}
            </Button>
          </div>

          {aiErr && <div className="text-xs text-red-500 mb-2">{aiErr}</div>}
          {aiPrompts.length > 0 && (
            <ul className="grid gap-2 mb-4">
              {aiPrompts.map((p, i) => (
                <li key={i}>
                  <button
                    onClick={() => onUsePrompt(p)}
                    className="text-left text-sm rounded-md px-3 py-2 bg-muted hover:bg-accent transition"
                    title="Click to insert into your draft"
                  >
                    {p}
                  </button>
                </li>
              ))}
            </ul>
          )}

          {weeklyErr && <div className="text-xs text-red-500">{weeklyErr}</div>}
          {weekly && (
            <div className="rounded-lg border p-4">
              <p className="text-xs text-muted-foreground mb-2">
                {weekly.week_start}
              </p>
              <p className="text-sm whitespace-pre-wrap text-muted-foreground mb-3">
                {weekly.summary}
              </p>
              {weekly.insights.themes?.length ? (
                <div className="flex flex-wrap gap-2">
                  {weekly.insights.themes.map((t: string, i: number) => (
                    <Badge key={i} className="text-xs py-1 px-2 bg-muted">
                      {t}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </div>
          )}
        </div>

        <PromptIdeas onUse={onUsePrompt} />

        <div className="rounded-lg border p-4">
          <h3 className="font-semibold mb-2">Tips</h3>
          <ul className="text-sm list-disc pl-5 space-y-1 text-muted-foreground">
            <li>Write for 5 minutes without judging yourself.</li>
            <li>Note one positive thing from today.</li>
            <li>Close with a small action for tomorrow.</li>
          </ul>
        </div>
      </aside>
    </div>
  )
}
