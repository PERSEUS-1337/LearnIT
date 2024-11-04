"use client";

import { FaFileSignature, FaFileUpload, FaUserClock } from "react-icons/fa";
import Image from "next/image";
import useSWR from "swr";
import { useRouter } from "next/navigation";
import { logout } from "./actions";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function Page() {
    const router = useRouter();
    const { data, error, isLoading } = useSWR("/api/user", fetcher);

    if (isLoading)
        return (
            <section className="w-screen h-screen flex items-center justify-center">
                <span className="loading loading-infinity loading-lg text-primary"></span>
            </section>
        );

    if (error) throw new Error();

    return (
        <main>
            <section className="container mx-auto px-5 py-5 md:px-10 md:py-10 h-screen">
                <div className="flex flex-col items-center h-full justify-between">
                    <div className="flex-1 flex flex-col justify-center gap-10">
                        <div className="flex flex-col items-center">
                            <Image
                                src="/images/welcome.svg"
                                height="300"
                                width="300"
                                alt="Lady waving"
                                className="w-44"
                            />
                            <h3 className="text-xl md:text-2xl">Hello</h3>
                            <h2 className="text-2xl md:text-4xl text-primary font-bold">
                                {data?.user.full_name}
                            </h2>
                        </div>
                        <div className="grid grid-cols-3 gap-2 md:gap-5">
                            <div className="bg-neutral text-neutral-content rounded-lg p-3 md:p-4 col-span-1">
                                <h2 className="flex flex-col md:gap-y-2 font-medium text-md">
                                    <FaFileUpload className="text-lg md:text-xl" />
                                    Files Uploaded
                                </h2>
                                <p className="text-lg md:text-xl font-bold mt-2 text-primary">
                                    {data.uploads} files
                                </p>
                            </div>
                            <div className="bg-neutral text-neutral-content rounded-lg p-3 md:p-4 col-span-1">
                                <h2 className="flex flex-col md:gap-y-2 font-medium text-md">
                                    <FaFileSignature className="text-lg md:text-xl" />
                                    Files Processed
                                </h2>
                                <p className="text-lg md:text-xl font-bold mt-2 text-primary">
                                    {data.total_files_processed} files
                                </p>
                            </div>
                            <div className="bg-neutral text-neutral-content rounded-lg p-3 md:p-4 col-span-1">
                                <h2 className="flex flex-col md:gap-y-2 font-medium text-md">
                                    <FaUserClock className="text-lg md:text-xl" />
                                    Reading Time
                                </h2>
                                <p className="text-lg md:text-xl font-bold mt-2 text-primary">
                                    {data.total_approximated_reading_time_minutes >
                                    60
                                        ? `${Math.floor(
                                              data.total_approximated_reading_time_minutes /
                                                  60
                                          )} h`
                                        : `${Math.round(
                                              data.total_approximated_reading_time_minutes
                                          )} mins`}{" "}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="w-full max-w-lg flex flex-col items-center">
                        <button
                            className="btn btn-circle btn-primary w-full"
                            onClick={() => router.push("/files")}
                        >
                            Let&apos;s Learn
                        </button>
                        <p className="text-center text-base-content mt-2 text-xs">
                            Enhance your learning experience
                        </p>

                        <button
                            className="btn mt-5 btn-ghost"
                            onClick={() => logout()}
                        >
                            Logout Account
                        </button>
                    </div>
                </div>
            </section>
        </main>
    );
}
