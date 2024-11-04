import useUserStore from "@/stores/user";
import apiInstance from "./api";

export default (url) => {
    const bearerToken = useUserStore((state) => state.bearerToken);

    return (url) =>
        apiInstance
            .get(url, {
                headers: { Authorization: `Bearer ${bearerToken}` },
            })
            .then((res) => res.data);
    // return (url) =>
    //     fetch(`${process.env.NEXT_PUBLIC_API_URL}/${url}`, {
    //         headers: {
    //             Authorization: `Bearer ${bearerToken}`,
    //             "Access-Control-Allow-Origin": "*",
    //             "Content-Type": "application/x-www-form-urlencoded",
    //         },
    //         method: "GET",
    //     }).then((response) => response.json());
};
