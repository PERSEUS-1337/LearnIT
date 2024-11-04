import { create } from "zustand";
import { persist } from "zustand/middleware";

const useUserStore = create(
    persist(
        (set) => ({
            bearerToken: null,
            setBearerToken: (token) => set({ bearerToken: token }),
            removeBearerToken: () => set({ bearerToken: null }),
        }),
        {
            name: "user-storage", // unique name for the storage (must be unique within your application)
        }
    )
);

export default useUserStore;
