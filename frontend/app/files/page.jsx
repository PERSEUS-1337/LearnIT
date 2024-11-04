"use client";

import { useState } from "react";
import {
    FaCaretLeft,
    FaCloudUploadAlt,
    FaEye,
    FaPlus,
    FaRocketchat,
    FaTrash,
} from "react-icons/fa";
import { BsThreeDotsVertical } from "react-icons/bs";
import moment from "moment";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";
import useSWR, { useSWRConfig } from "swr";
import useWrapperStore from "@/stores/wrapper";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function Page() {
    const router = useRouter();
    const [file, setFile] = useState(null);
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [confirmDeleteModalOpen, setConfirmDeleteModalOpen] = useState(null);
    const { setWrapperLoading, setSuccessMessage, setErrorMessage } =
        useWrapperStore((state) => ({
            setWrapperLoading: state.setIsLoading,
            setSuccessMessage: state.setSuccessMessage,
            setErrorMessage: state.setErrorMessage,
        }));

    const { data, error, isLoading } = useSWR("/api/files", fetcher, {
        refreshInterval: 1500,
    });
    const { mutate } = useSWRConfig();

    if (isLoading)
        return (
            <section className="w-screen h-screen flex items-center justify-center">
                <span className="loading loading-infinity loading-lg text-primary"></span>
            </section>
        );

    const uploadFile = async () => {
        setUploadModalOpen(false);
        setWrapperLoading(true);
        const formData = new FormData();
        formData.append("file", file);
        try {
            const resp = await fetch("/api/file/upload", {
                method: "POST",
                body: formData,
            });
            const data = await resp.json();

            if (data.error) throw new Error(data.error);

            setSuccessMessage("Successfully uploaded file.");
            mutate("/api/files");
        } catch (err) {
            setErrorMessage(err.message);
        } finally {
            setWrapperLoading(false);
        }
    };

    const deleteFile = async () => {
        setConfirmDeleteModalOpen(null);
        setWrapperLoading(true);
        try {
            const resp = await fetch(
                `/api/file?filename=${confirmDeleteModalOpen}`,
                {
                    method: "DELETE",
                }
            );
            const data = await resp.json();

            if (data.error) throw new Error(data.error);

            setSuccessMessage("Successfully deleted file.");
            mutate("/api/files");
        } catch (error) {
            setErrorMessage(err.message);
        } finally {
            setWrapperLoading(false);
        }
    };

    const processTSCC = async (fileName) => {
        setWrapperLoading(true);
        const formData = new FormData();
        formData.append("filename", fileName);
        // formData.append("llm", "dev");
        try {
            const resp = await fetch("/api/file/process", {
                method: "POST",
                body: formData,
            });
            const data = await resp.json();

            if (data.error) throw new Error(data.error);

            setSuccessMessage(`Successfully started processing of file.`);
            mutate("/api/files");
        } catch (err) {
            setErrorMessage(err.message);
        } finally {
            setWrapperLoading(false);
        }
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (file.type !== "application/pdf")
            return setErrorMessage(`File ${file.name} is of invalid type.`);

        setFile(file);
        setUploadModalOpen(true);
    };

    return (
        <main>
            <dialog
                id="upload-modal"
                className={`modal ${uploadModalOpen ? "modal-open" : ""}`}
            >
                <div className="modal-box">
                    <h3 className="font-bold text-lg">Upload File</h3>
                    <p className="py-4">
                        Are you sure you want to upload{" "}
                        <strong className="text-primary">{file?.name}</strong>?
                    </p>
                    <div className="modal-action">
                        <button
                            className="btn btn-primary"
                            onClick={uploadFile}
                        >
                            Confirm
                        </button>
                    </div>
                </div>
                <form
                    method="dialog"
                    className="modal-backdrop"
                    onSubmit={() => setUploadModalOpen(false)}
                >
                    <button>close</button>
                </form>
            </dialog>
            <dialog
                id="delete-modal"
                className={`modal ${
                    confirmDeleteModalOpen ? "modal-open" : ""
                }`}
            >
                <div className="modal-box">
                    <h3 className="font-bold text-lg">Confirm Delete</h3>
                    <p className="py-4">
                        Deleting this file will delete all your tokens and
                        reading progress. Are you sure you want to delete{" "}
                        <span className="font-bold">
                            {confirmDeleteModalOpen}
                        </span>
                        ?
                    </p>
                    <div className="modal-action">
                        <button className="btn btn-error" onClick={deleteFile}>
                            Confirm
                        </button>
                    </div>
                </div>
                <form
                    method="dialog"
                    className="modal-backdrop"
                    onSubmit={() => setConfirmDeleteModalOpen(null)}
                >
                    <button>close</button>
                </form>
            </dialog>
            <section className="container mx-auto px-5 py-1 md:px-10 h-screen">
                <div className="flex flex-col items-center h-full">
                    <div className="flex justify-between w-full items-center border-b py-2 border-neutral">
                        <button
                            className="btn btn-circle"
                            onClick={router.back}
                        >
                            <FaCaretLeft />
                        </button>
                        <h2 className="text-2xl font-bold">Files</h2>
                    </div>
                    <div className="flex-1 flex flex-col relative w-full py-2">
                        <div className="flex-1 py-2 overflow-y-scroll">
                            <div className="grid gap-y-2">
                                {data.data.length ? (
                                    data.data.map((item, index) => (
                                        <div
                                            className="border-b border-neutral relative pb-4 flex items-center gap-2"
                                            key={index}
                                        >
                                            {!item.status ||
                                            item.status.progress === 100 ? (
                                                <div className="dropdown dropdown-right dropdown-hover">
                                                    <div
                                                        tabIndex={0}
                                                        role="button"
                                                        className="btn btn-circle btn-sm"
                                                    >
                                                        <BsThreeDotsVertical className="text-lg" />
                                                    </div>
                                                    <ul
                                                        tabIndex={0}
                                                        className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
                                                    >
                                                        <li
                                                            className={`${
                                                                item.processed &&
                                                                item.status
                                                                    ?.progress ===
                                                                    100
                                                                    ? ""
                                                                    : "hidden"
                                                            }`}
                                                        >
                                                            <Link
                                                                href={`/read/${item.name}`}
                                                            >
                                                                <FaEye /> Read
                                                            </Link>
                                                        </li>
                                                        <li
                                                            className={`${
                                                                item.processed &&
                                                                item.status
                                                                    ?.progress ===
                                                                    100
                                                                    ? ""
                                                                    : "hidden"
                                                            }`}
                                                        >
                                                            <Link
                                                                href={`/chat/${item.name}`}
                                                            >
                                                                <FaRocketchat />{" "}
                                                                Chat
                                                            </Link>
                                                        </li>
                                                        <li
                                                            className={`${
                                                                item.status
                                                                    ? "hidden"
                                                                    : ""
                                                            }`}
                                                        >
                                                            <p
                                                                onClick={() =>
                                                                    processTSCC(
                                                                        item.name
                                                                    )
                                                                }
                                                            >
                                                                <FaCloudUploadAlt />{" "}
                                                                Process File
                                                            </p>
                                                        </li>
                                                        <li>
                                                            <p
                                                                onClick={() =>
                                                                    setConfirmDeleteModalOpen(
                                                                        item.name
                                                                    )
                                                                }
                                                            >
                                                                <FaTrash />
                                                                Delete
                                                            </p>
                                                        </li>
                                                    </ul>
                                                </div>
                                            ) : (
                                                <span className="loading loading-infinity text-primary"></span>
                                            )}
                                            <div className="flex flex-col flex-1 [overflow-wrap:anywhere]">
                                                <h2 className="font-bold">
                                                    {item.name}
                                                </h2>
                                                <p className="text-xs">
                                                    Uploaded on{" "}
                                                    {moment(
                                                        item.uploaded_at
                                                    ).format("MMMM DD")}
                                                </p>
                                                {!item.processed &&
                                                item.status ? (
                                                    <div className="flex flex-col text-xs gap-2 opacity-75 mt-4 w-full">
                                                        <p>
                                                            {
                                                                item.status
                                                                    .message
                                                            }
                                                        </p>
                                                        <progress
                                                            className="progress w-56"
                                                            value={
                                                                item.status
                                                                    .progress
                                                            }
                                                            max="100"
                                                        ></progress>
                                                    </div>
                                                ) : undefined}
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="py-10 w-full h-full flex flex-col items-center justify-center gap-2">
                                        <Image
                                            src="/images/empty.svg"
                                            height={200}
                                            width={200}
                                            className="w-42"
                                            alt="Empty feeling"
                                        />
                                        <h4 className="text-lg font-bold">
                                            No Files Uploaded
                                        </h4>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="absolute right-1 bottom-5 md:bottom-10">
                            <label
                                htmlFor="file-upload"
                                className="btn btn-circle btn-primary cursor-pointer"
                            >
                                <FaPlus />
                            </label>
                            <input
                                id="file-upload"
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                        </div>
                    </div>
                </div>
            </section>
        </main>
    );
}
