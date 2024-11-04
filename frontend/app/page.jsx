import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default function Home() {
    const accessToken = cookies().get("access-token");

    if (accessToken) return redirect("/app");

    return redirect("/login");
}
