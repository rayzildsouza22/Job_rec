import { api } from "./api";
import type { Job } from "../types/domain";

export async function listJobs(q?: string, location?: string): Promise<Job[]> {
  const res = await api.get<Job[]>("/jobs", { params: { q, location } });
  return res.data;
}

export async function getJob(id: number): Promise<Job> {
  const res = await api.get<Job>(`/jobs/${id}`);
  return res.data;
}

export async function createJob(data: Omit<Job, "id" | "created_at">): Promise<Job> {
  const res = await api.post<Job>("/jobs", data);
  return res.data;
}

export async function updateJob(id: number, data: Partial<Job>): Promise<Job> {
  const res = await api.put<Job>(`/jobs/${id}`, data);
  return res.data;
}

export async function deleteJob(id: number): Promise<void> {
  await api.delete(`/jobs/${id}`);
}
