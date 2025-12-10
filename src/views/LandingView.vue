<template>
  <div class="skew-bg landing-pattern" style="min-height: 100vh;">
    
    <!-- 1. TOP NAVIGATION BAR -->
    <v-app-bar color="transparent" elevation="0" class="px-4 py-2 backdrop-blur" fixed>
       <div class="d-flex align-center cursor-pointer" @click="$router.push('/')">
          <v-avatar color="transparent" size="40" rounded="lg" variant="flat" class="me-3">
              <v-img src="/images/logo.ico" alt="Logo" width="40" height="40"></v-img>
          </v-avatar>
          <div class="font-weight-bold text-h6 text-black" style="font-family: 'Space Grotesk', sans-serif;">
            Skew<span class="text-primary">Play</span>
          </div>
       </div>

       <v-spacer></v-spacer>

       <div class="d-none d-md-flex align-center ga-6 mr-8">
          <a href="#features" class="text-body-2 font-weight-medium text-black text-decoration-none nav-link">Features</a>
          <a href="#how-it-works" class="text-body-2 font-weight-medium text-black text-decoration-none nav-link">How it Works</a>
          <a href="#team" class="text-body-2 font-weight-medium text-black text-decoration-none nav-link">Team</a>
       </div>

       <div class="d-flex align-center ga-3">
          <v-btn variant="text" to="/login" class="font-weight-bold" rounded="lg">Login</v-btn>
          <v-btn color="primary" to="/register" variant="flat" elevation="0" rounded="lg" class="px-6">Get Started</v-btn>
       </div>
    </v-app-bar>

    <!-- 2. HERO SECTION -->
    <v-container class="pt-16 mt-16 pb-16">
      <v-row align="center" justify="center" class="text-center py-12">
        <v-col cols="12" md="10" lg="8">
          <h1 class="text-h3 text-md-h2 font-weight-bold mb-4 text-on-background lh-tight">
            Balance your datasets <br class="d-none d-md-block" />
            <span class="bg-gradient-text">without writing code.</span>
          </h1>

          <p class="text-h6 text-medium-emphasis mb-8 font-weight-light mx-auto" style="line-height: 1.6; max-width: 650px;">
            Stop struggling with skewed data. Upload your CSVs, analyze imbalance s, and apply advanced mitigation strategies in minutes—not hours.
          </p>

          <div class="d-flex flex-column flex-sm-row justify-center align-center ga-4 mb-12">
            <v-btn 
              size="x-large" 
              color="primary" 
              to="/register" 
              class="px-8 text-on-primary"
              append-icon="mdi-arrow-right"
              elevation="4"
              rounded="xl"
            >
              Start for Free
            </v-btn>
            
            <v-btn 
              size="x-large" 
              variant="outlined" 
              color="on-background" 
              href="#how-it-works"
              prepend-icon="mdi-play-circle-outline"
              rounded="xl"
            >
              See How It Works
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- 3. FEATURES SECTION -->
    <div id="features" class="py-16 bg-white-50">
      <v-container>
        <div class="text-center mb-16">
          <h2 class="text-h4 font-weight-bold mb-4">Everything you need to build better models</h2>
          <p class="text-body-1 text-medium-emphasis">Professional-grade tools wrapped in a beautiful, intuitive interface.</p>
        </div>

        <v-row justify="center" class="ga-4">
          <v-col cols="12" md="4">
            <v-card class="h-100 pa-8 glass-card text-center" hover>
              <div class="mb-6 d-inline-flex pa-4 rounded-xl bg-primary-lighten-5">
                 <v-icon icon="mdi-scale-balance" size="40" color="primary"></v-icon>
              </div>
              <h3 class="text-h6 font-weight-bold text-on-surface mb-3">Auto-Balancing</h3>
              <p class="text-body-2 text-medium-emphasis lh-relaxed">
                Detect class imbalance instantly. Apply SMOTE, ADASYN, or Random Undersampling with a single click and visualize the shift.
              </p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="h-100 pa-8 glass-card text-center" hover>
               <div class="mb-6 d-inline-flex pa-4 rounded-xl bg-secondary-lighten-5">
                 <v-icon icon="mdi-state-machine" size="40" color="secondary"></v-icon>
              </div>
              <h3 class="text-h6 font-weight-bold text-on-surface mb-3">Visual Pipelines</h3>
              <p class="text-body-2 text-medium-emphasis lh-relaxed">
                Design preprocessing and training workflows visually. Drag, drop, and connect steps without writing a single line of Python.
              </p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="h-100 pa-8 glass-card text-center" hover>
               <div class="mb-6 d-inline-flex pa-4 rounded-xl bg-accent-lighten-5">
                 <v-icon icon="mdi-cloud-sync" size="40" color="accent"></v-icon>
              </div>
              <h3 class="text-h6 font-weight-bold text-on-surface mb-3">Cloud Persistence</h3>
              <p class="text-body-2 text-medium-emphasis lh-relaxed">
                Your datasets and models are safe in the cloud. Access your experiments from any device, anywhere, anytime.
              </p>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- 4. HOW IT WORKS -->
    <div id="how-it-works" class="py-16">
       <v-container>
          <v-row align="center">
             <v-col cols="12" md="6">
                <v-chip color="primary" label class="mb-4 font-weight-bold">WORKFLOW</v-chip>
                <h2 class="text-h3 font-weight-bold mb-6">From CSV to Model <br> in 4 Simple Steps</h2>
                
                <v-list lines="three" bg-color="transparent">
                   <v-list-item class="px-0 mb-4">
                      <template v-slot:prepend>
                         <v-avatar color="primary" size="48" class="font-weight-bold text-h6">1</v-avatar>
                      </template>
                      <v-list-item-title class="font-weight-bold text-h6 mb-1">Upload & Analyze</v-list-item-title>
                      <v-list-item-subtitle class="text-body-1">Upload your dataset. We automatically profile it to detect class imbalance, missing values, and data types.</v-list-item-subtitle>
                   </v-list-item>

                   <v-list-item class="px-0 mb-4">
                      <template v-slot:prepend>
                         <v-avatar color="primary" size="48" class="font-weight-bold text-h6">2</v-avatar>
                      </template>
                      <v-list-item-title class="font-weight-bold text-h6 mb-1">Preprocess & Clean</v-list-item-title>
                      <v-list-item-subtitle class="text-body-1">Clean data using our visual pipeline. Handle missing values and normalize features effortlessly.</v-list-item-subtitle>
                   </v-list-item>

                   <v-list-item class="px-0 mb-4">
                      <template v-slot:prepend>
                         <v-avatar color="primary" size="48" class="font-weight-bold text-h6">3</v-avatar>
                      </template>
                      <v-list-item-title class="font-weight-bold text-h6 mb-1">Balance by Applying Techniques</v-list-item-title>
                      <v-list-item-subtitle class="text-body-1">Apply advanced re-sampling techniques like SMOTE, ADASYN, or Random Undersampling to fix skewness.</v-list-item-subtitle>
                   </v-list-item>

                    <v-list-item class="px-0 mb-4">
                      <template v-slot:prepend>
                         <v-avatar color="primary" size="48" class="font-weight-bold text-h6">4</v-avatar>
                      </template>
                      <v-list-item-title class="font-weight-bold text-h6 mb-1">Train & Evaluate</v-list-item-title>
                      <v-list-item-subtitle class="text-body-1">Select classifiers (Random Forest, XGBoost) and train them instantly. Compare performance metrics like F1-Score.</v-list-item-subtitle>
                   </v-list-item>
                </v-list>
             </v-col>
             <v-col cols="12" md="6">
                <!-- Visual Representation of the Pipeline -->
                <v-card class="rounded-xl elevation-5 border bg-surface overflow-hidden">
                   <div class="pa-4 border-b d-flex align-center bg-grey-lighten-5">
                      <div class="d-flex ga-2">
                         <div class="rounded-circle bg-error" style="width: 10px; height: 10px;"></div>
                         <div class="rounded-circle bg-warning" style="width: 10px; height: 10px;"></div>
                         <div class="rounded-circle bg-success" style="width: 10px; height: 10px;"></div>
                      </div>
                      <div class="mx-auto text-caption font-weight-bold text-medium-emphasis">SkewPlay Pipeline</div>
                   </div>
                   <div class="pa-8 d-flex flex-column align-center justify-center bg-white" style="min-height: 400px;">
                      <!-- Abstract Nodes -->
                      <div class="d-flex align-center mb-4">
                          <v-card class="pa-4 rounded-lg border text-center" width="120">
                             <v-icon icon="mdi-file-delimited" color="primary" class="mb-2"></v-icon>
                             <div class="text-caption font-weight-bold">Dataset</div>
                          </v-card>
                      </div>
                      <v-icon icon="mdi-arrow-down" color="grey-lighten-2" class="mb-4"></v-icon>
                      <div class="d-flex align-center gap-4 mb-4">
                          <v-card class="pa-4 rounded-lg border text-center" width="120">
                             <v-icon icon="mdi-wrench" color="secondary" class="mb-2"></v-icon>
                             <div class="text-caption font-weight-bold">Clean</div>
                          </v-card>
                          <div class="mx-2 text-grey-lighten-2">+</div>
                          <v-card class="pa-4 rounded-lg border text-center" width="120" color="primary" variant="flat">
                             <v-icon icon="mdi-scale-balance" color="white" class="mb-2"></v-icon>
                             <div class="text-caption font-weight-bold">Balance</div>
                          </v-card>
                      </div>
                      <v-icon icon="mdi-arrow-down" color="grey-lighten-2" class="mb-4"></v-icon>
                      <div class="d-flex align-center mb-4">
                          <v-card class="pa-4 rounded-lg border text-center" width="120">
                             <v-icon icon="mdi-brain" color="accent" class="mb-2"></v-icon>
                             <div class="text-caption font-weight-bold">Train</div>
                          </v-card>
                      </div>
                   </div>
                </v-card>
             </v-col>
          </v-row>
       </v-container>
    </div>

    <!-- 5. TEAM SECTION -->
    <div id="team" class="py-16 bg-grey-lighten-4">
       <v-container>
          <div class="text-center mb-12">
             <h2 class="text-h4 font-weight-bold mb-2">Meet the Team</h2>
             <p class="text-medium-emphasis">The minds behind SkewPlay.</p>
          </div>

          <v-row justify="center">
             <v-col cols="12" sm="6" md="4">
                <v-card class="text-center pa-6 rounded-xl border-none elevation-2" flat>
                   <v-avatar size="120" class="mb-4 elevation-3">
                      <v-img src="/images/ahsan.png" alt="Ahsan"></v-img>
                   </v-avatar>
                   <h3 class="text-h6 font-weight-bold">Ahsan Akhlaq</h3>
                   <div class="text-body-2 text-primary font-weight-bold mb-4">Lead Developer & ML Engineer</div>
                   
                   <p class="text-caption text-medium-emphasis mb-4">
                      Passionate about democratizing machine learning and solving the class imbalance problem for everyone.
                   </p>

                   <div class="d-flex justify-center ga-2">
                      <v-btn icon="mdi-github" variant="text" size="small" color="grey-darken-1"></v-btn>
                      <v-btn icon="mdi-linkedin" variant="text" size="small" color="blue-darken-2"></v-btn>
                      <v-btn icon="mdi-email" variant="text" size="small" color="grey-darken-1"></v-btn>
                   </div>
                </v-card>
             </v-col>

             <v-col cols="12" sm="6" md="4">
                <v-card class="text-center pa-6 rounded-xl border-none elevation-2" flat>
                   <v-avatar size="120" class="mb-4 elevation-3">
                      <v-img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Abdul&top[]=shortHair,shortHairDreads01,shortHairDreads02,shortHairFrizzle,shortHairShaggyMullet,shortHairShortCurly,shortHairShortFlat,shortHairShortRound,shortHairShortWaved,shortHairSides,shortHairTheCaesar,shortHairTheCaesarSidePart" alt="Abdul"></v-img>
                   </v-avatar>
                   <h3 class="text-h6 font-weight-bold">Abdul Qudoos</h3>
                   <div class="text-body-2 text-primary font-weight-bold mb-4">Full Stack Developer</div>
                   
                   <p class="text-caption text-medium-emphasis mb-4">
                      Expert in building scalable web architectures and intuitive user interfaces that drive engagement.
                   </p>

                   <div class="d-flex justify-center ga-2">
                      <v-btn icon="mdi-github" variant="text" size="small" color="grey-darken-1"></v-btn>
                      <v-btn icon="mdi-linkedin" variant="text" size="small" color="blue-darken-2"></v-btn>
                      <v-btn icon="mdi-email" variant="text" size="small" color="grey-darken-1"></v-btn>
                   </div>
                </v-card>
             </v-col>

             <v-col cols="12" sm="6" md="4">
                <v-card class="text-center pa-6 rounded-xl border-none elevation-2" flat>
                   <v-avatar size="120" class="mb-4 elevation-3">
                      <v-img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Noor&top[]=shortHair,shortHairDreads01,shortHairDreads02,shortHairFrizzle,shortHairShaggyMullet,shortHairShortCurly,shortHairShortFlat,shortHairShortRound,shortHairShortWaved,shortHairSides,shortHairTheCaesar,shortHairTheCaesarSidePart" alt="Noor"></v-img>
                   </v-avatar>
                   <h3 class="text-h6 font-weight-bold">Noor-ul-Ghani</h3>
                   <div class="text-body-2 text-primary font-weight-bold mb-4">Backend Specialist</div>
                   
                   <p class="text-caption text-medium-emphasis mb-4">
                      Focused on optimizing data pipelines and ensuring secure, efficient cloud infrastructure.
                   </p>

                   <div class="d-flex justify-center ga-2">
                      <v-btn icon="mdi-github" variant="text" size="small" color="grey-darken-1"></v-btn>
                      <v-btn icon="mdi-linkedin" variant="text" size="small" color="blue-darken-2"></v-btn>
                      <v-btn icon="mdi-email" variant="text" size="small" color="grey-darken-1"></v-btn>
                   </div>
                </v-card>
             </v-col>
          </v-row>
       </v-container>
    </div>

    <!-- 6. FOOTER -->
    <v-footer class="bg-black text-white py-12">
       <v-container>
          <v-row>
             <v-col cols="12" md="4">
                <div class="font-weight-bold text-h5 mb-4 font-display">SkewPlay</div>
                <p class="text-grey-lighten-1 text-body-2 mb-4" style="max-width: 300px;">
                   The all-in-one platform for handling imbalanced datasets. Build robust models with confidence.
                </p>
                <div class="text-caption text-grey-darken-1">
                   © 2025 SkewPlay. All rights reserved.
                </div>
             </v-col>
             <v-col cols="6" md="2">
                <div class="font-weight-bold text-body-1 mb-4">Product</div>
                <div class="d-flex flex-column ga-2 text-caption text-grey-lighten-1">
                   <a href="#" class="text-white text-decoration-none">Features</a>
                   <a href="#" class="text-white text-decoration-none">Pricing</a>
                   <a href="#" class="text-white text-decoration-none">Docs</a>
                </div>
             </v-col>
             <v-col cols="6" md="2">
                <div class="font-weight-bold text-body-1 mb-4">Company</div>
                <div class="d-flex flex-column ga-2 text-caption text-grey-lighten-1">
                   <a href="#" class="text-white text-decoration-none">About</a>
                   <a href="#" class="text-white text-decoration-none">Team</a>
                   <a href="#" class="text-white text-decoration-none">Careers</a>
                </div>
             </v-col>
             <v-col cols="12" md="4">
                <div class="font-weight-bold text-body-1 mb-4">Stay Updated</div>
                <v-text-field
                   label="Enter your email"
                   variant="outlined"
                   bg-color="grey-darken-3"
                   color="white"
                   density="compact"
                   hide-details
                   append-inner-icon="mdi-send"
                ></v-text-field>
             </v-col>
          </v-row>
       </v-container>
    </v-footer>

  </div>
</template>

<script setup lang="ts">
// No script logic needed for static landing page
</script>

<style scoped>
.lh-tight {
  line-height: 1.1 !important;
}
.lh-relaxed {
   line-height: 1.6 !important;
}
.backdrop-blur {
   backdrop-filter: blur(12px);
   background: rgba(255, 255, 255, 0.8) !important;
   border-bottom: 1px solid rgba(0,0,0,0.05);
}

.nav-link {
   position: relative;
   transition: color 0.2s;
}
.nav-link:hover {
   color: rgb(var(--v-theme-primary)) !important;
}

/* Gradient Text for Hero */
.bg-gradient-text {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-accent)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Subtle Background Pattern */
.landing-pattern {
  position: relative;
}

.landing-pattern::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Modern Dot Pattern */
  background-image: radial-gradient(rgba(var(--v-theme-on-surface), 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}
</style>