"use client";

import useWrapperStore from "@/stores/wrapper";

export default function Wrapper({ children }) {
    const {
        isLoading,
        successMessage,
        errorMessage,
        removeErrorMessage,
        removeSuccessMessage,
    } = useWrapperStore((state) => ({
        isLoading: state.isLoading,
        successMessage: state.successMessage,
        errorMessage: state.errorMessage,
        removeSuccessMessage: state.removeSuccessMessage,
        removeErrorMessage: state.removeErrorMessage,
    }));

    return (
        <div>
            {isLoading ? (
                <main className="w-screen h-screen flex items-center justify-center fixed z-50 bg-base-100">
                    <span className="loading loading-infinity loading-lg text-primary"></span>
                </main>
            ) : undefined}

            {successMessage ? (
                <div
                    role="alert"
                    className="alert alert-success fixed left-5 bottom-32 max-w-xs md:max-w-sm lg:max-w-lg p-2 md:p-4 flex justify-between"
                >
                    <div className="flex items-center gap-2">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-6 w-6 shrink-0 stroke-current"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                    </div>

                    <span>{successMessage}</span>
                    <div className="flex items-center justify-center">
                        <button
                            className="btn btn-sm btn-circle btn-ghost"
                            onClick={removeSuccessMessage}
                        >
                            x
                        </button>
                    </div>
                </div>
            ) : undefined}
            {errorMessage ? (
                <div
                    role="alert"
                    className="alert alert-error fixed left-5 bottom-32 max-w-xs md:max-w-sm p-2 md:p-4 flex justify-between"
                >
                    <div className="flex items-center gap-2">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-6 w-6 shrink-0 stroke-current"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <span>{errorMessage}</span>
                    </div>

                    <div className="flex items-center justify-center">
                        <button
                            className="btn btn-sm btn-circle btn-error"
                            onClick={removeErrorMessage}
                        >
                            x
                        </button>
                    </div>
                </div>
            ) : undefined}
            {children}
        </div>
    );
}
