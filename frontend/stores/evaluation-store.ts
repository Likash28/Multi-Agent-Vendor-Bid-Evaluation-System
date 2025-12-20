import { create } from "zustand";
import api from "@/lib/api";
import type { Evaluation, EvaluationConfig } from "@/types/api";

interface EvaluationState {
  currentEvaluation: Evaluation | null;
  evaluations: Evaluation[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentEvaluation: (evaluation: Evaluation | null) => void;
  setEvaluations: (evaluations: Evaluation[]) => void;
  createEvaluation: (config: EvaluationConfig) => Promise<Evaluation>;
  updateEvaluation: (id: string, updates: Partial<Evaluation>) => Promise<void>;
  fetchEvaluations: () => Promise<void>;
  fetchEvaluationById: (id: string) => Promise<void>;
  deleteEvaluation: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useEvaluationStore = create<EvaluationState>((set, get) => ({
  currentEvaluation: null,
  evaluations: [],
  isLoading: false,
  error: null,

  setCurrentEvaluation: (evaluation: Evaluation | null) => {
    set({ currentEvaluation: evaluation });
  },

  setEvaluations: (evaluations: Evaluation[]) => {
    set({ evaluations });
  },

  createEvaluation: async (config: EvaluationConfig) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post<Evaluation>("/evaluations", config);
      const newEvaluation = response.data;

      set((state) => ({
        evaluations: [newEvaluation, ...state.evaluations],
        currentEvaluation: newEvaluation,
        isLoading: false,
      }));

      return newEvaluation;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to create evaluation";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateEvaluation: async (id: string, updates: Partial<Evaluation>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.patch<Evaluation>(
        `/evaluations/${id}`,
        updates
      );
      const updatedEvaluation = response.data;

      set((state) => ({
        evaluations: state.evaluations.map((eval) =>
          eval.id === id ? updatedEvaluation : eval
        ),
        currentEvaluation:
          state.currentEvaluation?.id === id
            ? updatedEvaluation
            : state.currentEvaluation,
        isLoading: false,
      }));
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to update evaluation";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchEvaluations: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<Evaluation[]>("/evaluations");
      set({ evaluations: response.data, isLoading: false });
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to fetch evaluations";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchEvaluationById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get<Evaluation>(`/evaluations/${id}`);
      set({ currentEvaluation: response.data, isLoading: false });
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to fetch evaluation";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteEvaluation: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.delete(`/evaluations/${id}`);
      set((state) => ({
        evaluations: state.evaluations.filter((eval) => eval.id !== id),
        currentEvaluation:
          state.currentEvaluation?.id === id ? null : state.currentEvaluation,
        isLoading: false,
      }));
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to delete evaluation";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
