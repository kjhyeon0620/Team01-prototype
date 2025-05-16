<script lang="ts">
  import { DepositWarningModalStore } from './store';
  import { onMount } from 'svelte';

  export let name: string;
  export let parameters: { [key: string]: any };
  export let exceedLimit: number;

  let localData: { [key: string]: any } = {};

  onMount(() => {
    localData = { ...parameters };
  });

  let warningMessage = '';
  $: {
    if (localData.amount != null && localData.balance != null && localData.amount > localData.balance) {
      warningMessage = `💸 현재 보유 금액(${localData.balance.toLocaleString()}원)을 초과하여 ${localData.amount.toLocaleString()}원을 송금하려고 합니다.`;
    }
    else if (localData.amount != null && localData.amount >= exceedLimit) {
      warningMessage = `💸 제한 금액(${exceedLimit.toLocaleString()}원)을 초과하여 ${localData.amount.toLocaleString()}원을 송금하려고 합니다.`;
    }
    else {
      warningMessage = '';
    }
  }

  function handleCheck() {
    $DepositWarningModalStore?.resolver?.(null);
    DepositWarningModalStore.set(null);
  }
</script>

<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-8 min-w-[320px] max-w-[90vw] shadow-lg">
    <h2 class="text-xl font-bold mb-6">비정상적 송금 금액입니다.</h2>
        <div class="mb-4">
          {#if warningMessage}
            <div class="mb-4 text-red-600 font-semibold">
                {warningMessage}
            </div>
          {/if}
        </div>
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="px-4 py-2 rounded border bg-gray-100 hover:bg-gray-200" on:click={handleCheck}>확인</button>
      </div>
  </div>
</div>
