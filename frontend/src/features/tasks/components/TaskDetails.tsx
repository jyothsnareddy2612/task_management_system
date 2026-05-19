import { MessageSquare, Save } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import { Select } from "../../../components/ui/Select";
import { TASK_PRIORITY_LABELS, TASK_STATUS_LABELS } from "../../../config/constants";
import type { User } from "../../../types/auth";
import type { Comment, Task, TaskHistory, TaskPriority, TaskStatus, TaskUpdateRequest } from "../../../types/tasks";
import { formatDate } from "../../../utils/formatDate";
import { taskService } from "../services/taskService";

interface TaskDetailsProps {
  canManage: boolean;
  onUpdate: (taskId: string, payload: TaskUpdateRequest) => Promise<void>;
  task: Task;
  users: User[];
}

function toDateTimeLocal(value: string | null) {
  if (!value) {
    return "";
  }
  return value.slice(0, 16);
}

export function TaskDetails({ canManage, onUpdate, task, users }: TaskDetailsProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [history, setHistory] = useState<TaskHistory[]>([]);
  const [comment, setComment] = useState("");
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description ?? "");
  const [priority, setPriority] = useState<TaskPriority>(task.priority);
  const [status, setStatus] = useState<TaskStatus>(task.status);
  const [assignedTo, setAssignedTo] = useState(task.assigned_to ?? "");
  const [dueDate, setDueDate] = useState(toDateTimeLocal(task.due_date));
  const userNameById = new Map(users.map((user) => [user.id, user.name]));

  useEffect(() => {
    void taskService.listComments(task.id).then(setComments);
    void taskService.listHistory(task.id).then(setHistory);
  }, [task.id]);

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onUpdate(task.id, {
      assigned_to: assignedTo || null,
      description,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      priority,
      status,
      title,
    });
  }

  async function handleComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!comment.trim()) {
      return;
    }
    const saved = await taskService.addComment(task.id, comment.trim());
    setComments((current) => [...current, saved]);
    setComment("");
  }

  return (
    <div className="task-details">
      <form className="edit-form" onSubmit={handleSave}>
        <Input disabled={!canManage} label="Edit title" minLength={3} onChange={(event) => setTitle(event.target.value)} value={title} />
        <label className="field" htmlFor={`edit-description-${task.id}`}>
          <span>Edit description</span>
          <textarea
            disabled={!canManage}
            id={`edit-description-${task.id}`}
            onChange={(event) => setDescription(event.target.value)}
            value={description}
          />
        </label>
        <div className="edit-grid">
          <Select
            disabled={!canManage}
            label="Status"
            onChange={(event) => setStatus(event.target.value as TaskStatus)}
            options={Object.entries(TASK_STATUS_LABELS).map(([value, label]) => ({ label, value }))}
            value={status}
          />
          <Select
            disabled={!canManage}
            label="Priority"
            onChange={(event) => setPriority(event.target.value as TaskPriority)}
            options={Object.entries(TASK_PRIORITY_LABELS).map(([value, label]) => ({ label, value }))}
            value={priority}
          />
          <Select
            disabled={!canManage}
            label="Assigned worker"
            onChange={(event) => setAssignedTo(event.target.value)}
            options={[
              { label: "Unassigned", value: "" },
              ...users.map((user) => ({ label: `${user.name} (${user.role})`, value: user.id })),
            ]}
            value={assignedTo}
          />
          <Input disabled={!canManage} label="Due date" onChange={(event) => setDueDate(event.target.value)} type="datetime-local" value={dueDate} />
        </div>
        {canManage ? (
          <Button icon={<Save size={16} />} type="submit" variant="secondary">
            Save changes
          </Button>
        ) : null}
      </form>

      <section className="comments-section">
        <h4>Comments</h4>
        <form className="comment-form" onSubmit={handleComment}>
          <Input label="Add comment" onChange={(event) => setComment(event.target.value)} value={comment} />
          <Button icon={<MessageSquare size={16} />} type="submit" variant="secondary">
            Comment
          </Button>
        </form>
        <div className="comment-list">
          {comments.length === 0 ? <p>No comments yet.</p> : null}
          {comments.map((item) => (
            <article className="comment-item" key={item.id}>
              <p>{item.content}</p>
              <span>{formatDate(item.created_at)}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="history-section">
        <h4>Status history</h4>
        {history.length === 0 ? <p>No status history yet.</p> : null}
        {history.map((item) => (
          <div className="history-item" key={item.id}>
            <span>
              Old status <strong>{item.old_status ? TASK_STATUS_LABELS[item.old_status] : "Created"}</strong>
            </span>
            <span>
              New status <strong>{TASK_STATUS_LABELS[item.new_status]}</strong>
            </span>
            <span>
              Changed by <strong>{userNameById.get(item.changed_by) ?? item.changed_by}</strong>
            </span>
            <span>
              Changed at <strong>{formatDate(item.changed_at)}</strong>
            </span>
          </div>
        ))}
      </section>
    </div>
  );
}
