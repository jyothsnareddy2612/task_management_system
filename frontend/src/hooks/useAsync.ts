import { useCallback, useState } from "react";

type AsyncState<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
};

export function useAsync<T>() {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const run = useCallback(async (task: () => Promise<T>) => {
    setState((current) => ({ ...current, error: null, isLoading: true }));
    try {
      const data = await task();
      setState({ data, error: null, isLoading: false });
      return data;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Something went wrong";
      setState({ data: null, error: message, isLoading: false });
      throw error;
    }
  }, []);

  return { ...state, run };
}
