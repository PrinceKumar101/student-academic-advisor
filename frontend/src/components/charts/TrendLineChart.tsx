import type { components } from "../../types/api";
import { EmptyState } from "../EmptyState";

type TrendSeries = components["schemas"]["TrendSeriesOut"];

const WIDTH = 640;
const HEIGHT = 220;
const PAD = 28;

export function TrendLineChart({ series, title }: { series: TrendSeries; title: string }) {
  if (series.points.length === 0) {
    return <EmptyState title={`${title}: no points`} />;
  }

  const values = series.points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  const coordinates = series.points.map((point, index) => {
    const x = PAD + (index / Math.max(series.points.length - 1, 1)) * (WIDTH - PAD * 2);
    const y = HEIGHT - PAD - ((point.value - min) / span) * (HEIGHT - PAD * 2);
    return { x, y, on: point.on, value: point.value };
  });
  const polyline = coordinates.map((point) => `${point.x},${point.y}`).join(" ");
  const gridYs = [PAD, HEIGHT / 2, HEIGHT - PAD];

  return (
    <figure className="max-w-full rounded-lg border border-rule bg-surface p-4">
      <figcaption className="mb-2 font-serif text-base text-ink">
        {title}: {series.label}
        {series.slope !== null ? ` (slope ${series.slope})` : ""}
        {series.sudden_change ? ` · ${series.sudden_change}` : ""}
      </figcaption>
      <svg
        role="img"
        aria-label={`${title} ${series.label}`}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="h-64 w-full text-accent"
      >
        {gridYs.map((y) => (
          <line key={y} x1={PAD} x2={WIDTH - PAD} y1={y} y2={y} stroke="#D7D0C3" strokeWidth="1" />
        ))}
        <polyline fill="none" stroke="currentColor" strokeWidth="2.5" points={polyline} />
        {coordinates.map((point) => (
          <g key={`${point.on}-${point.value}`}>
            <circle cx={point.x} cy={point.y} r="4" fill="#1F4E79" />
            <title>
              {point.on}: {point.value}
            </title>
          </g>
        ))}
      </svg>
    </figure>
  );
}
