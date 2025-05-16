<script lang="ts">
  import { onDestroy } from 'svelte';
  import RecordRTC, { StereoAudioRecorder } from 'recordrtc';

  let recorder: any = null;
  let mediaStream: MediaStream | null = null;
  let audioUrl: string | null = null;
  let isRecording = false;
  let timer: any = null;

  let messages: any[] = [];

  // 5초 녹음 시작
  async function startRecording() {
    if (isRecording) return;
    try {
      // 샘플레이트와 채널 지정
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1
        }
      });

      recorder = new RecordRTC(mediaStream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: StereoAudioRecorder,
        desiredSampRate: 16000,
        numberOfAudioChannels: 1,
        timeSlice: 5000
      });

      recorder.startRecording();
      isRecording = true;

      // 5초 후 자동 정지
      timer = setTimeout(() => stopRecording(), 5000);
    } catch (err) {
      messages = [...messages, { role: 'system', content: '녹음 오류: ' + err }];
    }
  }

  // 녹음 정지 및 서버 전송
  async function stopRecording() {
    if (!recorder || !isRecording) return;

    recorder.stopRecording(async () => {
      const blob = recorder.getBlob();
      audioUrl = URL.createObjectURL(blob);
      await uploadWav(blob);
      isRecording = false;
      if (timer) clearTimeout(timer);
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
      }
    });
  }

  // WAV 업로드
  async function uploadWav(wavBlob: Blob) {
    const formData = new FormData();
    formData.append('file', wavBlob, 'recording.wav');

    try {
      const response = await fetch('/set-voice-reference', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        messages = [...messages, { role: 'system', content: '음성 업로드 성공' }];
      } else {
        messages = [...messages, { role: 'system', content: '업로드 실패' }];
      }
    } catch (error) {
      messages = [...messages, { role: 'system', content: '업로드 오류' }];
    }
  }

  onDestroy(() => {
    if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
  });
</script>

<div class="h-screen flex flex-col max-w-md mx-auto">
  <div class="flex-1 overflow-auto p-2 space-y-2">
    {#each messages as msg}
      <div class="max-w-[85%] px-3 py-2 text-sm break-words
        {msg.role === 'user' ? 'ml-auto bg-gray-100' : 'mr-auto'}">
        {msg.content}
      </div>
    {/each}
  </div>

  <div class="flex gap-2 p-2 border-t">
    <button
      class="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200"
      on:click={isRecording ? stopRecording : startRecording}
      disabled={isRecording}
    >
      {isRecording ? '녹음 중... (5초)' : '녹음 시작'}
    </button>
    {#if audioUrl}
      <audio controls src={audioUrl}></audio>
      <a href={audioUrl} download="test.wav" class="px-2 text-xs text-blue-500 underline">WAV 다운로드</a>
    {/if}
  </div>
</div>
