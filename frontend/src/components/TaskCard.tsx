import { Link } from "react-router-dom";
import type { Task } from "../lib/api";
import { TASK_ICONS } from "../lib/icons";

export default function TaskCard({ task }: { task: Task }) {
  return (
    <Link to={`/task/${task.id}`} className="task-card">
      {task.experimental && <span className="badge">experimental</span>}
      <div className="task-icon">{TASK_ICONS[task.id] ?? "🧠"}</div>
      <div className="task-label">{task.label}</div>
      <div className="task-desc">{task.description}</div>
    </Link>
  );
}
