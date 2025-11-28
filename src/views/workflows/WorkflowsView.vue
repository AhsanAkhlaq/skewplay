<template>
  <v-container fluid class="pa-0">
    <v-row class="align-center mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-white">Workflows</h1>
        <p class="text-subtitle-1 text-medium-emphasis">Manage your experiments and pipelines.</p>
      </v-col>
      <v-col class="text-right">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">
          New Workflow
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-for="wf in workflowsStore.workflows" :key="wf.id" cols="12" md="4">
        <v-card class="glass-card" hover>
          <v-card-title class="text-h6 font-weight-bold">{{ wf.name }}</v-card-title>
          <v-card-subtitle class="mb-2">
             Status: {{ wf.status }}
          </v-card-subtitle>
          
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
               <span class="text-caption text-grey">Created: {{ new Date(wf.createdAt?.seconds * 1000).toLocaleDateString() }}</span>
               <v-chip size="small" :color="wf.status === 'Completed' ? 'success' : 'warning'">
                  {{ wf.status }}
               </v-chip>
            </div>
          </v-card-text>

          <v-divider></v-divider>
          
          <v-card-actions>
             <v-spacer></v-spacer>
             <v-btn 
                color="error" 
                variant="text" 
                size="small" 
                @click="handleDelete(wf.id)"
            >
                Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="500">
      <v-card class="pa-4 rounded-lg">
        <v-card-title>Create New Workflow</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newWorkflowName"
            label="Workflow Name"
            variant="outlined"
            autofocus
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createWorkflow" :disabled="!newWorkflowName">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useWorkflowsStore } from '../../stores/workflows';

const workflowsStore = useWorkflowsStore();
const dialog = ref(false);
const newWorkflowName = ref('');

const createWorkflow = async () => {
  if (!newWorkflowName.value) return;
  try {
    await workflowsStore.createWorkflow(newWorkflowName.value);
    dialog.value = false;
    newWorkflowName.value = '';
  } catch (e) {
    // Error handled by store
  }
};

// FIX: Added null check for ID
const handleDelete = async (id: string | undefined) => {
  if (id && confirm('Delete this workflow?')) {
    await workflowsStore.deleteWorkflow(id);
  }
};

onMounted(() => {
  workflowsStore.fetchWorkflows();
});
</script>