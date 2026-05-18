import { ListChecks, RefreshCcw } from "lucide-react";

import { EmptyState } from "../../../components/common/EmptyState";
import { PageHeader } from "../../../components/common/PageHeader";
import { Button } from "../../../components/ui/Button";
import { TASK_STATUS_LABELS } from "../../../config/constants";
import { useAuth } from "../../auth";
import { adminService } from "../../admin/services/adminService";
import type { User } from "../../../types/auth";
import type { TaskStatus } from "../../../types/tasks";
import { TaskCard } from "./TaskCard";
import { TaskForm } from "./TaskForm";
import { useTasks } from "../hooks/useTasks";
import { useEffect, useMemo, useState } from "react";

const statusOptions: Array<TaskStatus | "ALL"> = ["ALL", "TODO", "IN_PROGRESS", "DONE"];

export function TaskBoard() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const {
    createTask,
    deleteTask,
    error,
    filteredTasks,
    isLoading,
    loadTasks,
    setStatusFilter,
    statusFilter,
    tasks,
    updateTask,
  } = useTasks();
  const canManage = user?.role === "ADMIN";
  const visibleUsers = useMemo(() => {
    if (users.length > 0) {
      return users;
    }
    return user ? [user] : [];
  }, [user, users]);

  useEffect(() => {
    if (!canManage) {
      setUsers(user ? [user] : []);
      return;
    }
    void adminService.listUsers().then(setUsers).catch(() => setUsers(user ? [user] : []));
  }, [canManage, user]);

  return (
    <main className="dashboard-main">
      <PageHeader
        actions={
          <Button icon={<RefreshCcw size={17} />} onClick={loadTasks} type="button" variant="secondary">
            Refresh
          </Button>
        }
        description="Assign work, track progress, collaborate through comments, and review status history."
        title="Task workspace"
      />

      <section className="dashboard-grid">
        <aside className="panel create-panel">
          <h2>Create task</h2>
          <TaskForm canAssign={canManage} onCreate={createTask} users={visibleUsers} />
        </aside>

        <section className="panel task-panel">
          <div className="task-toolbar">
            <div>
              <h2>Tasks</h2>
              <p>{tasks.length} total tasks</p>
            </div>
            <div className="segmented-control" aria-label="Filter tasks by status">
              {statusOptions.map((status) => (
                <button
                  className={statusFilter === status ? "active" : ""}
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  type="button"
                >
                  {status === "ALL" ? "All" : TASK_STATUS_LABELS[status]}
                </button>
              ))}
            </div>
          </div>

          {error ? <p className="form-error">{error}</p> : null}
          {isLoading ? <div className="skeleton-list" aria-label="Loading tasks" /> : null}
          {!isLoading && filteredTasks.length === 0 ? (
            <EmptyState
              body="Create a task or change the status filter to see matching work."
              icon={<ListChecks size={28} />}
              title="No tasks found"
            />
          ) : null}
          <div className="task-list">
            {filteredTasks.map((task) => (
              <TaskCard
                canManage={canManage}
                key={task.id}
                onDelete={deleteTask}
                onStatusChange={(taskId, status) => updateTask(taskId, { status })}
                onUpdate={updateTask}
                task={task}
                users={visibleUsers}
              />
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
