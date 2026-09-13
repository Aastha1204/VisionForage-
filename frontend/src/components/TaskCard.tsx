import { useNavigate } from "react-router-dom";
import type { Task } from "../lib/api";
import { TASK_ICONS } from "../lib/icons";
import TiltCard from "./TiltCard";

export default function TaskCard({ task, index = 0 }: { task: Task; index?: number }) {
  const navigate = useNavigate();

  return (
    <TiltCard className="task-card" onClick={() => navigate(`/task/${task.id}`)} maxTilt={10}>
      <div className="task-card-inner entrance" style={{ animationDelay: `${index * 45}ms` }}>
        {task.experimental ? (
          <span className="badge badge-experimental">experimental</span>
        ) : (
          <span className="badge badge-live">● live</span>
        )}
        <div className="task-icon">{TASK_ICONS[task.id] ?? "🧠"}</div>
        <div className="task-label">{task.label}</div>
        <div className="task-desc">{task.description}</div>
      </div>
    </TiltCard>
  );
}
