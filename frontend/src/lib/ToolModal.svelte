<script lang="ts">
  import { ToolModalStore } from './store';

  export let name: string;


  function handleSubmit() {

    $ToolModalStore?.resolver?.(null);
    ToolModalStore.set(null);
  }

  setTimeout(() => {
    handleSubmit()
  }, 3000);
</script>

<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-8 min-w-[320px] max-w-[90vw] shadow-lg">
    <h2 class="text-xl font-bold mb-6">{name}</h2>
   
    <button type="button" class="px-4 py-2 rounded border bg-gray-100 hover:bg-gray-200" on:click={handleSubmit}>취소</button>
    <button type="submit" class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700" on:click={handleSubmit}>확인</button>
    
  </div>
</div>
