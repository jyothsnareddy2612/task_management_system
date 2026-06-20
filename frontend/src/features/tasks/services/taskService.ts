import { apiClient } from "../../../lib/http";
import type { Comment, Task, TaskCreateRequest, TaskHistory, TaskPage, TaskUpdateRequest } from "../../../types/tasks";

export const taskService = {
  async listTasks() {
    const { data } = await apiClient.get<TaskPage>("/tasks");
    return data;
  },

  async createTask(payload: TaskCreateRequest) {
    const { data } = await apiClient.post<Task>("/tasks", payload);
    return data;
  },

  async updateTask(taskId: string, payload: TaskUpdateRequest) {
    const { data } = await apiClient.patch<Task>(`/tasks/${taskId}`, payload);
    return data;
  },

  async deleteTask(taskId: string) {
    await apiClient.delete(`/tasks/${taskId}`);
  },

  async listComments(taskId: string) {
    const { data } = await apiClient.get<Comment[]>(`/tasks/${taskId}/comments`);
    return data;
  },

  async addComment(taskId: string, content: string) {
    const { data } = await apiClient.post<Comment>(`/tasks/${taskId}/comments`, { content });
    return data;
  },

  async listHistory(taskId: string) {
    const { data } = await apiClient.get<TaskHistory[]>(`/tasks/${taskId}/history`);
    return data;
  },
};
