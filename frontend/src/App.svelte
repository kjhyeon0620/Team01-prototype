<script>
  import Router from "svelte-spa-router";
  import LLM from "./lib/LLM.svelte";

  const routes = {
    "/": LLM,
  };
</script>

<main>
  <a href="#/">홈</a>
  <Router {routes} />
</main>
