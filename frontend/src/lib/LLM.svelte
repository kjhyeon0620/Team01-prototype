<script lang="ts">

	// configuration 

	let thread_id = crypto.randomUUID()






	// type

	type Message = {
		role: 'user' | 'assistant';
		content: string;
		type?: string;
	};


	const apiKey = "sk_6385f249516d6f10760e51fd6d526a9107a29ad175714db5";
	const voiceId = "AW5wrnG1jVizOYY7R1Oo";


	async function generateAndPlayTTS({apiKey,voiceId,text,gain = 5, // (1.0 = 원본)
	}: any) {
	try {
		// 1. API 호출
		const response = await fetch(
		`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}?output_format=mp3_44100_128`,
		{
			method: "POST",
			headers: {
			"Content-Type": "application/json",
			"xi-api-key": apiKey,
			Accept: "audio/mpeg",
			},
			body: JSON.stringify({
			text,
			model_id: 'eleven_multilingual_v2',
			}),
		}
		);

		if (!response.ok) {
		const errorData = await response.json();
		throw new Error(`TTS API Error: ${errorData.detail?.message || 'Unknown error'}`);
		}

		const audioContext = new AudioContext();
		const arrayBuffer = await response.arrayBuffer();
		const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
		
		const gainNode = audioContext.createGain();
		gainNode.gain.value = Math.min(Math.max(gain, 0.1), 5.0); // 0.1~5.0 범위 제한
		
		const source = audioContext.createBufferSource();
		source.buffer = audioBuffer;
		source.connect(gainNode).connect(audioContext.destination);
		
		if (audioContext.state === 'suspended') {
		await audioContext.resume();
		}
		
		source.start(0);

	} catch (error) {
		console.error("TTS 재생 실패:", error);
		throw error; 
	}
	}


	// llm stream function

	let messages = $state<Message[]>([{ role: 'assistant', content: '안녕하세요!' }]);
	let input    = $state('');
	let chatContainer: HTMLDivElement;


	async function createStream(query: string | object, thread_id: string, APPROVAL_ALLOW: boolean = true) {

		if (typeof(query) == 'string')
			messages.push({ role: 'user', content: query });
		else
			messages.push({ role: 'user', content: 'APPROVAL_REQUIRED' });

		const res = await fetch('/stream', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ thread_id: thread_id, query: query})
		})

		if (!res.body) return
		const reader  = res.body.getReader()
		const decoder = new TextDecoder()
		
		let currentMessage: Message | null = null
		
		
		while (true) {
			const { value, done } = await reader.read()
			if (done) break

			const chunk = decoder.decode(value)
			for(let line of chunk.split('\n\n')) {

				if(!line.startsWith('data: ')) continue
				const content = line.slice(6); // delete "data: "
				if (content === '[DONE]') continue
				


				// NOT APPROVAL_REQUIRED
				if (/^\[TOOL_END\](.*)\[\/TOOL_END\]$/.test(content)) { 
					const toolContent = JSON.parse(content.match(/^\[TOOL_END\](.*)\[\/TOOL_END\]$/)![1]);
					console.log(toolContent)
    				messages.push({ role: 'assistant', content: toolContent.name, type: 'tool' });
				}
				// APPROVAL_REQUIRED
				else if (/^\[APPROVAL_REQUIRED\](.*)\[\/APPROVAL_REQUIRED\]$/.test(content)) {

					if (APPROVAL_ALLOW) {
						const [_, name, parameters] = content.match(/\[APPROVAL_REQUIRED\](.*?):\s*(\{.*\})\[\/APPROVAL_REQUIRED\]/) || [];
	
						if (name && parameters)
							return { name, parameters : JSON.parse(parameters) }
					}else {
						const toolContent = content.match(/^\[APPROVAL_REQUIRED\](.*)\[\/APPROVAL_REQUIRED\]$/)![1];
    					messages.push({ role: 'assistant', content: toolContent, type: 'tool' });
					}
				}
				// 일반 텍스트 처리 
				else {
					if (!currentMessage) {				
						currentMessage = { role: 'assistant', content };
						messages.push(currentMessage);
					} else messages[messages.length-1].content = messages[messages.length-1].content + content;
				}

			}
		}
		// generateAndPlayTTS({apiKey, voiceId, text:messages[messages.length-1].content})
		setTimeout(() => chatContainer?.scrollTo({ top: chatContainer.scrollHeight }), 0);
		return null

	}


	import { ApprovalModalStore, openApprovalModal, DepositWarningModalStore, openDepositWarningModal } from './store'
	import ApprovalModal from './ApprovalModal.svelte'
	import DepositWarningModal from './DepositWarningModal.svelte'

	// 기준 비용
	let exceedLimit = 50000;

	async function sendMessage() {

		const text = input.trim();
		const APPROVAL_REQUIRED = await createStream(text, thread_id)
		if (APPROVAL_REQUIRED) {
			if (APPROVAL_REQUIRED.parameters.amount >= exceedLimit) {
				await openDepositWarningModal(APPROVAL_REQUIRED.name, APPROVAL_REQUIRED.parameters, exceedLimit);
			}
			
			const result = await openApprovalModal(APPROVAL_REQUIRED.name, APPROVAL_REQUIRED.parameters);

			await createStream(result || {'address' : '', amount : 0}, thread_id, false)
		}

	}

	const onKeydown = (e: KeyboardEvent) => e.key === 'Enter' && sendMessage();


</script>





<div class="h-screen flex flex-col max-w-md mx-auto">
  <div class="flex-1 overflow-auto p-2 space-y-2" bind:this={chatContainer}>
	{#each messages as msg}
	  <div class="max-w-[85%] px-3 py-2 text-sm break-words
		{msg.role === 'user'
		  ? 'ml-auto bg-gray-100'
		  : 'mr-auto'}">
		{#if msg.type == 'tool'}<span class="text-xs text-gray-500">[시스템]</span><br>{/if}
		{msg.content}
	  </div>
	{/each}
  </div>

  <div class="flex gap-2 p-2 border-t">
	<input
	  class="flex-1 px-3 py-2 border text-sm"
	  bind:value={input}
	  placeholder="메시지 입력"
	  onkeydown={onKeydown}
	/>
	<button
	  onclick={sendMessage}
	  class="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200"
	>전송</button>
  </div>
</div>





{#if $ApprovalModalStore}
  <ApprovalModal name={$ApprovalModalStore.name} parameters={$ApprovalModalStore.parameters} />
{/if}
{#if $DepositWarningModalStore}
  <DepositWarningModal name={$DepositWarningModalStore.name} parameters={$DepositWarningModalStore.parameters} exceedLimit={exceedLimit} />
{/if}
