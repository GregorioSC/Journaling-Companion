import { Button } from "@/components/ui/button"

const PROMPTS = [
  "What energized you today? Why?",
  "Describe a moment of calm you noticed.",
  "What’s one small win you’re proud of?",
  "What challenged you today, and how did you respond?",
  "Name one thing you’ll try tomorrow to make it 1% better.",
  "Who supported you recently? Write them a thank-you note (even if you don’t send it).",
  "When did you feel most like yourself this week?"
]

export function PromptIdeas({ onUse }: { onUse: (text: string) => void }) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">Prompt ideas</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            const idx = Math.floor(Math.random() * PROMPTS.length)
            onUse(PROMPTS[idx])
          }}
        >
          Surprise me
        </Button>
      </div>
      <div className="grid gap-2">
        {PROMPTS.slice(0, 4).map((p, i) => (
          <button
            key={i}
            onClick={() => onUse(p)}
            className="text-left text-sm rounded-md px-3 py-2 bg-muted hover:bg-accent transition"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}
