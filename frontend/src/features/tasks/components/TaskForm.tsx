import { Plus } from "lucide-react";
import { type FormEvent, useState } from "react";

import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import { Select } from "../../../components/ui/Select";
import type { User } from "../../../types/auth";
import type { TaskCreateRequest, TaskPriority } from "../../../types/tasks";

interface TaskFormProps {
  canAssign: boolean;
  onCreate: (payload: TaskCreateRequest) => Promise<void>;
  users: User[];
}

export function TaskForm({ canAssign, onCreate, users }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("MEDIUM");
  const [assignedTo, setAssignedTo] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    try {
      await onCreate({
        assigned_to: assignedTo || undefined,
        description,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        priority,
        title,
      });
      setTitle("");
      setDescription("");
      setPriority("MEDIUM");
      setAssignedTo("");
      setDueDate("");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <Input label="Title" minLength={3} onChange={(event) => setTitle(event.target.value)} required value={title} />
      <label className="field" htmlFor="description">
        <span>Description</span>
        <textarea id="description" onChange={(event) => setDescription(event.target.value)} value={description} />
      </label>
      <Select
        label="Priority"
        onChange={(event) => setPriority(event.target.value as TaskPriority)}
        options={[
          { label: "Low", value: "LOW" },
          { label: "Medium", value: "MEDIUM" },
          { label: "High", value: "HIGH" },
          { label: "Urgent", value: "URGENT" },
        ]}
        value={priority}
      />
      {canAssign ? (
        <Select
          label="Assign to"
          onChange={(event) => setAssignedTo(event.target.value)}
          options={[
            { label: "Unassigned", value: "" },
            ...users.map((user) => ({ label: `${user.name} (${user.role})`, value: user.id })),
          ]}
          value={assignedTo}
        />
      ) : null}
      <Input label="Due date" onChange={(event) => setDueDate(event.target.value)} type="datetime-local" value={dueDate} />
      <Button disabled={isSaving} icon={<Plus size={18} />} type="submit">
        {isSaving ? "Adding..." : "Add task"}
      </Button>
    </form>
  );
}
