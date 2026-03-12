<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold mb-1">Admin Portal</h1>
            <p class="text-subtitle-1 text-medium-emphasis">System overview and user management</p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            :loading="isLoading"
            @click="fetchStats"
          >
            Refresh Stats
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Stat Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 rounded-lg" elevation="2">
          <div class="d-flex align-center mb-2">
            <v-avatar color="blue-lighten-4" class="me-3">
              <v-icon icon="mdi-account-group" color="blue"></v-icon>
            </v-avatar>
            <span class="text-overline">Total Users</span>
          </div>
          <h2 class="text-h4 font-weight-bold">{{ stats.totalUsers || 0 }}</h2>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 rounded-lg" elevation="2">
          <div class="d-flex align-center mb-2">
            <v-avatar color="green-lighten-4" class="me-3">
              <v-icon icon="mdi-currency-usd" color="green"></v-icon>
            </v-avatar>
            <span class="text-overline">Total Revenue</span>
          </div>
          <h2 class="text-h4 font-weight-bold">${{ (stats.totalRevenue / 100).toFixed(2) }}</h2>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 rounded-lg" elevation="2">
          <div class="d-flex align-center mb-2">
            <v-avatar color="purple-lighten-4" class="me-3">
              <v-icon icon="mdi-flask-outline" color="purple"></v-icon>
            </v-avatar>
            <span class="text-overline">Experiments Run</span>
          </div>
          <h2 class="text-h4 font-weight-bold">{{ stats.totalExperiments || 0 }}</h2>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 rounded-lg" elevation="2">
          <div class="d-flex align-center mb-2">
            <v-avatar color="orange-lighten-4" class="me-3">
              <v-icon icon="mdi-database-outline" color="orange"></v-icon>
            </v-avatar>
            <span class="text-overline">Storage Used</span>
          </div>
          <h2 class="text-h4 font-weight-bold">{{ formatBytes(stats.totalStorageBytes || 0) }}</h2>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-row>
      <v-col cols="12">
        <v-tabs v-model="activeTab" color="primary" class="mb-4">
          <v-tab value="users">
            <v-icon start icon="mdi-account-group"></v-icon>
            Users
          </v-tab>
          <v-tab value="admins">
            <v-icon start icon="mdi-shield-account"></v-icon>
            Admins
          </v-tab>
          <v-tab value="payments">
            <v-icon start icon="mdi-credit-card-outline"></v-icon>
            Payments
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- User Window -->
          <v-window-item value="users">
            <v-card class="rounded-lg" elevation="2">
              <v-card-title class="d-flex align-center pa-4">
                <v-icon icon="mdi-account-settings" class="me-2"></v-icon>
                User List
                <v-spacer></v-spacer>
                <v-text-field
                  v-model="userSearch"
                  prepend-inner-icon="mdi-magnify"
                  label="Search Users"
                  single-line
                  hide-details
                  density="compact"
                  variant="outlined"
                  style="max-width: 300px"
                ></v-text-field>
              </v-card-title>

              <v-data-table
                :headers="userHeaders"
                :items="regularUsers"
                :search="userSearch"
                :loading="isLoading"
                class="elevation-0 border"
                density="comfortable"
              >
                <template v-slot:item.tier="{ item }">
                  <v-chip
                    :color="item.tier === 'Advanced' ? 'primary' : 'grey'"
                    size="small"
                    label
                  >
                    {{ item.tier }}
                  </v-chip>
                </template>
                <template v-slot:item.createdAt="{ value }">
                  {{ formatDate(value) }}
                </template>
                <template v-slot:item.storageBytes="{ item }">
                  {{ formatBytes(item.storageBytes) }}
                </template>
                <template v-slot:item.role="{ item }">
                  <v-chip
                    :color="item.role === 'admin' ? 'error' : 'info'"
                    size="small"
                    variant="outlined"
                  >
                    {{ item.role }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- Admins Window -->
          <v-window-item value="admins">
            <v-card class="rounded-lg" elevation="2">
              <v-card-title class="d-flex align-center pa-4">
                <v-icon icon="mdi-shield-account" class="me-2 text-error"></v-icon>
                Admin Roster
                <v-spacer></v-spacer>
                <v-text-field
                  v-model="userSearch"
                  prepend-inner-icon="mdi-magnify"
                  label="Search Admins"
                  single-line
                  hide-details
                  density="compact"
                  variant="outlined"
                  style="max-width: 300px"
                ></v-text-field>
              </v-card-title>

              <v-data-table
                :headers="adminHeaders"
                :items="adminUsers"
                :search="userSearch"
                :loading="isLoading"
                class="elevation-0 border"
                density="comfortable"
              >
                <template v-slot:item.createdAt="{ value }">
                  {{ formatDate(value) }}
                </template>
                <template v-slot:item.role="{ item }">
                  <v-chip
                    color="error"
                    size="small"
                    variant="flat"
                  >
                    {{ item.role }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- Payment Window -->
          <v-window-item value="payments">
            <v-card class="rounded-lg" elevation="2">
              <v-card-title class="d-flex align-center pa-4">
                <v-icon icon="mdi-cash-multiple" class="me-2"></v-icon>
                Recent Transactions
                <v-spacer></v-spacer>
                <v-text-field
                  v-model="paymentSearch"
                  prepend-inner-icon="mdi-magnify"
                  label="Search Payments"
                  single-line
                  hide-details
                  density="compact"
                  variant="outlined"
                  style="max-width: 300px"
                ></v-text-field>
              </v-card-title>

              <v-data-table
                :headers="paymentHeaders"
                :items="payments"
                :search="paymentSearch"
                :loading="isLoading"
                class="elevation-0 border"
                density="comfortable"
              >
                <template v-slot:item.amount="{ value }">
                  <span class="font-weight-bold text-success font-mono">
                    ${{ (value / 100).toFixed(2) }}
                  </span>
                </template>
                <template v-slot:item.date="{ value }">
                  {{ formatDate(value) }}
                </template>
                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="item.status === 'succeeded' ? 'success' : 'warning'"
                    size="x-small"
                    class="text-uppercase"
                  >
                    {{ item.status }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { apiClient } from '../../services/api';

interface Stats {
  totalUsers: number;
  totalRevenue: number;
  totalExperiments: number;
  totalStorageBytes: number;
}

const stats = ref<Stats>({
  totalUsers: 0,
  totalRevenue: 0,
  totalExperiments: 0,
  totalStorageBytes: 0,
});

const users = ref<any[]>([]);
const payments = ref<any[]>([]);

const regularUsers = computed(() => users.value.filter(u => u.role !== 'admin'));
const adminUsers = computed(() => users.value.filter(u => u.role === 'admin'));

const isLoading = ref(false);
const activeTab = ref('users');
const userSearch = ref('');
const paymentSearch = ref('');
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');

// Use explicit literal types for alignment to satisfy Vuetify 3 TypeScript
const userHeaders = [
  { title: 'Name', key: 'displayName', align: 'start' as const },
  { title: 'Email', key: 'email', align: 'start' as const },
  { title: 'Joined', key: 'createdAt', align: 'center' as const },
  { title: 'Tier', key: 'tier', align: 'center' as const },
  { title: 'Role', key: 'role', align: 'center' as const },
  { title: 'Experiments', key: 'experiments', align: 'end' as const },
  { title: 'Storage', key: 'storageBytes', align: 'end' as const },
];

const adminHeaders = [
  { title: 'Name', key: 'displayName', align: 'start' as const },
  { title: 'Email', key: 'email', align: 'start' as const },
  { title: 'Role Assigned On', key: 'createdAt', align: 'center' as const },
  { title: 'Role', key: 'role', align: 'center' as const },
];

const paymentHeaders = [
  { title: 'User', key: 'userName', align: 'start' as const },
  { title: 'Email', key: 'userEmail', align: 'start' as const },
  { title: 'Amount', key: 'amount', align: 'end' as const },
  { title: 'Date', key: 'date', align: 'center' as const },
  { title: 'Status', key: 'status', align: 'center' as const },
];

const fetchStats = async () => {
  isLoading.value = true;
  try {
    const [statsRes, usersRes, paymentsRes] = await Promise.all([
      apiClient.get('/admin/stats'),
      apiClient.get('/admin/users'),
      apiClient.get('/admin/payments'),
    ]);
    stats.value = statsRes.data;
    users.value = usersRes.data;
    payments.value = paymentsRes.data;
  } catch (error) {
    console.error('Error fetching admin data:', error);
    snackbarText.value = 'Failed to load admin data. Ensure backend is running and Firebase Admin is configured.';
    snackbarColor.value = 'error';
    snackbar.value = true;
  } finally {
    isLoading.value = false;
  }
};

const formatDate = (val: any) => {
  if (!val) return 'N/A';
  
  try {
    // Handle Firestore Timestamp (if coming directly from SDK)
    if (typeof val === 'object' && val.seconds) {
      return new Date(val.seconds * 1000).toLocaleDateString();
    }
    // Handle ISO string or Date object
    const date = new Date(val);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleDateString();
  } catch (e) {
    return 'N/A';
  }
};

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  if (i < 0) return '0 B';
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

onMounted(fetchStats);
</script>

<style scoped>
.v-card-title {
  font-weight: bold;
}
</style>
