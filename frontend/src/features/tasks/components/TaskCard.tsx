import { CheckCircle2, Circle, Clock3, Edit3, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "../../../components/ui/Button";
import { TASK_PRIORITY_LABELS, TASK_STATUS_LABELS } from "../../../config/constants";
import type { User } from "../../../types/auth";
import type { Task, TaskStatus, TaskUpdateRequest } from "../../../types/tasks";
import { formatDate } from "../../../utils/formatDate";
import { TaskDetails } from "./TaskDetails";

interface TaskCardProps {
  canManage: boolean;
  onDelete: (taskId: string) => Promise<void>;
  onStatusChange: (taskId: string, status: TaskStatus) => Promise<void>;
  onUpdate: (taskId: string, payload: TaskUpdateRequest) => Promise<void>;
  task: Task;
  users: User[];
}

const nextStatus: Record<TaskStatus, TaskStatus> = {
  TODO: "IN_PROGRESS",
  IN_PROGRESS: "DONE",
  DONE: "TODO",
};

const statusIcon = {
  TODO: <Circle size={16} />,
  IN_PROGRESS: <Clock3 size={16} />,
  DONE: <CheckCircle2 size={16} />,
};

export function TaskCard({ canManage, onDelete, onStatusChange, onUpdate, task, users }: TaskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const assignee = users.find((user) => user.id === task.assigned_to);

  return (
    <article className={`task-card priority-${task.priority.toLowerCase()}`}>
      <div className="task-card-top">
        <span className={`status-pill status-${task.status.toLowerCase()}`}>
          {statusIcon[task.status]}
          {TASK_STATUS_LABELS[task.status]}
        </span>
        <span className="priority-pill">{TASK_PRIORITY_LABELS[task.priority]}</span>
      </div>
      <h3>{task.title}</h3>
      <p>{task.description || "No description added."}</p>
      <div className="task-meta">
        <span>Due {formatDate(task.due_date)}</span>
        <span>Assigned to {assignee?.name ?? "Unassigned"}</span>
      </div>
      <div className="task-actions">
        <Button onClick={() => onStatusChange(task.id, nextStatus[task.status])} type="button" variant="secondary">
          Move to {TASK_STATUS_LABELS[nextStatus[task.status]]}
        </Button>
        <Button icon={<Edit3 size={16} />} onClick={() => setIsExpanded((value) => !value)} type="button" variant="ghost">
          Details
        </Button>
        <Button
          aria-label={`Delete ${task.title}`}
          icon={<Trash2 size={16} />}
          onClick={() => onDelete(task.id)}
          type="button"
          variant="ghost"
        />
      </div>
      {isExpanded ? <TaskDetails canManage={canManage} onUpdate={onUpdate} task={task} users={users} /> : null}
    </article>
  );
}
