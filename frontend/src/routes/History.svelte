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
        // 분류 결과를 store에 설정
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

        // 결과 탭으로 이동
        currentTab.set("result");
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString("ko-KR");
    }

    function getStatusBadgeClass(status) {
        switch (status) {
            case "completed":
                return "status-completed";
            case "processing":
                return "status-processing";
            case "failed":
                return "status-failed";
            default:
                return "";
        }
    }

    function getStatusText(status) {
        switch (status) {
            case "completed":
                return "✓ 완료";
            case "processing":
                return "⏳ 진행 중";
            case "failed":
                return "✗ 실패";
            default:
                return status;
        }
    }
</script>

<div class="container">
    <div class="card">
        <h2>
            <span>📑 이력 조회</span>
            <button class="refresh-btn" on:click={loadHistory}>
                🔄 새로고침
            </button>
        </h2>

        {#if loading}
            <div class="loading">
                <p>이력을 불러오는 중...</p>
            </div>
        {:else if histories.length === 0}
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <p>아직 분류 이력이 없습니다.</p>
                <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                    파일 업로드 탭에서 첫 번째 분류를 시작하세요.
                </p>
            </div>
        {:else}
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>파일명</th>
                            <th>시트/컬럼</th>
                            <th>상태</th>
                            <th>통계</th>
                            <th>작성일시</th>
                            <th>작업</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each histories as history}
                            <tr>
                                <td>#{history.id}</td>
                                <td>{history.filename}</td>
                                <td>
                                    <div style="font-size: 0.875rem;">
                                        <div>{history.sheet_name}</div>
                                        <div style="color: #a0aec0;">
                                            {history.column_name}
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span
                                        class="status-badge {getStatusBadgeClass(
                                            history.status,
                                        )}"
                                    >
                                        {getStatusText(history.status)}
                                    </span>
                                </td>
                                <td>
                                    <div class="stats-text">
                                        전체: {history.total_rows} / 성공: {history.processed_rows}
                                        / 실패: {history.failed_rows}
                                    </div>
                                </td>
                                <td>{formatDate(history.created_at)}</td>
                                <td>
                                    <button
                                        class="view-btn"
                                        on:click={() => viewResult(history)}
                                    >
                                        👁️ 결과 보기
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

<style>
    .container {
        max-width: 1200px;
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    h2 {
        margin: 0 0 1.5rem 0;
        color: #1a1a1a;
        font-size: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .refresh-btn {
        background: #e6e6fa;
        color: #667eea;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .refresh-btn:hover {
        background: #d0d0f0;
    }

    .loading {
        text-align: center;
        padding: 3rem;
        color: #a0aec0;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #a0aec0;
    }

    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .table-container {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    thead {
        background: #f7fafc;
    }

    th {
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: #4a5568;
        border-bottom: 2px solid #e2e8f0;
    }

    td {
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }

    tbody tr:hover {
        background: #f7fafc;
    }

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-completed {
        background: #c6f6d5;
        color: #22543d;
    }

    .status-processing {
        background: #feebc8;
        color: #7c2d12;
    }

    .status-failed {
        background: #fed7d7;
        color: #742a2a;
    }

    .view-btn {
        background: #667eea;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .view-btn:hover {
        background: #5568d3;
        transform: translateY(-1px);
    }

    .stats-text {
        color: #718096;
        font-size: 0.875rem;
    }
</style>
