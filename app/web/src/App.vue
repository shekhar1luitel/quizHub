<template>
  <main class="app-shell">
    <header class="hero">
      <p class="eyebrow">QuizHub insight</p>
      <h1>Your learning launchpad</h1>
      <p>
        Explore categories curated by QuizHub, keep an eye on trending quizzes, and jump back
        into practice whenever you're ready.
      </p>
    </header>
    <section class="content">
      <PublicHome />
    </section>
  </main>
</template>

<script setup lang="ts">
import PublicHome from './components/PublicHome.vue'
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2.5rem clamp(1rem, 4vw, 3.5rem);
}

.hero {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  border-radius: 1.5rem;
  padding: clamp(1.5rem, 3vw, 2.5rem);
  box-shadow: 0 18px 45px -20px rgba(37, 99, 235, 0.6);
  display: grid;
  gap: 0.75rem;
}

.hero .eyebrow {
  margin: 0;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.85;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 3.5vw, 2.75rem);
  font-weight: 700;
}

.hero p {
  margin: 0;
  font-size: clamp(1rem, 2vw, 1.2rem);
  max-width: 48rem;
  color: rgba(255, 255, 255, 0.92);
}

.content {
  flex: 1;
}

@media (max-width: 720px) {
  .app-shell {
    padding: 1.5rem;
  }

  .hero {
    border-radius: 1.25rem;
  }
}
</style>
