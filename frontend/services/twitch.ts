import {client} from "@/services/client";
import {AxiosError, AxiosResponse} from "axios";

const getTwitchUsers = (login: string | string[]) => {
    return new Promise<Array<any>>(async (resolve, reject) => {
        client
            .get("/api/twitch/users", { params: {login}})
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getTwitchUsersById = (id: string | string[]) => {
    return new Promise<Array<any>>(async (resolve, reject) => {
        client
            .get("/api/twitch/users", { params: {id}})
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getTwitchUsers,
    getTwitchUsersById
}