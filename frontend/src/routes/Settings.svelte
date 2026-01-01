<script>
  import { onMount } from "svelte";
  import { getSettings, updateSettings, checkModels } from "../lib/api.js";
  import { userSettings, successMessage, errorMessage } from "../lib/stores.js";

  let settings = {
    openai_api_key: "",
    openai_base_url: "https://api.openai.com/v1",
    model_name: "gpt-4o-mini",
    sheet_name: "일보_DPU",
    column_name: "Issue",
    prompt: "",
    few_shot_examples: "",
  };
  let availableModels = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
  ];
  let fetchingModels = false;

  let loading = true;
  let saving = false;

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    loading = true;
    try {
      settings = await getSettings();
      userSettings.set(settings);
    } catch (error) {
      errorMessage.set(`설정 불러오기 실패: ${error.message}`);
    } finally {
      loading = false;
    }
  }

  async function handleSave() {
    saving = true;
    errorMessage.set("");
    successMessage.set("");

    try {
      const updated = await updateSettings(settings);
      userSettings.set(updated);
      successMessage.set("설정이 저장되었습니다.");
    } catch (error) {
      errorMessage.set(
        `설정 저장 실패: ${error.response?.data?.detail || error.message}`,
      );
    } finally {
      saving = false;
    }
  }

  async function fetchModels() {
    if (!settings.openai_base_url || !settings.openai_api_key) {
      errorMessage.set("Base URL과 API Key를 먼저 입력해주세요.");
      return;
    }

    fetchingModels = true;
    errorMessage.set("");
    successMessage.set("");

    try {
      const models = await checkModels(
        settings.openai_base_url,
        settings.openai_api_key,
      );
      if (models && models.length > 0) {
        availableModels = models;
        // 중복 제거 및 정렬
        availableModels = [...new Set(availableModels)].sort();
        successMessage.set(
          `모델 목록을 성공적으로 불러왔습니다. (${models.length}개)`,
        );
      } else {
        errorMessage.set("불러온 모델 목록이 비어있습니다.");
      }
    } catch (error) {
      errorMessage.set(
        `모델 목록 불러오기 실패: ${error.response?.data?.detail || error.message}`,
      );
    } finally {
      fetchingModels = false;
    }
  }
</script>

<div class="max-w-5xl mx-auto space-y-6">
  {#if loading}
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body items-center py-16">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="mt-4">설정을 불러오는 중...</p>
      </div>
    </div>
  {:else}
    <!-- OpenAI Settings -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-7 h-7"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
            />
          </svg>
          LLM API 설정
        </h2>
        <p class="text-sm text-base-content/60 mb-4">
          분류에 사용할 LLM API 설정을 입력하세요
        </p>

        <div class="alert alert-warning mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="stroke-current shrink-0 w-6 h-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <span class="text-sm"
            >API 키는 안전하게 보관되며, 분류 작업에만 사용됩니다</span
          >
        </div>

        <div class="grid grid-cols-1 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">API Key</span>
              <span class="label-text-alt text-error">필수</span>
            </label>
            <input
              type="password"
              bind:value={settings.openai_api_key}
              placeholder="sk-..."
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt">OpenAI API 키를 입력하세요</span>
            </label>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Base URL</span>
            </label>
            <input
              type="text"
              bind:value={settings.openai_base_url}
              placeholder="https://api.openai.com/v1"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt">OpenAI 호환 API의 Base URL</span>
              <button
                class="btn btn-xs btn-outline btn-primary"
                on:click={fetchModels}
                disabled={fetchingModels}
              >
                {#if fetchingModels}
                  <span class="loading loading-spinner loading-xs"></span>
                {:else}
                  모델 목록 불러오기
                {/if}
              </button>
            </label>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Model Name</span>
            </label>
            <input
              type="text"
              list="model-options"
              class="input input-bordered w-full"
              bind:value={settings.model_name}
              placeholder="모델 이름을 입력하거나 선택하세요"
            />
            <datalist id="model-options">
              {#each availableModels as model}
                <option value={model} />
              {/each}
            </datalist>
            <label class="label">
              <span class="label-text-alt"
                >사용할 모델을 선택하거나 직접 입력하세요</span
              >
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Settings -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-7 h-7"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0118 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 016 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5"
            />
          </svg>
          데이터 설정
        </h2>
        <p class="text-sm text-base-content/60 mb-4">
          Excel 파일의 기본 설정을 입력하세요
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Sheet Name</span>
            </label>
            <input
              type="text"
              bind:value={settings.sheet_name}
              placeholder="일보_DPU"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt">Excel 시트 이름</span>
            </label>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Column Name</span>
            </label>
            <input
              type="text"
              bind:value={settings.column_name}
              placeholder="Issue"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt">분류할 컬럼 이름</span>
            </label>
          </div>
        </div>

        <div class="form-control mt-4">
          <label class="label">
            <span class="label-text font-medium">기본 프롬프트</span>
          </label>
          <textarea
            bind:value={settings.prompt}
            placeholder="분류 프롬프트를 입력하세요..."
            class="textarea textarea-bordered h-24"
          ></textarea>
          <label class="label">
            <span class="label-text-alt">파일 분류 시 사용할 기본 프롬프트</span
            >
          </label>
        </div>
      </div>
    </div>

    <!-- Few-Shot Examples -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-7 h-7"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
            />
          </svg>
          Few-Shot Learning
        </h2>
        <p class="text-sm text-base-content/60 mb-4">
          LLM의 분류 성능을 향상시키기 위한 예제를 입력하세요 (선택사항)
        </p>

        <div class="form-control">
          <textarea
            bind:value={settings.few_shot_examples}
            placeholder="예제 1:&#10;Issue: 'DPU 불량 발생, 설비명: LINE-A, 조치: 재작업 실시'&#10;결과: &#123;'불량명': 'DPU 불량', '설비명': 'LINE-A', '조치내용': '재작업 실시'&#125;&#10;&#10;예제 2:&#10;..."
            class="textarea textarea-bordered h-32"
          ></textarea>
          <label class="label">
            <span class="label-text-alt"
              >분류 예제를 입력하면 AI가 더 정확하게 분류합니다</span
            >
          </label>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <button
          class="btn btn-primary btn-lg w-full gap-2"
          on:click={handleSave}
          disabled={saving}
        >
          {#if saving}
            <span class="loading loading-spinner"></span>
            저장 중...
          {:else}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-6 h-6"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            설정 저장
          {/if}
        </button>
      </div>
    </div>
  {/if}
</div>
