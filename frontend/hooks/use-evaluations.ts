import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEvaluationStore } from "@/stores/evaluation-store";
import type { Evaluation, EvaluationConfig } from "@/types/api";

export function useEvaluations() {
  const queryClient = useQueryClient();
  const {
    evaluations,
    isLoading: storeLoading,
    error,
    fetchEvaluations,
    createEvaluation: storeCreateEvaluation,
    updateEvaluation: storeUpdateEvaluation,
    deleteEvaluation: storeDeleteEvaluation,
    clearError,
  } = useEvaluationStore();

  const evaluationsQuery = useQuery({
    queryKey: ["evaluations"],
    queryFn: async () => {
      await fetchEvaluations();
      return evaluations;
    },
    staleTime: 30000, // 30 seconds
  });

  const createMutation = useMutation({
    mutationFn: async (config: EvaluationConfig) => {
      return await storeCreateEvaluation(config);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({
      id,
      updates,
    }: {
      id: string;
      updates: Partial<Evaluation>;
    }) => {
      await storeUpdateEvaluation(id, updates);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
      queryClient.invalidateQueries({
        queryKey: ["evaluation", variables.id],
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await storeDeleteEvaluation(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
    },
  });

  return {
    evaluations,
    isLoading:
      storeLoading ||
      evaluationsQuery.isLoading ||
      createMutation.isPending ||
      updateMutation.isPending ||
      deleteMutation.isPending,
    error:
      error ||
      evaluationsQuery.error ||
      createMutation.error ||
      updateMutation.error ||
      deleteMutation.error,
    createEvaluation: createMutation.mutate,
    updateEvaluation: updateMutation.mutate,
    deleteEvaluation: deleteMutation.mutate,
    refetch: evaluationsQuery.refetch,
    clearError,
  };
}

export function useEvaluation(id: string) {
  const queryClient = useQueryClient();
  const {
    currentEvaluation,
    isLoading,
    error,
    fetchEvaluationById,
    updateEvaluation: storeUpdateEvaluation,
  } = useEvaluationStore();

  const evaluationQuery = useQuery({
    queryKey: ["evaluation", id],
    queryFn: async () => {
      await fetchEvaluationById(id);
      return currentEvaluation;
    },
    enabled: !!id,
    staleTime: 10000, // 10 seconds
  });

  const updateMutation = useMutation({
    mutationFn: async (updates: Partial<Evaluation>) => {
      await storeUpdateEvaluation(id, updates);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", id] });
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
    },
  });

  return {
    evaluation: currentEvaluation,
    isLoading: isLoading || evaluationQuery.isLoading || updateMutation.isPending,
    error: error || evaluationQuery.error || updateMutation.error,
    updateEvaluation: updateMutation.mutate,
    refetch: evaluationQuery.refetch,
  };
}
