import BoundingBoxViewer from "./BoundingBoxViewer";
import type { InferResult } from "../lib/api";

function isDetectionArray(data: unknown): data is { score: number; label: string; box: unknown }[] {
  return (
    Array.isArray(data) &&
    data.length > 0 &&
    data.every((d) => d && typeof d === "object" && "box" in d && "label" in d)
  );
}

export default function ResultViewer({
  result,
  sourceImageUrl,
}: {
  result: InferResult;
  sourceImageUrl?: string | null;
}) {
  const { type, data } = result.result;

  if (type === "image") {
    return <img className="result-image" src={data as string} alt="Model output" />;
  }

  if (type === "video") {
    return (
      <video className="result-image" src={data as string} controls autoPlay loop />
    );
  }

  if (type === "text") {
    return <pre className="result-text">{String(data)}</pre>;
  }

  if (type === "json" && sourceImageUrl && isDetectionArray(data)) {
    return <BoundingBoxViewer imageUrl={sourceImageUrl} detections={data} />;
  }

  return <pre className="result-json">{JSON.stringify(data, null, 2)}</pre>;
}
