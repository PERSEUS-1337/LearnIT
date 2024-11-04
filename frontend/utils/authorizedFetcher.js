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

};
