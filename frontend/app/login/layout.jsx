"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function Layout({ children }) {
    const accessToken = cookies().get("access-token");

    if (accessToken) return redirect("/app");

    return children;
}
