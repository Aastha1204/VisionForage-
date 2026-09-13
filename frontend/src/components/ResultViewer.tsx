import type { InferResult } from "../lib/api";

export default function ResultViewer({ result }: { result: InferResult }) {
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

  return <pre className="result-json">{JSON.stringify(data, null, 2)}</pre>;
}
