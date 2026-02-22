import type { ParamsOption } from 'openapi-fetch';
import type { paths } from '~/client/api';
import client from '~/lib';

interface AppError {
    type: string;
    msg: string
}

type RobotProfileQueryOption<T> = ParamsOption<T>;

type RobotProfileResponse = paths['/api/v1/robot/{name}']['get']['responses']['200']['content']['application/json'];

export function useRobotProfile(fetchOptions: RobotProfileQueryOption<paths['/api/v1/robot/{name}']['get']>) {
    const state = ref<RobotProfileResponse>();
    const isReady = ref(false);
    const isFetching = ref(false);
    const error = ref<AppError[] | undefined>(undefined);

    async function execute() {
        error.value = undefined;
        isReady.value = false;
        isFetching.value = true;
        const { data, error: fetchError } = await client.GET('/api/v1/robot/{name}', fetchOptions);
        if (fetchError) {
            error.value = fetchError.detail;
        }
        else {
            state.value = data;
            isReady.value = true;
        }
        isFetching.value = false;
    }
    return {
        state,
        isReady,
        isFetching,
        error,
        execute
    };
};
