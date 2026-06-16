import { useCallback, useEffect, useMemo, useState } from "react";

import { env } from "../../../config/env";
import { getApiErrorMessage } from "../../../services/apiError";
import type { Task, TaskCreateRequest, TaskStatus, TaskUpdateRequest } from "../../../types/tasks";
import { taskService } from "../services/taskService";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "ALL">("ALL");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadTasks = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    try {
      const page = await taskService.listTasks();
      setTasks(page.items);
    } catch (error) {
      setError(getApiErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    const websocket = new WebSocket(env.taskEventsUrl);

    websocket.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data) as {
          event_type: "task.created" | "task.updated" | "task.deleted";
          payload: Task | { id: string };
          task_id: string;
        };

        if (event.event_type === "task.deleted") {
          setTasks((current) => current.filter((task) => task.id !== event.task_id));
          return;
        }

        const task = event.payload as Task;
        setTasks((current) => {
          const exists = current.some((item) => item.id === task.id);
          if (exists) {
            return current.map((item) => (item.id === task.id ? task : item));
          }
          return [task, ...current];
        });
      } catch {
        void loadTasks();
      }
    };

    return () => websocket.close();
  }, [loadTasks]);

  const filteredTasks = useMemo(
    () => (statusFilter === "ALL" ? tasks : tasks.filter((task) => task.status === statusFilter)),
    [statusFilter, tasks],
  );

  const createTask = useCallback(
    async (payload: TaskCreateRequest) => {
      const task = await taskService.createTask(payload);
      setTasks((current) => [task, ...current]);
    },
    [],
  );

  const updateTask = useCallback(async (taskId: string, payload: TaskUpdateRequest) => {
    const task = await taskService.updateTask(taskId, payload);
    setTasks((current) => current.map((item) => (item.id === task.id ? task : item)));
  }, []);

  const deleteTask = useCallback(async (taskId: string) => {
    await taskService.deleteTask(taskId);
    setTasks((current) => current.filter((task) => task.id !== taskId));
  }, []);

  return {
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
  };
}
