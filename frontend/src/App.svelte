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
  <a href="#/">홈</a>
  <a href="#/voice_reference">voice_reference</a>
  <Router {routes} />
</main>
