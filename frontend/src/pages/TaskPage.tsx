import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ResultViewer from "../components/ResultViewer";
import { fetchTask, runInference, type InferResult, type Task } from "../lib/api";
import { TASK_ICONS } from "../lib/icons";

export default function TaskPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<Task | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [candidateLabels, setCandidateLabels] = useState("");
  const [modelId, setModelId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InferResult | null>(null);

  useEffect(() => {
    if (!taskId) return;
    setTask(null);
    setResult(null);
    setError(null);
    setFile(null);
    setPreviewUrl(null);
    setPrompt("");
    setCandidateLabels("");
    setModelId("");
    fetchTask(taskId)
      .then(setTask)
      .catch((err) => setError(err.message));
  }, [taskId]);

  if (!taskId) return null;

  function handleFile(selected: File | null) {
    setFile(selected);
    setPreviewUrl(selected ? URL.createObjectURL(selected) : null);
  }

  async function handleRun() {
    if (!task) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await runInference(task.id, {
        file,
        prompt,
        candidateLabels,
        modelId: modelId || undefined,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const needsFile = task && ["image", "image_text", "video"].includes(task.input_type);
  const needsPrompt = task && ["text", "image_text"].includes(task.input_type);
  const needsLabels = task?.input_type === "image_text";

  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← All tasks
      </Link>

      {!task && !error && <p>Loading…</p>}
      {error && !task && <div className="error-banner">{error}</div>}

      {task && (
        <>
          <header className="task-header">
            <div className="task-icon-lg">{TASK_ICONS[task.id] ?? "🧠"}</div>
            <div>
              <h1>{task.label}</h1>
              <p>{task.description}</p>
              {task.experimental && (
                <div className="warning-banner">
                  This task is experimental on Hugging Face's free serverless API. It
                  may need a dedicated Inference Endpoint — override the model ID below
                  with your own endpoint if the default fails.
                </div>
              )}
            </div>
          </header>

          <div className="workspace">
            <div className="panel">
              <h3>Input</h3>

              {needsFile && (
                <div className="field">
                  <label>{task.input_type === "video" ? "Video file" : "Image file"}</label>
                  <input
                    type="file"
                    accept={task.input_type === "video" ? "video/*" : "image/*"}
                    onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                  />
                  {previewUrl && task.input_type !== "video" && (
                    <img src={previewUrl} alt="preview" className="preview-image" />
                  )}
                  {previewUrl && task.input_type === "video" && (
                    <video src={previewUrl} controls className="preview-image" />
                  )}
                </div>
              )}

              {needsPrompt && (
                <div className="field">
                  <label>Prompt</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe what you want…"
                    rows={3}
                  />
                </div>
              )}

              {needsLabels && (
                <div className="field">
                  <label>Candidate labels (comma-separated)</label>
                  <input
                    type="text"
                    value={candidateLabels}
                    onChange={(e) => setCandidateLabels(e.target.value)}
                    placeholder="cat, dog, car, tree"
                  />
                </div>
              )}

              <div className="field">
                <label>Model ID (optional override)</label>
                <input
                  type="text"
                  value={modelId}
                  onChange={(e) => setModelId(e.target.value)}
                  placeholder={task.default_model}
                />
              </div>

              <button className="run-btn" onClick={handleRun} disabled={loading}>
                {loading ? "Running…" : "Run"}
              </button>
            </div>

            <div className="panel">
              <h3>Output</h3>
              {error && <div className="error-banner">{error}</div>}
              {!error && !result && <p className="muted">Run the task to see results here.</p>}
              {result && (
                <>
                  <p className="muted">Model: {result.model}</p>
                  <ResultViewer result={result} />
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
