import { useRef, useState, type CSSProperties, type MouseEvent, type ReactNode } from "react";

export default function TiltCard({
  children,
  className = "",
  maxTilt = 12,
  onClick,
}: {
  children: ReactNode;
  className?: string;
  maxTilt?: number;
  onClick?: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [style, setStyle] = useState<CSSProperties>({});
  const [glare, setGlare] = useState({ x: 50, y: 50, opacity: 0 });

  function handleMouseMove(e: MouseEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;
    const rotateY = (px - 0.5) * maxTilt * 2;
    const rotateX = (0.5 - py) * maxTilt * 2;

    setStyle({
      transform: `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.03, 1.03, 1.03)`,
    });
    setGlare({ x: px * 100, y: py * 100, opacity: 0.15 });
  }

  function handleMouseLeave() {
    setStyle({ transform: "perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)" });
    setGlare((g) => ({ ...g, opacity: 0 }));
  }

  return (
    <div
      ref={ref}
      className={`tilt-card ${className}`}
      style={style}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
    >
      <div
        className="tilt-glare"
        style={{
          background: `radial-gradient(circle at ${glare.x}% ${glare.y}%, rgba(255,255,255,${glare.opacity}), transparent 60%)`,
        }}
      />
      <div className="tilt-content">{children}</div>
    </div>
  );
}
