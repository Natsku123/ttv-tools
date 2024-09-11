import {DiscordServer} from "@/src/services/types";
import {AxiosError, AxiosResponse} from "axios";
import {client} from "@/src/services/client";

const getDiscordServers = () => {
    return new Promise<Array<DiscordServer>>(async (resolve, reject) => {
        client
            .get("/api/discord/servers")
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getDiscordServer = (id: string) => {
    return new Promise<DiscordServer>(async (resolve, reject) => {
        client
            .get(`/api/discord/servers/${id}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getDiscordServers,
    getDiscordServer
}