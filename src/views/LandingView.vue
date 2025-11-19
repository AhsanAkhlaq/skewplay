<template>
  <main class="landing">
    <div class="hero surface">
      <p class="eyebrow">SkewPlay · No-code ML Lab</p>
      <h1>Balance your datasets without writing code.</h1>
      <p class="subtitle">
        Upload CSVs, analyze imbalance, prototype mitigation strategies, and
        save workflows — all inside a guided Vue + Firebase experience.
      </p>
      <div class="actions">
        <RouterLink to="/register" class="btn btn-primary">Get Started</RouterLink>
        <RouterLink to="/login" class="btn btn-ghost">I already have an account</RouterLink>
      </div>
    </div>

    <section class="feature-grid">
      <article class="surface">
        <h3>Guided pipelines</h3>
        <p>Follow the Upload → Balance → Train → Evaluate journey with tooltips and inline tutorials.</p>
      </article>
      <article class="surface">
        <h3>Realtime storage</h3>
        <p>Datasets, workflows, and experiments sync live via Firebase Firestore and Storage.</p>
      </article>
      <article class="surface">
        <h3>Explainable insights</h3>
        <p>Embed excerpts, formulas, and AI recommendations sourced from the SRS playbook.</p>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.landing {
  max-width: 960px;
  margin: 0 auto;
  padding: 3rem 1.25rem 4rem;
  color: #f1f5f9;
}

.hero {
  text-align: center;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-size: 0.8rem;
  color: #a3bffa;
}

h1 {
  font-size: clamp(2.5rem, 5vw, 3.3rem);
  margin: 0.75rem 0;
}

.subtitle {
  max-width: 640px;
  margin: 0 auto 1.5rem;
  color: #cbd5f5;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.feature-grid {
  margin-top: 2.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}
</style>

