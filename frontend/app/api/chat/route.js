import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request) {
    const accessToken = cookies().get("access-token");
    const searchParams = request.nextUrl.searchParams;
    const fileName = searchParams.get("filename");
    const query = searchParams.get("query");

    const resp = await fetch(
        `${process.env.API_URL}/docu/query-rag?filename=${fileName}&query=${query}`,
        {
            headers: {
                Authorization: `Bearer ${accessToken.value}`,
            },
            method: "GET",
        }
    );
    const data = await resp.json();


    if (data.detail) return NextResponse.json(data.detail, { status: 400 });

    return Response.json({ message: data.data.response });
}
