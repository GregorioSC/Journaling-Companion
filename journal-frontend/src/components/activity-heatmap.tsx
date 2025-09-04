type Day = { date: string; count: number }

function getWeekday(d: Date) {
  return d.getDay() // 0 Sun ... 6 Sat
}

export function ActivityHeatmap({ days }: { days: Day[] }) {
  // Build last 12 weeks columns (Sun..Sat)
  const today = new Date()
  const start = new Date(today)
  start.setDate(start.getDate() - (11 * 7 + getWeekday(today))) // start on a Sunday ~12 weeks ago

  const map = new Map(days.map(d => [new Date(d.date).toDateString(), d.count]))
  const cols: { date: Date; count: number }[][] = []
  let cursor = new Date(start)

  for (let c = 0; c < 12; c++) {
    const col: { date: Date; count: number }[] = []
    for (let r = 0; r < 7; r++) {
      const key = new Date(cursor).toDateString()
      const count = map.get(key) || 0
      col.push({ date: new Date(cursor), count })
      cursor.setDate(cursor.getDate() + 1)
    }
    cols.push(col)
  }

  function level(count: number) {
    if (count === 0) return "bg-muted/40"
    if (count === 1) return "bg-primary/20"
    if (count === 2) return "bg-primary/40"
    if (count === 3) return "bg-primary/60"
    return "bg-primary"
  }

  return (
    <div className="flex gap-1 overflow-x-auto rounded-md border p-3">
      {cols.map((col, i) => (
        <div key={i} className="grid gap-1" style={{ gridTemplateRows: "repeat(7, 12px)" }}>
          {col.map((cell, j) => (
            <div
              key={j}
              className={`h-3 w-3 rounded-sm ${level(cell.count)}`}
              title={`${cell.date.toDateString()} — ${cell.count} entries`}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
