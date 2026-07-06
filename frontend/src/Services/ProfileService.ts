import { api } from "./api";
import type { Profile } from "../types/domain";

export async function getMyProfile(): Promise<Profile> {
  const res = await api.get<Profile>("/profiles/me");
  return res.data;
}

export async function updateMyProfile(data: Partial<Profile>): Promise<Profile> {
  const res = await api.put<Profile>("/profiles/me", data);
  return res.data;
}
