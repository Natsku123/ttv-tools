import {TeamInvite} from "@/src/services/types";
import {AxiosError, AxiosResponse} from "axios";
import {client} from "@/src/services/client";

const getInvites = () => {
    return new Promise<Array<TeamInvite>>(async (resolve, reject) => {
        client
            .get(`/api/invites/`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const createInvite = (invite: TeamInvite) => {
    return new Promise<TeamInvite>(async (resolve, reject) => {
        client
            .post(`/api/invites/`, invite)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getInvite = (uuid: string) => {
    return new Promise<TeamInvite>(async (resolve, reject) => {
        client
            .get(`/api/invites/${uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const updateInvite = (uuid: string, invite: TeamInvite) => {
    return new Promise<TeamInvite>(async (resolve, reject) => {
        client
            .put(`/api/invites/${uuid}`, invite)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const deleteInvite = (uuid: string) => {
    return new Promise<TeamInvite>(async (resolve, reject) => {
        client
            .delete(`/api/invites/${uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const redeemInvite = (uuid: string) => {
    return new Promise<TeamInvite>(async (resolve, reject) => {
        client
            .post(`/api/invites/${uuid}/redeem`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getInvites,
    getInvite,
    createInvite,
    redeemInvite,
    updateInvite,
    deleteInvite
}