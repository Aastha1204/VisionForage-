import { useEffect, useState } from "react";
import Carousel3D from "../components/Carousel3D";
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
      <div className="bg-orb bg-orb-1" />
      <div className="bg-orb bg-orb-2" />
      <div className="bg-orb bg-orb-3" />

      <header className="hero">
        <h1>VisionForge</h1>
        <p>One dashboard for every computer-vision task, powered by Hugging Face.</p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {tasks.length > 0 && (
        <>
          <h2 className="section-title">Spin the wheel</h2>
          <Carousel3D tasks={tasks} />
        </>
      )}

      <h2 className="section-title">Computer Vision</h2>
      <div className="grid">
        {tasks.map((task, i) => (
          <TaskCard key={task.id} task={task} index={i} />
        ))}
      </div>
    </div>
  );
}
