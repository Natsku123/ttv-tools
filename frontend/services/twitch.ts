import {client} from "@/services/client";
import {AxiosError, AxiosResponse} from "axios";

const getTwitchUsers = (login: string) => {
    return new Promise<Array<any>>(async (resolve, reject) => {
        client
            .get("/api/twitch/users", { params: {login}})
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getTwitchUsers
}