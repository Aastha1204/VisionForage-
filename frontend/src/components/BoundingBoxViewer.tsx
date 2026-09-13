import { useState } from "react";

type Detection = {
  score: number;
  label: string;
  box: { xmin: number; ymin: number; xmax: number; ymax: number };
};

const COLORS = ["#4f8cff", "#f5a524", "#3ddc97", "#ff5a8a", "#a78bfa", "#ffd23f", "#ff7a45", "#36cfc9"];

function buildColorMap(labels: string[]): Map<string, string> {
  const map = new Map<string, string>();
  let next = 0;
  for (const label of labels) {
    if (!map.has(label)) {
      map.set(label, COLORS[next % COLORS.length]);
      next++;
    }
  }
  return map;
}

export default function BoundingBoxViewer({
  imageUrl,
  detections,
}: {
  imageUrl: string;
  detections: Detection[];
}) {
  const [naturalSize, setNaturalSize] = useState<{ w: number; h: number } | null>(null);
  const colorMap = buildColorMap(detections.map((d) => d.label));

  return (
    <div className="bbox-wrap">
      <img
        className="result-image"
        src={imageUrl}
        alt="Detection input"
        onLoad={(e) => {
          const img = e.currentTarget;
          setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
        }}
      />
      {naturalSize && (
        <svg
          className="bbox-overlay"
          viewBox={`0 0 ${naturalSize.w} ${naturalSize.h}`}
          preserveAspectRatio="none"
        >
          {detections.map((d, i) => {
            const { xmin, ymin, xmax, ymax } = d.box;
            const color = colorMap.get(d.label)!;
            const w = xmax - xmin;
            const h = ymax - ymin;
            const fontSize = Math.max(naturalSize.h * 0.022, 14);
            return (
              <g key={i}>
                <rect
                  x={xmin}
                  y={ymin}
                  width={w}
                  height={h}
                  fill="none"
                  stroke={color}
                  strokeWidth={Math.max(naturalSize.w * 0.003, 2)}
                />
                <rect
                  x={xmin}
                  y={Math.max(ymin - fontSize * 1.4, 0)}
                  width={Math.min((d.label.length + 5) * fontSize * 0.55, w + 40)}
                  height={fontSize * 1.4}
                  fill={color}
                />
                <text
                  x={xmin + 4}
                  y={Math.max(ymin - fontSize * 0.35, fontSize)}
                  fontSize={fontSize}
                  fill="#0b0f1a"
                  fontWeight={700}
                >
                  {d.label} {(d.score * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
