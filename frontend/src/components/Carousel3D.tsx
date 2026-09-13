import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Task } from "../lib/api";
import { TASK_ICONS } from "../lib/icons";

const CARD_WIDTH = 200;

export default function Carousel3D({ tasks }: { tasks: Task[] }) {
  const navigate = useNavigate();
  const [angle, setAngle] = useState(0);
  const pausedRef = useRef(false);
  const angleRef = useRef(0);
  const rafRef = useRef<number | null>(null);

  const count = tasks.length;
  const angleStep = 360 / Math.max(count, 1);
  const radius = Math.round(CARD_WIDTH / 2 / Math.tan(Math.PI / Math.max(count, 3)));

  useEffect(() => {
    let last = performance.now();
    function tick(now: number) {
      const dt = now - last;
      last = now;
      if (!pausedRef.current) {
        angleRef.current = (angleRef.current + dt * 0.012) % 360;
        setAngle(angleRef.current);
      }
      rafRef.current = requestAnimationFrame(tick);
    }
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  function rotateBy(delta: number) {
    angleRef.current = (angleRef.current + delta + 360) % 360;
    setAngle(angleRef.current);
  }

  if (count === 0) return null;

  return (
    <div
      className="carousel3d-scene"
      onMouseEnter={() => (pausedRef.current = true)}
      onMouseLeave={() => (pausedRef.current = false)}
    >
      <div className="carousel3d-stage" style={{ transform: `rotateY(${-angle}deg)` }}>
        {tasks.map((task, i) => {
          const itemAngle = i * angleStep;
          return (
            <div
              key={task.id}
              className="carousel3d-card"
              style={{
                transform: `rotateY(${itemAngle}deg) translateZ(${radius}px)`,
              }}
              onClick={() => navigate(`/task/${task.id}`)}
            >
              <div className="carousel3d-icon">{TASK_ICONS[task.id] ?? "🧠"}</div>
              <div className="carousel3d-label">{task.label}</div>
            </div>
          );
        })}
      </div>
      <button className="carousel3d-nav carousel3d-nav-left" onClick={() => rotateBy(-angleStep)} aria-label="Previous">
        ‹
      </button>
      <button className="carousel3d-nav carousel3d-nav-right" onClick={() => rotateBy(angleStep)} aria-label="Next">
        ›
      </button>
    </div>
  );
}
