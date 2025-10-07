import type { ParamsOption, RequestBodyOption } from 'openapi-fetch';
import type { paths } from '~/client/api';
import client from '~/lib';

interface AppError {
  code: number
  message: string
}

type RobotQueryOptions<T> = ParamsOption<T> & RequestBodyOption<T>;

type RobotListResponse = paths['/api/v1/robot/']['get']['responses']['200']['content']['application/json'];

export function useRobotList(fetchOptions: RobotQueryOptions<paths['/api/v1/robot/']['get']>) {
  const state = ref<RobotListResponse>();
  const isReady = ref(false);
  const isFetching = ref(false);
  const error = ref<AppError | undefined>(undefined);

  async function execute() {
    error.value = undefined;
    isReady.value = false;
    isFetching.value = true;
    const { data, error: fetchError } = await client.GET('/api/v1/robot/', fetchOptions);
    if (fetchError) {
      error.value = fetchError;
    }
    else {
      state.value = data;
      isReady.value = true;
    }
    isFetching.value = false;
  }
  execute();
  return {
    state,
    isReady,
    isFetching,
    error,
    execute,
  };
};
