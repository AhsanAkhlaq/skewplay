<template>
  <div class="gradient-page">
    <v-container class="py-12" max-width="960">
      <v-card class="pa-10 md-glass text-center" elevation="10">
        <p class="text-uppercase text-medium-emphasis text-caption mb-2">SkewPlay · No-code ML Lab</p>
        <h1 class="text-h3 font-weight-bold mb-4">Balance your datasets without writing code.</h1>
        <p class="text-body-1 text-medium-emphasis mb-6">
          Upload CSVs, analyze imbalance, prototype mitigation strategies, and save workflows — all
          in a guided Vue + Firebase experience inspired by “Machine Learning for Imbalanced Data”.
        </p>
        <div class="d-flex flex-wrap justify-center ga-4 mb-6">
          <v-btn size="large" color="primary" to="/register">
            Get started
          </v-btn>
          <v-btn size="large" variant="tonal" to="/login">
            I already have an account
          </v-btn>
        </div>
        <v-row class="ga-4" align="stretch">
          <v-col cols="12" md="4">
            <v-sheet class="pa-6 rounded-xl" elevation="2">
              <h3 class="text-subtitle-1 font-weight-bold mb-2">Guided pipelines</h3>
              <p class="text-body-2 text-medium-emphasis">
                Follow the Upload → Balance → Train → Evaluate journey with inline tutorials.
              </p>
            </v-sheet>
          </v-col>
          <v-col cols="12" md="4">
            <v-sheet class="pa-6 rounded-xl" elevation="2">
              <h3 class="text-subtitle-1 font-weight-bold mb-2">Realtime storage</h3>
              <p class="text-body-2 text-medium-emphasis">
                Datasets, workflows, and experiments sync live via Firebase Auth, Firestore, and Storage.
              </p>
            </v-sheet>
          </v-col>
          <v-col cols="12" md="4">
            <v-sheet class="pa-6 rounded-xl" elevation="2">
              <h3 class="text-subtitle-1 font-weight-bold mb-2">Explainable insights</h3>
              <p class="text-body-2 text-medium-emphasis">
                Embed excerpts, formulas, and AI recommendations sourced directly from the SRS playbook.
              </p>
            </v-sheet>
          </v-col>
        </v-row>
      </v-card>
    </v-container>
  </div>
</template>
