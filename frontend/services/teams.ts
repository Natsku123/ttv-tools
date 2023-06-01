import {Membership, Team, TeamInvite} from "@/services/types";
import {AxiosError, AxiosResponse} from "axios";
import {client} from "@/services/client";

const getTeams = () => {
    return new Promise<Array<Team>>(async (resolve, reject) => {
        client
            .get(`/api/teams/`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const createTeam = (team: Team) => {
    return new Promise<Team>(async (resolve, reject) => {
        client
            .post(`/api/teams/`, team)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getTeam = (uuid: string | string[] | undefined) => {
    if (uuid) {
        return new Promise<Team>(async (resolve, reject) => {
            client
                .get(`/api/teams/${uuid}`)
                .then((res: AxiosResponse) => {
                    resolve(res.data);
                })
                .catch((error: AxiosError) => reject(error));
        });
    }
    return null;
}

const getInvitesByTeam = (team_uuid: string) => {
    return new Promise<Array<TeamInvite>>(async (resolve, reject) => {
        client
            .get(`/api/teams/${team_uuid}/invites`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const updateTeam = (uuid: string, team: Team) => {
    return new Promise<Team>(async (resolve, reject) => {
        client
            .put(`/api/teams/${uuid}`, team)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const deleteTeam = (uuid: string) => {
    return new Promise<Team>(async (resolve, reject) => {
        client
            .delete(`/api/teams/${uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getMembers = (team_uuid: string) => {
    return new Promise<Array<Membership>>(async (resolve, reject) => {
        client
            .get(`/api/teams/${team_uuid}/members`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const getMember = (team_uuid: string, user_uuid: string) => {
    return new Promise<Membership>(async (resolve, reject) => {
        client
            .get(`/api/teams/${team_uuid}/members/${user_uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const updateMember = (team_uuid: string, user_uuid: string, member: Membership) => {
    return new Promise<Membership>(async (resolve, reject) => {
        client
            .put(`/api/teams/${team_uuid}/members/${user_uuid}`, member)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

const deleteMember = (team_uuid: string, user_uuid: string) => {
    return new Promise<Membership>(async (resolve, reject) => {
        client
            .delete(`/api/teams/${team_uuid}/members/${user_uuid}`)
            .then((res: AxiosResponse) => {
                resolve(res.data);
            })
            .catch((error: AxiosError) => reject(error));
    });
}

export {
    getMember,
    getTeams,
    getTeam,
    getMembers,
    getInvitesByTeam,
    createTeam,
    deleteMember,
    updateMember,
    updateTeam
}