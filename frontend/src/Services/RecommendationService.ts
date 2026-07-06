import { api } from "./api";
import type {
  RecommendationHistoryItem,
  RecommendationItem,
  SkillGap,
} from "../types/domain";

export async function generateRecommendations(topK = 5): Promise<RecommendationItem[]> {
  const res = await api.post<{ items: RecommendationItem[] }>(
    "/recommendations/generate",
    null,
    { params: { top_k: topK } },
  );
  return res.data.items;
}

export async function getHistory(): Promise<RecommendationHistoryItem[]> {
  const res = await api.get<RecommendationHistoryItem[]>("/recommendations/history");
  return res.data;
}

export async function getSkillGap(jobId: number): Promise<SkillGap> {
  const res = await api.get<SkillGap>(`/recommendations/skill-gap/${jobId}`);
  return res.data;
}
