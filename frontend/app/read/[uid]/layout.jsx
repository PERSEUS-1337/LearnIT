"use server";

import { cookies } from "next/headers";
import { notFound } from "next/navigation";

export default async function Layout({ children }) {
    const accessToken = cookies().get("access-token");

    if (!accessToken) notFound();

    return children;
}
