import { api } from "./api";
import type { SavedJob } from "../types/domain";

export async function listSavedJobs(): Promise<SavedJob[]> {
  const res = await api.get<SavedJob[]>("/saved-jobs");
  return res.data;
}

export async function saveJob(jobId: number): Promise<SavedJob> {
  const res = await api.post<SavedJob>(`/saved-jobs/${jobId}`);
  return res.data;
}

export async function unsaveJob(jobId: number): Promise<void> {
  await api.delete(`/saved-jobs/${jobId}`);
}
