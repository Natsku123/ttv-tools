import {AxiosError, AxiosResponse} from "axios";
import {EventSubscription} from "@/services/types";
import {client} from "@/services/client";

const getEventSubs = () => {
    return new Promise<Array<EventSubscription>>(async (resolve, reject) => {
        client
            .get("/api/eventsubs/")
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getEventSubsByUser = (user_uuid: string | undefined) => {
    if (user_uuid) {
        return new Promise<Array<EventSubscription>>(async (resolve, reject) => {
            client
                .get(`/api/eventsubs/user/${user_uuid}`)
                .then((res: AxiosResponse) => {
                    resolve(res.data);
                })
                .catch((error: AxiosError) => reject(error));
        });
    }
    return null;
}

const createEventSub = (eventsub: EventSubscription) => {
    return new Promise<EventSubscription>(async (resolve, reject) => {
        client
            .post(`/api/eventsubs/`, eventsub)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getEventSub = (uuid: string) => {
    return new Promise<Array<EventSubscription>>(async (resolve, reject) => {
        client
            .get(`/api/eventsubs/${uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const updateEventSub = (uuid: string, eventsub: EventSubscription) => {
    return new Promise<EventSubscription>(async (resolve, reject) => {
        client
            .put(`/api/eventsubs/${uuid}`, eventsub)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const deleteEventSub = (uuid: string) => {
    return new Promise<EventSubscription>(async (resolve, reject) => {
        client
            .delete(`/api/eventsubs/${uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getEventSubs,
    getEventSubsByUser,
    getEventSub,
    updateEventSub,
    deleteEventSub,
    createEventSub
}