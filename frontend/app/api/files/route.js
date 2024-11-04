import { cookies } from "next/headers";

export async function GET(request) {
    const accessToken = cookies().get("access-token");

    const resp = await fetch(`${process.env.API_URL}/user/file/list`, {
        headers: {
            Authorization: `Bearer ${accessToken.value}`,
        },
        method: "GET",
    });
    const data = await resp.json();

    return Response.json({ data });
}
