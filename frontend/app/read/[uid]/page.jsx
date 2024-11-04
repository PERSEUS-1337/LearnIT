"use client";

import { useRouter, useParams } from "next/navigation";
import { FaCaretLeft, FaRocketchat } from "react-icons/fa";

import useSWR from "swr";

const fetcher = async (url) => {
    const res = await fetch(url);

    // If the status code is not in the range 200-299,
    // we still try to parse and throw it.
    if (res.status >= 400) {
        const error = new Error("An error occurred while fetching the data.");
        // Attach extra info to the error object.
        error.info = await res.json();
        error.status = res.status;
        throw error;
    }

    return res.json();
};

export default function Page() {
    const router = useRouter();
    const params = useParams();
    const { data, error, isLoading } = useSWR(
        `/api/read?filename=${params.uid}`,
        fetcher
    );

    if (error)
        return (
            <section className="w-screen h-screen flex flex-col items-center justify-center gap-5">
                <h1 className="font-bold max-w-lg text-center">{error.info}</h1>
                <button
                    className="btn btn-primary btn-neutral"
                    onClick={() => router.push("/files")}
                >
                    Go Back
                </button>
            </section>
        );

    if (isLoading)
        return (
            <section className="w-screen h-screen flex items-center justify-center">
                <span className="loading loading-infinity loading-lg text-primary"></span>
            </section>
        );

    return (
        <main>
            <section className="container mx-auto px-5 md:px-10 md:py-10 h-screen">
                <div className="flex flex-col items-center h-full w-full max-w-5xl p-2 mx-auto justify-between relative">
                    <div className="absolute right-1 bottom-5 md:bottom-10 z-50">
                        <button
                            className="btn btn-circle btn-primary cursor-pointer"
                            onClick={() => router.push(`/chat/${params.uid}`)}
                        >
                            <FaRocketchat />
                        </button>
                    </div>
                    <div className="flex justify-between w-full items-center border-b py-2 border-neutral">
                        <button
                            className="btn btn-circle"
                            onClick={router.back}
                        >
                            <FaCaretLeft />
                        </button>
                        <h2 className="text-2xl font-bold">LearnIt AI</h2>
                    </div>
                    <div className="flex-1 overflow-y-scroll py-5 flex flex-col gap-5">
                        {" "}
                        {data.data?.length ? (
                            <>
                                {data.data?.map((item, index) => (
                                    <div
                                        className="bg-neutral p-5 rounded-lg shadow-sm"
                                        key={index}
                                    >
                                        <h4 className="font-bold text-primary text-xs mb-2">
                                            Card {index + 1}
                                        </h4>
                                        <p>{item}</p>
                                    </div>
                                ))}
                                <div className="text-center divider">
                                    <p className="max-w-lg">End of Cards</p>
                                </div>
                            </>
                        ) : undefined}
                    </div>
                </div>
            </section>
        </main>
    );
}
