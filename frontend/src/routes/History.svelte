<script>
    import { onMount } from "svelte";
    import { getHistory } from "../lib/api.js";
    import {
        classificationResult,
        currentTab,
        errorMessage,
    } from "../lib/stores.js";

    let histories = [];
    let loading = true;

    onMount(async () => {
        await loadHistory();
    });

    async function loadHistory() {
        loading = true;
        try {
            histories = await getHistory();
        } catch (error) {
            errorMessage.set(`이력 조회 실패: ${error.message}`);
        } finally {
            loading = false;
        }
    }

    function viewResult(history) {
        classificationResult.set({
            history_id: history.id,
            filename: history.filename,
            status: history.status,
            total_rows: history.total_rows,
            processed_rows: history.processed_rows,
            failed_rows: history.failed_rows,
            result_path: null,
            message:
                history.error_message ||
                `분류가 ${history.status === "completed" ? "완료" : history.status}되었습니다.`,
        });

        currentTab.set("result");
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString("ko-KR");
    }

    function getStatusClass(status) {
        switch (status) {
            case "completed":
                return "badge-success";
            case "processing":
                return "badge-warning";
            case "failed":
                return "badge-error";
            default:
                return "badge-ghost";
        }
    }

    function getStatusText(status) {
        switch (status) {
            case "completed":
                return "완료";
            case "processing":
                return "진행 중";
            case "failed":
                return "실패";
            default:
                return status;
        }
    }
</script>

<div class="max-w-7xl mx-auto">
    <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
            <div
                class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4"
            >
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
                            d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    이력 조회
                </h2>

                <button
                    class="btn btn-outline btn-sm gap-2"
                    on:click={loadHistory}
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-4 h-4"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
                        />
                    </svg>
                    새로고침
                </button>
            </div>

            {#if loading}
                <div class="flex justify-center items-center py-16">
                    <span
                        class="loading loading-spinner loading-lg text-primary"
                    ></span>
                </div>
            {:else if histories.length === 0}
                <div class="text-center py-16">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-24 h-24 mx-auto text-base-300 mb-4"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M2.25 13.5h3.86a2.25 2.25 0 012.012 1.244l.256.512a2.25 2.25 0 002.013 1.244h3.218a2.25 2.25 0 002.013-1.244l.256-.512a2.25 2.25 0 012.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 00-2.15-1.588H6.911a2.25 2.25 0 00-2.15 1.588L2.35 13.177a2.25 2.25 0 00-.1.661z"
                        />
                    </svg>
                    <h3 class="text-2xl font-bold mb-2">
                        아직 분류 이력이 없습니다
                    </h3>
                    <p class="text-base-content/60">
                        파일 업로드 탭에서 첫 번째 분류를 시작하세요
                    </p>
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="table table-zebra">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>파일명</th>
                                <th class="hidden md:table-cell">시트 / 컬럼</th
                                >
                                <th>상태</th>
                                <th class="hidden lg:table-cell">통계</th>
                                <th class="hidden xl:table-cell">작성일시</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each histories as history}
                                <tr class="hover">
                                    <td>
                                        <div class="font-mono text-sm">
                                            #{history.id}
                                        </div>
                                    </td>
                                    <td>
                                        <div class="flex items-center gap-3">
                                            <div class="avatar placeholder">
                                                <div
                                                    class="bg-neutral text-neutral-content rounded-lg w-12"
                                                >
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
                                                            d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                                                        />
                                                    </svg>
                                                </div>
                                            </div>
                                            <div>
                                                <div class="font-medium">
                                                    {history.filename}
                                                </div>
                                                <div
                                                    class="text-sm opacity-50 md:hidden"
                                                >
                                                    {history.sheet_name} / {history.column_name}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="hidden md:table-cell">
                                        <div class="text-sm">
                                            <div class="font-medium">
                                                {history.sheet_name}
                                            </div>
                                            <div class="opacity-50">
                                                {history.column_name}
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <div
                                            class="badge {getStatusClass(
                                                history.status,
                                            )} gap-2"
                                        >
                                            {#if history.status === "processing"}
                                                <span
                                                    class="loading loading-spinner loading-xs"
                                                ></span>
                                            {/if}
                                            {getStatusText(history.status)}
                                        </div>
                                    </td>
                                    <td class="hidden lg:table-cell">
                                        <div class="text-xs space-y-1">
                                            <div>
                                                전체: <span
                                                    class="font-mono font-bold"
                                                    >{history.total_rows}</span
                                                >
                                            </div>
                                            <div>
                                                성공: <span
                                                    class="font-mono text-success font-bold"
                                                    >{history.processed_rows}</span
                                                >
                                            </div>
                                            <div>
                                                실패: <span
                                                    class="font-mono text-error font-bold"
                                                    >{history.failed_rows}</span
                                                >
                                            </div>
                                        </div>
                                    </td>
                                    <td class="hidden xl:table-cell">
                                        <div class="text-sm opacity-70">
                                            {formatDate(history.created_at)}
                                        </div>
                                    </td>
                                    <td>
                                        <button
                                            class="btn btn-primary btn-sm gap-2"
                                            on:click={() => viewResult(history)}
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke-width="1.5"
                                                stroke="currentColor"
                                                class="w-4 h-4"
                                            >
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                                                />
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                                />
                                            </svg>
                                            보기
                                        </button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </div>
</div>
