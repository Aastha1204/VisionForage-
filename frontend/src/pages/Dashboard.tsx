import { useEffect, useState } from "react";
import TaskCard from "../components/TaskCard";
import { fetchTasks, type Task } from "../lib/api";

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="page">
      <header className="hero">
        <h1>VisionForge</h1>
        <p>One dashboard for every computer-vision task, powered by Hugging Face.</p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <h2 className="section-title">Computer Vision</h2>
      <div className="grid">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}
