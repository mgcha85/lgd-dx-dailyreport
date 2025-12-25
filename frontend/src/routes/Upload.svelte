<script>
    import { uploadFile, classifyFile } from "../lib/api.js";
    import {
        userSettings,
        classificationResult,
        currentTab,
        isLoading,
        errorMessage,
        successMessage,
    } from "../lib/stores.js";

    let selectedFile = null;
    let fileName = "";
    let prompt =
        "다음 Issue 내용을 분석하여 불량명, 설비명, 조치내용을 JSON 형식으로 추출해주세요.";
    let sheetName = "";
    let columnName = "";
    let uploading = false;
    let classifying = false;
    let dragActive = false;

    $: sheetName = $userSettings.sheet_name || "일보_DPU";
    $: columnName = $userSettings.column_name || "Issue";

    function handleDragOver(e) {
        e.preventDefault();
        dragActive = true;
    }

    function handleDragLeave(e) {
        e.preventDefault();
        dragActive = false;
    }

    function handleDrop(e) {
        e.preventDefault();
        dragActive = false;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            selectedFile = files[0];
            fileName = files[0].name;
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            selectedFile = files[0];
            fileName = files[0].name;
        }
    }

    async function handleUploadAndClassify() {
        if (!selectedFile) {
            errorMessage.set("파일을 선택해주세요.");
            return;
        }

        errorMessage.set("");
        successMessage.set("");
        uploading = true;

        try {
            // 파일 업로드
            const uploadResult = await uploadFile(selectedFile);
            successMessage.set(
                `파일이 업로드되었습니다: ${uploadResult.filename}`,
            );

            uploading = false;
            classifying = true;

            // 분류 실행
            const classifyData = {
                file_path: uploadResult.file_path,
                sheet_name: sheetName,
                column_name: columnName,
                prompt: prompt,
            };

            const classifyResult = await classifyFile(classifyData);

            classificationResult.set(classifyResult);
            successMessage.set(
                `분류가 완료되었습니다! (성공: ${classifyResult.processed_rows}, 실패: ${classifyResult.failed_rows})`,
            );

            // 결과 탭으로 이동
            setTimeout(() => {
                currentTab.set("result");
            }, 1500);
        } catch (error) {
            errorMessage.set(
                `오류 발생: ${error.response?.data?.detail || error.message}`,
            );
        } finally {
            uploading = false;
            classifying = false;
        }
    }
</script>

<div class="container">
    <div class="card">
        <h2>📤 파일 업로드</h2>

        <div
            class="upload-area"
            class:active={dragActive}
            on:dragover={handleDragOver}
            on:dragleave={handleDragLeave}
            on:drop={handleDrop}
            on:click={() => document.getElementById("fileInput").click()}
        >
            <div class="upload-icon">📁</div>
            <p class="upload-text">클릭하거나 파일을 여기로 드래그하세요</p>
            <p class="upload-subtext">
                Excel (.xlsx, .xls) 또는 PowerPoint (.pptx) 파일
            </p>

            <input
                id="fileInput"
                type="file"
                class="file-input"
                accept=".xlsx,.xls,.pptx"
                on:change={handleFileSelect}
            />
        </div>

        {#if selectedFile}
            <div class="selected-file">
                <span>📄</span>
                <strong>{fileName}</strong>
            </div>
        {/if}
    </div>

    <div class="card">
        <h2>⚙️ 분류 설정</h2>

        <div class="form-group">
            <label for="sheetName">시트 이름</label>
            <input
                id="sheetName"
                type="text"
                bind:value={sheetName}
                placeholder="일보_DPU"
            />
        </div>

        <div class="form-group">
            <label for="columnName">컬럼 이름</label>
            <input
                id="columnName"
                type="text"
                bind:value={columnName}
                placeholder="Issue"
            />
        </div>

        <div class="form-group">
            <label for="prompt">프롬프트</label>
            <textarea
                id="prompt"
                bind:value={prompt}
                placeholder="분류 프롬프트를 입력하세요..."
            ></textarea>
        </div>

        <button
            class="btn"
            on:click={handleUploadAndClassify}
            disabled={uploading || classifying}
        >
            {#if uploading}
                <span class="loading"></span> 파일 업로드 중...
            {:else if classifying}
                <span class="loading"></span> 분류 진행 중...
            {:else}
                🚀 업로드 및 분류 시작
            {/if}
        </button>
    </div>
</div>

<style>
    .container {
        max-width: 700px;
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }

    h2 {
        margin: 0 0 1.5rem 0;
        color: #1a1a1a;
        font-size: 1.5rem;
    }

    .upload-area {
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }

    .upload-area.active {
        border-color: #667eea;
        background: #f0f3ff;
    }

    .upload-area:hover {
        border-color: #667eea;
        background: #fafbff;
    }

    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .upload-text {
        color: #4a5568;
        margin-bottom: 0.5rem;
    }

    .upload-subtext {
        color: #a0aec0;
        font-size: 0.875rem;
    }

    .file-input {
        display: none;
    }

    .selected-file {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
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

    input[type="text"],
    textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        font-size: 0.95rem;
        transition: border-color 0.2s;
    }

    input[type="text"]:focus,
    textarea:focus {
        outline: none;
        border-color: #667eea;
    }

    textarea {
        min-height: 100px;
        resize: vertical;
        font-family: inherit;
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
        display: inline-block;
        width: 16px;
        height: 16px;
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
</style>
