export type Task = {
  id: string;
  label: string;
  category: string;
  description: string;
  default_model: string;
  input_type: "image" | "text" | "image_text" | "video" | "none";
  output_type: "image" | "json" | "text" | "video";
  experimental: boolean;
};

export type InferResult = {
  task_id: string;
  model: string;
  result: {
    type: "image" | "video" | "json" | "text";
    data: unknown;
  };
};

export async function fetchTasks(): Promise<Task[]> {
  const res = await fetch("/api/tasks");
  if (!res.ok) throw new Error("Failed to load tasks");
  const body = await res.json();
  return body.tasks;
}

export async function fetchTask(taskId: string): Promise<Task> {
  const res = await fetch(`/api/tasks/${taskId}`);
  if (!res.ok) throw new Error("Task not found");
  return res.json();
}

export async function runInference(
  taskId: string,
  fields: {
    file?: File | null;
    prompt?: string;
    candidateLabels?: string;
    modelId?: string;
  },
): Promise<InferResult> {
  const form = new FormData();
  if (fields.file) form.append("file", fields.file);
  if (fields.prompt) form.append("prompt", fields.prompt);
  if (fields.candidateLabels) form.append("candidate_labels", fields.candidateLabels);
  if (fields.modelId) form.append("model_id", fields.modelId);

  // An empty FormData still sends a multipart body with zero parts, which
  // FastAPI's parser rejects outright — send no body at all in that case.
  const hasFields = Array.from(form.keys()).length > 0;
  const res = await fetch(`/api/infer/${taskId}`, {
    method: "POST",
    body: hasFields ? form : undefined,
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail || "Inference failed");
  return body;
}
