import { cookies } from "next/headers";

export async function DELETE(request) {
    const accessToken = cookies().get("access-token");
    const searchParams = request.nextUrl.searchParams;
    const fileName = searchParams.get("filename");

    const resp = await fetch(
        `${process.env.API_URL}/docu/?filename=${fileName}`,
        {
            headers: {
                Authorization: `Bearer ${accessToken.value}`,
            },
            method: "DELETE",
        }
    );

    const data = await resp.json();

    if (data.detail) return Response.json({ error: data.detail });

    return Response.json({});
}
