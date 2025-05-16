<script lang="ts">
  import { VoiceModalStore } from './store';
  import { onDestroy } from 'svelte';

  let mediaRecorder: MediaRecorder | null = null;
  let audioChunks: BlobPart[] = [];
  let audioBlob: Blob | null = null;
  let audioUrl: string | null = null;
  let recording = false;
  let finished = false;
  let remainingTime = 5;
  let countdownInterval: ReturnType<typeof setInterval> | null = null;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  async function startRecording() {
    audioChunks = [];
    audioBlob = null;
    audioUrl = null;
    finished = false;
    remainingTime = 5;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e: BlobEvent) => {
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      audioUrl = URL.createObjectURL(audioBlob);
      finished = true;
      recording = false;
      // 스트림 정리
      stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();
    recording = true;

    // 5초 후 자동 중지
    timeoutId = setTimeout(() => {
      mediaRecorder?.stop();
    }, 5000);

    // 카운트다운
    countdownInterval = setInterval(() => {
      remainingTime -= 1;
      if (remainingTime <= 0 && countdownInterval) {
        clearInterval(countdownInterval);
      }
    }, 1000);
  }

  function handleSubmit() {
    $VoiceModalStore?.resolver?.(audioBlob);
    VoiceModalStore.set(null);
  }

  function handleCancel() {
    if (recording) {
      mediaRecorder?.stop();
    }
    $VoiceModalStore?.resolver?.(null);
    VoiceModalStore.set(null);
  }

  // 컴포넌트 언마운트 시 타이머 정리
  onDestroy(() => {
    if (timeoutId) clearTimeout(timeoutId);
    if (countdownInterval) clearInterval(countdownInterval);
    if (recording) mediaRecorder?.stop();
  });
</script>

<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-8 min-w-[320px] max-w-[90vw] shadow-lg">
    <h2 class="text-xl font-bold mb-6">음성 녹음</h2>
    <div class="flex flex-col items-center gap-4 min-h-[120px]">
      {#if !recording && !finished}
        <button
          class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
          on:click={startRecording}
        >녹음 시작</button>
      {/if}
      {#if recording}
        <div class="animate-pulse text-gray-500">녹음 중... ({remainingTime}초 남음)</div>
      {/if}
      {#if finished && audioUrl}
        <audio controls src={audioUrl} class="w-full mt-4"></audio>
      {/if}
    </div>
    <div class="flex gap-3 justify-end mt-6">
      <button type="button" class="px-4 py-2 rounded border bg-gray-100 hover:bg-gray-200" on:click={handleCancel}>취소</button>
      <button
        type="button"
        class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
        disabled={!audioBlob}
        on:click={handleSubmit}
      >확인</button>
    </div>
  </div>
</div>
