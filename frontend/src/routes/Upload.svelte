<script>
    import { onMount } from "svelte";
    import { uploadFile, classifyFileWithProgress } from "../lib/api.js";
    import {
        userSettings,
        classificationResult,
        currentTab,
        isLoading,
        errorMessage,
        successMessage,
        uploadedFile,
        classificationProgress,
    } from "../lib/stores.js";

    let uploading = false;
    let classifying = false;
    let dragActive = false;

    // Local reactive variables that sync with stores
    let selectedFile = null;
    let fileName = "";
    let sheetName = "";
    let columnName = "";
    let prompt = "";

    // Progress bar values
    let progress = { current: 0, total: 0, isActive: false };

    // Subscribe to stores
    const unsubscribeFile = uploadedFile.subscribe((value) => {
        selectedFile = value.file;
        fileName = value.fileName;
    });

    const unsubscribeSettings = userSettings.subscribe((value) => {
        sheetName = value.sheet_name || "";
        columnName = value.column_name || "";
        prompt = value.prompt || "";
    });

    const unsubscribeProgress = classificationProgress.subscribe((value) => {
        progress = value;
    });

    // Cleanup subscriptions on destroy
    import { onDestroy } from "svelte";
    onDestroy(() => {
        unsubscribeFile();
        unsubscribeSettings();
        unsubscribeProgress();
    });

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
            setFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            setFile(files[0]);
        }
    }

    function setFile(file) {
        selectedFile = file;
        fileName = file.name;
        uploadedFile.set({ file, fileName: file.name });
    }

    function cancelFileSelection() {
        selectedFile = null;
        fileName = "";
        uploadedFile.set({ file: null, fileName: "" });
        // Reset the file input
        const fileInput = document.getElementById("fileInput");
        if (fileInput) {
            fileInput.value = "";
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
        classificationProgress.set({ current: 0, total: 0, isActive: false });

        try {
            const uploadResult = await uploadFile(selectedFile);
            successMessage.set(
                `파일이 업로드되었습니다: ${uploadResult.filename}`,
            );

            uploading = false;
            classifying = true;

            const classifyData = {
                file_path: uploadResult.file_path,
                sheet_name: sheetName,
                column_name: columnName,
                prompt: prompt,
            };

            // Use streaming classification with progress
            const classifyResult = await classifyFileWithProgress(
                classifyData,
                (progressData) => {
                    classificationProgress.set({
                        current: progressData.current,
                        total: progressData.total,
                        isActive: true,
                    });
                },
            );

            classificationProgress.set({
                current: 0,
                total: 0,
                isActive: false,
            });
            classificationResult.set(classifyResult);
            successMessage.set(
                `분류가 완료되었습니다! (성공: ${classifyResult.processed_rows}, 실패: ${classifyResult.failed_rows})`,
            );

            setTimeout(() => {
                currentTab.set("result");
            }, 1500);
        } catch (error) {
            errorMessage.set(
                `오류 발생: ${error.response?.data?.detail || error.message}`,
            );
            classificationProgress.set({
                current: 0,
                total: 0,
                isActive: false,
            });
        } finally {
            uploading = false;
            classifying = false;
        }
    }
</script>

<div class="max-w-5xl mx-auto space-y-6">
    <!-- Upload Card -->
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
                        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                    />
                </svg>
                파일 업로드
            </h2>

            <div
                class="border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all {dragActive
                    ? 'border-primary bg-primary/10'
                    : 'border-base-300 hover:border-primary/50 hover:bg-base-200'}"
                on:dragover={handleDragOver}
                on:dragleave={handleDragLeave}
                on:drop={handleDrop}
                on:click={() => document.getElementById("fileInput").click()}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                    class="w-16 h-16 mx-auto mb-4 text-primary"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                </svg>

                <p class="text-lg font-medium mb-2">
                    클릭하거나 파일을 여기로 드래그하세요
                </p>
                <p class="text-sm text-base-content/60">
                    Excel (.xlsx, .xls, .xlsb) 또는 PowerPoint (.pptx) 파일
                </p>

                <input
                    id="fileInput"
                    type="file"
                    class="hidden"
                    accept=".xlsx,.xls,.xlsb,.pptx"
                    on:change={handleFileSelect}
                />
            </div>

            {#if selectedFile}
                <div class="alert alert-info flex justify-between items-center">
                    <div class="flex items-center gap-2">
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
                                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <span><strong>{fileName}</strong> 선택됨</span>
                    </div>
                    <button
                        class="btn btn-ghost btn-sm text-error"
                        on:click|stopPropagation={cancelFileSelection}
                        disabled={uploading || classifying}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke-width="1.5"
                            stroke="currentColor"
                            class="w-5 h-5"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                        취소
                    </button>
                </div>
            {/if}
        </div>
    </div>

    <!-- Settings Card -->
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
                        d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"
                    />
                </svg>
                분류 설정
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">시트 이름</span>
                    </label>
                    <input
                        type="text"
                        bind:value={sheetName}
                        placeholder="시트 이름을 입력하세요"
                        class="input input-bordered w-full"
                    />
                </div>

                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">컬럼 이름</span>
                    </label>
                    <input
                        type="text"
                        bind:value={columnName}
                        placeholder="컬럼 이름을 입력하세요"
                        class="input input-bordered w-full"
                    />
                </div>
            </div>

            <div class="form-control">
                <label class="label">
                    <span class="label-text font-medium">프롬프트</span>
                </label>
                <textarea
                    bind:value={prompt}
                    placeholder="분류 프롬프트를 입력하세요..."
                    class="textarea textarea-bordered h-24"
                ></textarea>
            </div>

            <!-- Progress Bar -->
            {#if progress.isActive}
                <div class="mt-4">
                    <div class="flex justify-between mb-2">
                        <span class="text-sm font-medium">분류 진행 중...</span>
                        <span class="text-sm font-medium"
                            >{progress.current} / {progress.total}</span
                        >
                    </div>
                    <progress
                        class="progress progress-primary w-full"
                        value={progress.current}
                        max={progress.total}
                    ></progress>
                    <p class="text-xs text-base-content/60 mt-1">
                        {Math.round((progress.current / progress.total) * 100)}%
                        완료
                    </p>
                </div>
            {/if}

            <div class="card-actions justify-end mt-4">
                <button
                    class="btn btn-primary btn-lg w-full md:w-auto"
                    on:click={handleUploadAndClassify}
                    disabled={uploading || classifying}
                >
                    {#if uploading}
                        <span class="loading loading-spinner"></span>
                        파일 업로드 중...
                    {:else if classifying}
                        <span class="loading loading-spinner"></span>
                        분류 진행 중...
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
                                d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"
                            />
                        </svg>
                        업로드 및 분류 시작
                    {/if}
                </button>
            </div>
        </div>
    </div>
</div>
