import { api } from "./api";
import type { Resume } from "../types/domain";

export async function uploadResume(file: File): Promise<Resume> {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post<Resume>("/resumes/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function getMyResume(): Promise<Resume> {
  const res = await api.get<Resume>("/resumes/me");
  return res.data;
}

export async function deleteMyResume(): Promise<void> {
  await api.delete("/resumes/me");
}
