<script>
    import { onMount } from "svelte";
    import { currentTab, errorMessage, successMessage } from "./lib/stores.js";
    import Upload from "./routes/Upload.svelte";
    import Result from "./routes/Result.svelte";
    import History from "./routes/History.svelte";
    import Settings from "./routes/Settings.svelte";

    let activeTab = "upload";

    currentTab.subscribe((value) => {
        activeTab = value;
    });

    function setTab(tab) {
        currentTab.set(tab);
        errorMessage.set("");
        successMessage.set("");
    }
</script>

<div class="app">
    <header>
        <h1>📊 일보 자동 분류 시스템</h1>
        <p class="subtitle">LLM을 활용한 제조 현장 일보 자동 분류</p>
    </header>

    <nav>
        <ul class="nav-tabs">
            <li>
                <button
                    class:active={activeTab === "upload"}
                    on:click={() => setTab("upload")}
                >
                    📤 파일 업로드
                </button>
            </li>
            <li>
                <button
                    class:active={activeTab === "result"}
                    on:click={() => setTab("result")}
                >
                    📋 분류 결과
                </button>
            </li>
            <li>
                <button
                    class:active={activeTab === "history"}
                    on:click={() => setTab("history")}
                >
                    📑 이력 조회
                </button>
            </li>
            <li>
                <button
                    class:active={activeTab === "settings"}
                    on:click={() => setTab("settings")}
                >
                    ⚙️ 설정
                </button>
            </li>
        </ul>
    </nav>

    <main>
        {#if $errorMessage}
            <div class="message error">{$errorMessage}</div>
        {/if}

        {#if $successMessage}
            <div class="message success">{$successMessage}</div>
        {/if}

        {#if activeTab === "upload"}
            <Upload />
        {:else if activeTab === "result"}
            <Result />
        {:else if activeTab === "history"}
            <History />
        {:else if activeTab === "settings"}
            <Settings />
        {/if}
    </main>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
            "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans",
            "Helvetica Neue", sans-serif;
        background-color: #f5f7fa;
    }

    .app {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .subtitle {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.9;
    }

    nav {
        background: white;
        border-bottom: 1px solid #e1e8ed;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    .nav-tabs {
        display: flex;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0;
        list-style: none;
    }

    .nav-tabs button {
        background: none;
        border: none;
        padding: 1rem 1.5rem;
        font-size: 0.95rem;
        color: #657786;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
    }

    .nav-tabs button:hover {
        color: #667eea;
        background: #f5f7fa;
    }

    .nav-tabs button.active {
        color: #667eea;
        border-bottom-color: #667eea;
        font-weight: 600;
    }

    main {
        flex: 1;
        max-width: 1200px;
        width: 100%;
        margin: 0 auto;
        padding: 2rem;
    }

    .message {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        animation: slideDown 0.3s ease-out;
    }

    .message.error {
        background: #fee;
        color: #c33;
        border: 1px solid #fcc;
    }

    .message.success {
        background: #efe;
        color: #3c3;
        border: 1px solid #cfc;
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
