<script>
    import { onMount } from "svelte";
    import { classificationResult } from "../lib/stores.js";
    import { downloadResult } from "../lib/api.js";

    let result = null;

    classificationResult.subscribe((value) => {
        result = value;
    });

    function handleDownload() {
        if (result && result.history_id) {
            downloadResult(result.history_id);
        }
    }
</script>

<div class="container">
    <div class="card">
        <h2>📋 분류 결과</h2>

        {#if !result}
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <p>아직 분류 결과가 없습니다.</p>
                <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                    파일 업로드 탭에서 파일을 업로드하고 분류를 실행하세요.
                </p>
            </div>
        {:else}
            <div class="result-header">
                <div class="result-info">
                    <h3>{result.filename}</h3>
                    <p>History ID: {result.history_id}</p>
                </div>
                <div class="status-badge status-{result.status}">
                    {result.status === "completed"
                        ? "✓ 완료"
                        : result.status === "processing"
                          ? "⏳ 진행 중"
                          : "✗ 실패"}
                </div>
            </div>

            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{result.total_rows}</div>
                    <div class="stat-label">전체 행 수</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{result.processed_rows}</div>
                    <div class="stat-label">처리 성공</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{result.failed_rows}</div>
                    <div class="stat-label">처리 실패</div>
                </div>
            </div>

            {#if result.message}
                <div
                    style="background: #ebf8ff; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;"
                >
                    <p style="margin: 0; color: #2c5282;">{result.message}</p>
                </div>
            {/if}

            {#if result.status === "completed" && result.result_path}
                <div class="actions">
                    <button class="btn" on:click={handleDownload}>
                        💾 결과 파일 다운로드
                    </button>
                </div>
            {/if}
        {/if}
    </div>
</div>

<style>
    .container {
        max-width: 1000px;
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

    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
    }

    .result-info h3 {
        margin: 0 0 0.5rem 0;
        color: #2d3748;
    }

    .result-info p {
        margin: 0;
        color: #718096;
    }

    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
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

    .stats {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
    }

    .stat-item {
        flex: 1;
        background: #f7fafc;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        color: #718096;
        font-size: 0.875rem;
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
    }

    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
</style>
