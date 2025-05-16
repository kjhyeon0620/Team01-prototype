<script>
  import Router from "svelte-spa-router";
  import LLM from "./lib/LLM.svelte";
  import VoiceReference from "./lib/VoiceReference.svelte";

  const routes = {
    "/": LLM,
    "/voice_reference": VoiceReference
  };
</script>

<main>
  <div class="flex flex-row w-screen h-screen justify-center items-center">
    <div class="flex-1 flex justify-center items-center flex-col">
      <a href="#/">홈</a>
      <a href="#/voice_reference">voice_reference</a>
    </div>
    <div class="h-11/12 flex flex-col max-w-md mx-auto flex-auto justify-center items-center">
      <Router {routes} />
    </div>
    <div class="flex-1 flex justify-center items-center">
      pintech-team01
    </div>
  </div>
</main>