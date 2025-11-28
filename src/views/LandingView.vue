<template>
  <div class="skew-bg d-flex align-center" style="min-height: 100vh;">
    <v-container>
      
      <v-row align="center" justify="center" class="text-center py-10">
        <v-col cols="12" md="10" lg="8">
          
          <v-chip
            color="secondary"
            variant="outlined"
            class="mb-6 font-weight-bold"
            size="small"
            style="border-width: 2px;"
          >
            SKEWPLAY · NO-CODE ML LAB
          </v-chip>

          <h1 class="text-h3 text-md-h2 font-weight-bold mb-6 text-white lh-tight">
            Balance your datasets <br class="d-none d-md-block" />
            <span class="text-secondary">without writing code.</span>
          </h1>

          <p class="text-h6 text-grey-lighten-1 mb-8 font-weight-light mx-auto" style="max-width: 600px;">
            Upload CSVs, analyze imbalance, and mitigation strategies in a guided environment inspired by real-world ML workflows.
          </p>

          <div class="d-flex flex-column flex-sm-row justify-center align-center ga-4 mb-12">
            <v-btn 
              size="x-large" 
              color="primary" 
              to="/register" 
              class="px-8 text-white"
              append-icon="mdi-arrow-right"
              elevation="4"
            >
              Get Started Free
            </v-btn>
            
            <v-btn 
              size="x-large" 
              variant="outlined" 
              color="white" 
              to="/login"
              prepend-icon="mdi-login"
            >
              Login
            </v-btn>
          </div>

        </v-col>
      </v-row>

      <v-row justify="center" class="ga-4">
        
        <v-col cols="12" md="4">
          <v-card class="h-100 pa-6 glass-card text-center" hover>
            <v-avatar color="primary" variant="tonal" size="60" class="mb-4 rounded-xl">
              <v-icon icon="mdi-map-marker-path" size="32" color="white"></v-icon>
            </v-avatar>
            <h3 class="text-h6 font-weight-bold text-white mb-2">Guided Pipelines</h3>
            <p class="text-body-2 text-grey-lighten-1">
              Don't get lost. Follow our structured Upload → Balance → Train → Evaluate journey with built-in safeguards.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="h-100 pa-6 glass-card text-center" hover>
            <v-avatar color="secondary" variant="tonal" size="60" class="mb-4 rounded-xl">
              <v-icon icon="mdi-cloud-sync" size="32" color="secondary"></v-icon>
            </v-avatar>
            <h3 class="text-h6 font-weight-bold text-white mb-2">Real-time Sync</h3>
            <p class="text-body-2 text-grey-lighten-1">
              Your datasets and workflows save automatically to the cloud via Firebase, accessible from any device.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="h-100 pa-6 glass-card text-center" hover>
            <v-avatar color="accent" variant="tonal" size="60" class="mb-4 rounded-xl">
              <v-icon icon="mdi-school-outline" size="32" color="white"></v-icon>
            </v-avatar>
            <h3 class="text-h6 font-weight-bold text-white mb-2">Explainable AI</h3>
            <p class="text-body-2 text-grey-lighten-1">
              Understand the "Why". Get inline explanations, formulas, and book excerpts for every technique you use.
            </p>
          </v-card>
        </v-col>

      </v-row>
    </v-container>
  </div>
</template>

<style scoped>
.lh-tight {
  line-height: 1.2 !important;
}
</style>