<script>
  import { onMount } from "svelte";
  import { getSettings, updateSettings } from "../lib/api.js";
  import { userSettings, successMessage, errorMessage } from "../lib/stores.js";

  let settings = {
    openai_api_key: "",
    openai_base_url: "https://api.openai.com/v1",
    model_name: "gpt-4o-mini",
    sheet_name: "일보_DPU",
    column_name: "Issue",
    few_shot_examples: "",
  };

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
</script>

<div class="container">
  {#if loading}
    <div class="card">
      <div class="loading">
        <p>설정을 불러오는 중...</p>
      </div>
    </div>
  {:else}
    <div class="card">
      <h2>🤖 OpenAI API 설정</h2>
      <p class="section-description">
        LLM 분류에 사용할 OpenAI API 설정을 입력하세요.
      </p>

      <div class="warning-box">
        <p>⚠️ API 키는 안전하게 보관되며, 분류 작업에만 사용됩니다.</p>
      </div>

      <div class="form-group">
        <label for="apiKey">API Key</label>
        <input
          id="apiKey"
          type="password"
          bind:value={settings.openai_api_key}
          placeholder="sk-..."
        />
        <div class="help-text">OpenAI API 키를 입력하세요</div>
      </div>

      <div class="form-group">
        <label for="baseUrl">Base URL</label>
        <input
          id="baseUrl"
          type="text"
          bind:value={settings.openai_base_url}
          placeholder="https://api.openai.com/v1"
        />
        <div class="help-text">
          OpenAI API Base URL (기본값: https://api.openai.com/v1)
        </div>
      </div>

      <div class="form-group">
        <label for="modelName">Model Name</label>
        <input
          id="modelName"
          type="text"
          bind:value={settings.model_name}
          placeholder="gpt-4o-mini"
        />
        <div class="help-text">
          사용할 모델 이름 (예: gpt-4o-mini, gpt-4, gpt-3.5-turbo)
        </div>
      </div>
    </div>

    <div class="card">
      <h2>📊 데이터 설정</h2>
      <p class="section-description">
        엑셀 파일의 기본 시트명과 분류할 컬럼명을 설정하세요.
      </p>

      <div class="form-group">
        <label for="sheetName">Sheet Name</label>
        <input
          id="sheetName"
          type="text"
          bind:value={settings.sheet_name}
          placeholder="일보_DPU"
        />
        <div class="help-text">엑셀 시트 이름 (기본값: 일보_DPU)</div>
      </div>

      <div class="form-group">
        <label for="columnName">Column Name</label>
        <input
          id="columnName"
          type="text"
          bind:value={settings.column_name}
          placeholder="Issue"
        />
        <div class="help-text">분류할 컬럼 이름 (기본값: Issue)</div>
      </div>
    </div>

    <div class="card">
      <h2>💡 Few-Shot Examples</h2>
      <p class="section-description">
        LLM 분류 성능을 향상시키기 위한 예제를 입력하세요.
      </p>

      <div class="form-group">
        <label for="fewShot">Few-Shot Examples</label>
        <textarea
          id="fewShot"
          bind:value={settings.few_shot_examples}
          placeholder="예제 1:&#10;Issue: 'DPU 불량 발생, 설비명: LINE-A, 조치: 재작업 실시'&#10;결과: &#123;'불량명': 'DPU 불량', '설비명': 'LINE-A', '조치내용': '재작업 실시'&#125;&#10;&#10;예제 2:&#10;..."
        ></textarea>
        <div class="help-text">분류 예제를 입력하세요 (선택사항)</div>
      </div>
    </div>

    <div class="card">
      <button class="btn" on:click={handleSave} disabled={saving}>
        {#if saving}
          <span class="loading-spinner"></span> 저장 중...
        {:else}
          💾 설정 저장
        {/if}
      </button>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 800px;
  }

  .card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.5rem;
  }

  h2 {
    margin: 0 0 1rem 0;
    color: #1a1a1a;
    font-size: 1.5rem;
  }

  .section-description {
    color: #718096;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #4a5568;
    font-weight: 500;
  }

  .help-text {
    font-size: 0.875rem;
    color: #a0aec0;
    margin-top: 0.25rem;
  }

  input[type="text"],
  input[type="password"],
  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #cbd5e0;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: border-color 0.2s;
    font-family: inherit;
  }

  input[type="text"]:focus,
  input[type="password"]:focus,
  textarea:focus {
    outline: none;
    border-color: #667eea;
  }

  textarea {
    min-height: 150px;
    resize: vertical;
  }

  .btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.875rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition:
      transform 0.2s,
      box-shadow 0.2s;
    width: 100%;
  }

  .btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: #a0aec0;
  }

  .loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid #fff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .warning-box {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .warning-box p {
    margin: 0;
    color: #92400e;
    font-size: 0.875rem;
  }
</style>
