import {AxiosError, AxiosResponse} from "axios";
import {Team, User} from "@/src/services/types";
import {client} from "@/src/services/client";

const getCurrentUser = () => {
    return new Promise<User>(async (resolve, reject) => {
        client
            .get("/api/users/")
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getUsers = () => {
    return new Promise<Array<User>>(async (resolve, reject) => {
        client
            .get("/api/users/all")
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getUser = (user_uuid: string | string[] | undefined) => {
    if (user_uuid) {
        return new Promise<User>(async (resolve, reject) => {
            client
                .get(`/api/users/${user_uuid}`)
                .then((res: AxiosResponse) => {
                    resolve(res.data);
                })
                .catch((error: AxiosError) => reject(error));
        });
    }
    return null;
}

const updateUser = (user_uuid: string, user: User) => {
    return new Promise<User>(async (resolve, reject) => {
        client
            .put(`/api/users/${user_uuid}`, user)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const deleteUser = (user_uuid: string) => {
    return new Promise<User>(async (resolve, reject) => {
        client
            .delete(`/api/users/${user_uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getTeams = () => {
    return new Promise<Array<Team>>(async (resolve, reject) => {
        client
            .delete(`/api/users/teams`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getCurrentUser,
    getUser,
    getUsers,
    getTeams,
    updateUser,
    deleteUser
}