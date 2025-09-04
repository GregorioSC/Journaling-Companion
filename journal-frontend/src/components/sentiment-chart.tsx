import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts"

export function SentimentChart({
  data,
}: {
  data: { date: string; sentiment: number }[]
}) {
  return (
    <div className="w-full">
      <p className="text-sm text-muted-foreground mb-2">
        Sentiment ranges from <b>-1</b> (closer to sad/negative) to <b>+1</b>{" "}
        (closer to happy/positive).
      </p>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[-1, 1]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="sentiment"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
