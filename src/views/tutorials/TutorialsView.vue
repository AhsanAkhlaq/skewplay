<template>
  <v-container fluid class="pa-0">
    
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="8">
        <h1 class="text-h4 font-weight-bold text-high-emphasis">Tutorials</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Master the Data Balancing techniques with these step-by-step video guides.
        </p>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="store.isLoading">
        <v-col cols="12" sm="6" md="4" xl="3" v-for="n in 3" :key="n">
            <v-skeleton-loader class="rounded-lg border" type="image, article"></v-skeleton-loader>
        </v-col>
    </v-row>

    <!-- Content State -->
    <v-row v-else>
      <v-col 
        v-for="tutorial in store.tutorials" 
        :key="tutorial.id" 
        cols="12" 
        sm="6" 
        md="4"
        xl="3"
      >
        <v-card 
          class="glass-card h-100 d-flex flex-column cursor-pointer hover-card" 
          hover 
          elevation="0"
          border
          @click="openVideo(tutorial.url)"
        >
          <!-- Thumbnail Container with 16:9 Aspect Ratio -->
          <div class="position-relative w-100" style="padding-top: 56.25%;">
            <v-img
              :src="getThumbnail(tutorial.videoId)"
              absolute
              cover
              class="position-absolute top-0 left-0 w-100 h-100 rounded-t-lg"
              :alt="tutorial.title"
            >
              <template v-slot:placeholder>
                <div class="d-flex align-center justify-center fill-height bg-grey-lighten-4">
                  <v-progress-circular indeterminate color="primary"></v-progress-circular>
                </div>
              </template>
              
              <!-- Play Button Overlay -->
              <div class="play-overlay d-flex align-center justify-center">
                 <v-avatar color="rgba(0,0,0,0.6)" size="64">
                    <v-icon icon="mdi-play" size="32" color="white"></v-icon>
                 </v-avatar>
              </div>
            </v-img>
          </div>

          <div class="pa-4 d-flex flex-column flex-grow-1">
            <div class="d-flex align-start justify-space-between mb-2">
               <v-chip size="x-small" color="primary" label class="font-weight-bold">
                  VIDEO
               </v-chip>
               <span class="text-caption text-medium-emphasis">{{ tutorial.duration }}</span>
            </div>

            <h3 class="text-h6 font-weight-bold text-high-emphasis mb-2 line-clamp-2">
              {{ tutorial.title }}
            </h3>
            
            <p class="text-body-2 text-medium-emphasis flex-grow-1 mb-4 line-clamp-3">
              {{ tutorial.description }}
            </p>

            <v-btn 
              variant="tonal" 
              color="primary" 
              block 
              prepend-icon="mdi-youtube"
            >
              Watch Video
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useTutorialsStore } from '../../stores/tutorials';

const store = useTutorialsStore();

const getThumbnail = (videoId: string) => {
  return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
};

const openVideo = (url: string) => {
  window.open(url, '_blank');
};

onMounted(async () => {
  await store.fetchTutorials();
});
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Dark mode glass override */
:global(.v-theme--dark) .glass-card {
  background: rgba(30, 30, 30, 0.7) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.2) !important;
}

.play-overlay {
  background: rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.hover-card:hover .play-overlay {
  opacity: 1;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
