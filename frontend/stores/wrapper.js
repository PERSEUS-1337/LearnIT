import { create } from "zustand";

const useWrapperStore = create((set) => ({
    isLoading: false,
    successMessage: null,
    errorMessage: null,

    setIsLoading: (loading) => set({ isLoading: loading }),

    removeSuccessMessage: () => {
        set({ successMessage: null });
    },

    setSuccessMessage: (message) => {
        set({ successMessage: message });
        setTimeout(() => {
            set({ successMessage: null });
        }, 5000);
    },

    removeErrorMessage: () => {
        set({ errorMessage: null });
    },

    setErrorMessage: (message) => {
        set({ errorMessage: message });
        setTimeout(() => {
            set({ errorMessage: null });
        }, 5000);
    },
}));

export default useWrapperStore;
