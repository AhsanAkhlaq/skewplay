import { defineStore } from 'pinia';
import { ref } from 'vue';

type SnackbarColor = 'success' | 'error' | 'info' | 'warning';

export const useUiStore = defineStore('ui', () => {
    const snackbar = ref({
        show: false,
        message: '',
        color: 'info' as SnackbarColor,
        timeout: 4000
    });

    const showSnackbar = (message: string, color: SnackbarColor = 'info', timeout = 4000) => {
        snackbar.value = {
            show: true,
            message,
            color,
            timeout
        };
    };

    const showSuccess = (msg: string) => showSnackbar(msg, 'success');
    const showError = (msg: string) => showSnackbar(msg, 'error');
    const showInfo = (msg: string) => showSnackbar(msg, 'info');

    const confirmDialog = ref({
        show: false,
        title: '',
        message: '',
        resolve: null as ((value: boolean) => void) | null,
    });

    const confirm = (title: string, message: string): Promise<boolean> => {
        confirmDialog.value.title = title;
        confirmDialog.value.message = message;
        confirmDialog.value.show = true;

        return new Promise((resolve) => {
            confirmDialog.value.resolve = resolve;
        });
    };

    const resolveConfirm = (result: boolean) => {
        confirmDialog.value.show = false;
        if (confirmDialog.value.resolve) {
            confirmDialog.value.resolve(result);
            confirmDialog.value.resolve = null;
        }
    };

    return {
        snackbar,
        showSnackbar,
        showSuccess,
        showError,
        showInfo,
        confirmDialog,
        confirm,
        resolveConfirm
    };
});
