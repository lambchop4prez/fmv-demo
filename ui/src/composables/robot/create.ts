import type { RequestBodyOption } from 'openapi-fetch';
import type { paths } from '~/client/api';
import client from '~/lib';

interface CreateRobotError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

type CreateRobotOptions<T> = RequestBodyOption<T>;
type RobotProfile = paths['/robot/']['post']['responses']['201']['content']['application/json'];

export function useCreateRobot() {
  const createRobot = ref<RobotProfile>({ name: "", is_great: false, location: "", description: "", tasks: null });
  const isReady = ref(false);
  const isPosting = ref(false);

  const error = ref<CreateRobotError[] | undefined>();
  async function create(options: CreateRobotOptions<paths['/robot/']['post']>) {
    error.value = undefined;
    isReady.value = false;
    isPosting.value = true;
    try {
      const { data, error: postError } = await client.POST('/robot/', options);
      if (postError) {
        error.value = postError.detail
      }
      else {
        createRobot.value = data;
        isReady.value = true;
      }
    }
    catch (err) {
      error.value = [{ msg: (err as Error).message, loc: [], type: "HTTP" }]
    }
    isPosting.value = false;
  }
  return {
    createRobot,
    isReady,
    isPosting,
    error,
    create
  };
}
