import { apiClient } from "../../../lib/http";
import type { User } from "../../../types/auth";

export const adminService = {
  async listUsers() {
    const { data } = await apiClient.get<User[]>("/admin/users");
    return data;
  },
};
