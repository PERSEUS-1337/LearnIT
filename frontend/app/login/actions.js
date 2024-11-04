"use server";

import { redirect } from "next/navigation";
import { cookies } from "next/headers";

export async function submitForm(username, password) {
    const resp = await fetch(`${process.env.API_URL}/auth/login`, {
        body: new URLSearchParams({
            username,
            password,
            remember_me: true,
        }),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method: "POST",
    });

    const data = await resp.json();

    if (data.detail) return {error: data.detail};

    cookies().set("access-token", data.access_token, {
        secure: true,
        httpOnly: true,
        sameSite: "strict",
        path: "/",
    });

    redirect("/app");
}
