"use client";

import { useState } from "react";
import { submitForm } from "./actions";
import useWrapperStore from "@/stores/wrapper";

export default function Page(props) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const setErrorMessage = useWrapperStore((state) => state.setErrorMessage);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!username) {
            setErrorMessage("Email is required.");
            return;
        }
        if (!password) {
            setErrorMessage("Password is required.");
            return;
        }
        try {
            const message = await submitForm(username, password);

            if (!message) return;

            if (message.error) {
                throw new Error(message.error);
            }
        } catch (err) {
            setErrorMessage(err.message);
        }
    };

    return (
        <main>
            <section className="container mx-auto px-5 py-5 md:px-10 md:py-10 h-screen">
                <div className="flex flex-col items-center h-full justify-center">
                    <div className="card bg-neutral text-neutral-content w-96">
                        <form className="card-body" onSubmit={handleSubmit}>
                            <h2 className="card-title">LearnIt AI</h2>
                            <p className="text-sm">
                                Kindly login with your account to continue.
                            </p>
                            <div className="mt-2 flex flex-col gap-2">
                                <label className="input input-bordered flex items-center gap-2">
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 16 16"
                                        fill="currentColor"
                                        className="h-4 w-4 opacity-70"
                                    >
                                        <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM12.735 14c.618 0 1.093-.561.872-1.139a6.002 6.002 0 0 0-11.215 0c-.22.578.254 1.139.872 1.139h9.47Z" />
                                    </svg>
                                    <input
                                        type="text"
                                        className="grow"
                                        placeholder="Username"
                                        value={username}
                                        onChange={(e) =>
                                            setUsername(e.target.value)
                                        }
                                        required
                                    />
                                </label>
                                <label className="input input-bordered flex items-center gap-2">
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 16 16"
                                        fill="currentColor"
                                        className="h-4 w-4 opacity-70"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M14 6a4 4 0 0 1-4.899 3.899l-1.955 1.955a.5.5 0 0 1-.353.146H5v1.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-2.293a.5.5 0 0 1 .146-.353l3.955-3.955A4 4 0 1 1 14 6Zm-4-2a.75.75 0 0 0 0 1.5.5.5 0 0 1 .5.5.75.75 0 0 0 1.5 0 2 2 0 0 0-2-2Z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                    <input
                                        type="password"
                                        className="grow"
                                        required
                                        value={password}
                                        onChange={(e) =>
                                            setPassword(e.target.value)
                                        }
                                        placeholder="Password"
                                    />
                                </label>
                            </div>
                            <div className="card-actions justify-end mt-2">
                                <button className="btn btn-primary w-full">
                                    Login
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </section>
        </main>
    );
}
