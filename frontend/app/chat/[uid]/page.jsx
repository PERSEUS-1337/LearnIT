"use client";

import React, { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import { FaCaretLeft, FaRobot, FaUserGraduate } from "react-icons/fa";
import { IoMdSend } from "react-icons/io";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import useWrapperStore from "@/stores/wrapper";

export default function Page() {
    const router = useRouter();
    const params = useParams();
    const [messages, setMessages] = useState([]);
    const [textBox, setTextBox] = useState("");
    const [loadingMessage, setLoadingMessage] = useState(false);
    const setErrorMessage = useWrapperStore((state) => state.setErrorMessage);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!textBox.trim().length) return;

        setMessages((prev) => [...prev, { sender: "user", message: textBox.trim() }]);
        setTextBox("");
        setLoadingMessage(true);

        try {
            const resp = await fetch(
                `/api/chat?filename=${params.uid}&query=${textBox.trim()}`
            );

            const data = await resp.json();

            if (resp.status >= 400) throw new Error(data);

            setMessages((prev) => [
                ...prev,
                { sender: "ai", message: data.message },
            ]);
        } catch (err) {
            setMessages([]);
            setErrorMessage(err.message);
        } finally {
            setLoadingMessage(false);
        }
    };

    return (
        <main>
            <section className="container mx-auto px-5 py-5 md:px-10 md:py-10 h-screen">
                <div className="flex flex-col items-center h-full w-full max-w-5xl p-2 mx-auto justify-between">
                    <div className="flex justify-between w-full items-center border-b py-2 border-neutral">
                        <button
                            className="btn btn-circle"
                            onClick={router.back}
                        >
                            <FaCaretLeft />
                        </button>
                        <h2 className="text-2xl font-bold">LearnIt AI</h2>
                    </div>
                    {messages.length ? (
                        <div className="flex-1 overflow-scroll overflow-y-auto w-full flex flex-col gap-2 px-5">
                            {messages.map((item, index) => (
                                <div
                                    className={`chat ${
                                        item.sender === "user"
                                            ? "chat-end"
                                            : "chat-start"
                                    }`}
                                    key={index}
                                >
                                    <div className="chat-image">
                                        <div className="w-10 h-10 bg-neutral rounded-full flex items-center justify-center">
                                            {item.sender === "user" ? (
                                                <FaUserGraduate className="text-xl" />
                                            ) : (
                                                <FaRobot className="text-xl" />
                                            )}
                                        </div>
                                    </div>
                                    <div className="chat-header">
                                        {item.sender === "user" ? (
                                            <p>Your Question</p>
                                        ) : (
                                            <p>LearnIt AI</p>
                                        )}
                                    </div>
                                    <div className="chat-bubble">
                                        {item.sender === "user" ? (
                                            item.message
                                        ) : (
                                            <ReactMarkdown
                                                remarkPlugins={[remarkGfm]}
                                            >
                                                {item.message}
                                            </ReactMarkdown>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {loadingMessage ? (
                                <div className="chat chat-start">
                                    <div className="chat-image">
                                        <div className="w-10 h-10 bg-neutral rounded-full flex items-center justify-center">
                                            <FaRobot className="text-xl" />
                                        </div>
                                    </div>
                                    <div className="chat-header">
                                        LearnIt AI
                                    </div>
                                    <div className="chat-bubble flex items-center gap-2">
                                        <p>i am typing</p>
                                        <span className="loading loading-infinity text-primary"></span>
                                    </div>
                                </div>
                            ) : undefined}
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-2">
                            <div className="border p-8 rounded-lg">
                                <Image
                                    src="/images/chat.svg"
                                    height="300"
                                    width="300"
                                    alt="Bird waiting for the user to chat."
                                />
                            </div>
                            <p className="text-sm">
                                Start by asking queries for this application.
                            </p>
                        </div>
                    )}
                    <div>
                        <p className="text-center text-sm mb-2">
                            I do not save any chat histories. Each question has
                            its own context.
                        </p>
                    </div>
                    <form className="w-full relative" onSubmit={handleSubmit}>
                        <label className="input input-bordered rounded-full flex items-center gap-2">
                            <input
                                type="text"
                                className="grow"
                                placeholder="Enter query here"
                                value={textBox}
                                onChange={(e) => setTextBox(e.target.value)}
                            />
                            <button
                                className="btn btn-circle btn-sm"
                                type="submit"
                            >
                                <IoMdSend className="text-lg" />
                            </button>
                        </label>
                    </form>
                </div>
            </section>
        </main>
    );
}
