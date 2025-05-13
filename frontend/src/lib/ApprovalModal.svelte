<script lang="ts">
  import { ApprovalModalStore } from './store';
  import { onMount } from 'svelte';

  export let name: string;
  export let parameters: { [key: string]: any };

  let localData: { [key: string]: any } = {};

  onMount(() => {
    localData = { ...parameters };
  });

  function handleSubmit() {

    // 원본 data의 타입에 맞게 변환
    const result: { [key: string]: any } = {};
    for (const key in localData) {
      const original = parameters[key];
      const value = localData[key];
      switch (typeof original) {
        case 'number':
          result[key] = Number(value);
          break;
        case 'boolean':
          result[key] = !!value;
          break;
        default:
          result[key] = value;
      }
    }
    $ApprovalModalStore?.resolver?.(result);
    ApprovalModalStore.set(null);
  }

  function handleCancel() {
    $ApprovalModalStore?.resolver?.(null);
    ApprovalModalStore.set(null);
  }
</script>

<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-8 min-w-[320px] max-w-[90vw] shadow-lg">
    <h2 class="text-xl font-bold mb-6">{name}</h2>
    <form on:submit|preventDefault={handleSubmit}>
      {#each Object.entries(localData) as [key, value]}
        <div class="mb-4">
          <span class="block mb-2 font-medium">{key}</span>
          {#if typeof parameters[key] === 'boolean'}
            <input
              type="checkbox"
              class="h-5 w-5"
              bind:checked={localData[key]}
            />
          {:else if typeof parameters[key] === 'number'}
            <input
              type="number"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
              bind:value={localData[key]}
            />
          {:else}
            <input
              type="text"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
              bind:value={localData[key]}
            />
          {/if}
        </div>
      {/each}
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="px-4 py-2 rounded border bg-gray-100 hover:bg-gray-200" on:click={handleCancel}>취소</button>
        <button type="submit" class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">확인</button>
      </div>
    </form>
  </div>
</div>
