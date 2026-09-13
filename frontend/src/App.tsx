import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TaskPage from "./pages/TaskPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/task/:taskId" element={<TaskPage />} />
    </Routes>
  );
}
