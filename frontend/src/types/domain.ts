export interface Profile {
  id: number;
  user_id: number;
  full_name: string | null;
  education: string | null;
  skills: string | null;
  experience_level: string | null;
  preferred_role: string | null;
  preferred_location: string | null;
  updated_at: string;
}

export interface Job {
  id: number;
  company: string;
  title: string;
  description: string;
  required_skills: string;
  location: string | null;
  experience: string | null;
  salary: string | null;
  created_at: string;
}

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  extracted_text: string;
  uploaded_at: string;
}

export interface SavedJob {
  id: number;
  job: Job;
  saved_at: string;
}

export interface RecommendationItem {
  job: Job;
  similarity: number;
  matching_skills: string[];
  missing_skills: string[];
  explanation: string;
}

export interface RecommendationHistoryItem {
  id: number;
  job_id: number;
  similarity: number;
  explanation: string;
  matching_skills: string;
  missing_skills: string;
  created_at: string;
}

export interface SkillGap {
  job_id: number;
  matching_skills: string[];
  missing_skills: string[];
  suggestions: string;
}
