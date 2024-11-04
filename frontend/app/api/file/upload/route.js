import { cookies } from "next/headers";

export async function POST(request, respone) {
    const accessToken = cookies().get("access-token");
    const formData = await request.formData();
    const resp = await fetch(`${process.env.API_URL}/docu/upload`, {
        headers: {
            Authorization: `Bearer ${accessToken.value}`,
        },
        method: "POST",
        body: formData,
    });

    const data = await resp.json();

    if (data.detail) return Response.json({ error: data.detail });

    return Response.json({});
}
