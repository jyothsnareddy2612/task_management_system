import { LogOut, UserRound } from "lucide-react";

import { Button } from "../components/ui/Button";
import { useAuth } from "../features/auth";
import { TaskBoard } from "../features/tasks";

export function DashboardLayout() {
  const { logout, user } = useAuth();

  return (
    <div className="app-shell">
      <nav className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <span>TM</span>
          <strong>Task Portal</strong>
        </div>
        <div className="nav-item active">Tasks</div>
      </nav>
      <div className="content-shell">
        <header className="topbar">
          <div className="user-chip">
            <UserRound size={18} />
            <span>{user?.name}</span>
            <small>{user?.role}</small>
          </div>
          <Button icon={<LogOut size={17} />} onClick={logout} type="button" variant="ghost">
            Logout
          </Button>
        </header>
        <TaskBoard />
      </div>
    </div>
  );
}
