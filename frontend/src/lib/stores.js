import { writable } from 'svelte/store';

// 현재 탭
export const currentTab = writable('upload');

// 분류 결과 데이터
export const classificationResult = writable(null);

// 사용자 설정
export const userSettings = writable({
    openai_api_key: '',
    openai_base_url: 'https://api.openai.com/v1',
    model_name: 'gpt-4o-mini',
    sheet_name: '일보_DPU',
    column_name: 'Issue',
    few_shot_examples: ''
});

// 로딩 상태
export const isLoading = writable(false);

// 에러 메시지
export const errorMessage = writable('');

// 성공 메시지
export const successMessage = writable('');
