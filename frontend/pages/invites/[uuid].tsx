import { useRouter } from 'next/router';
import {Avatar, Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Team, TeamInvite, User} from "@/services/types";
import {AxiosError} from "axios";
import ErrorMessage from "@/components/ErrorMessage";
import { formatRFC7231 } from 'date-fns';
import {getTeam} from "@/services/teams";
import {getCurrentUser} from "@/services/users";
import DeleteIcon from "@mui/icons-material/Delete";
import {deleteInvite, getInvite} from "@/services/invites";
import {getTwitchUsersById} from "@/services/twitch";
import {redirect} from "next/navigation";

export default function InvitePage() {
    const router = useRouter();

    const queryClient = useQueryClient();

    const {
        data,
        error,
        isLoading
    }: UseQueryResult<TeamInvite, AxiosError> = useQuery(["invites", router.query.uuid], () => getInvite(router.query.uuid as string), {
        enabled: !!router.query.uuid
    });

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });

    const twitchId = data?.user_twitch_id;


    const {
        data: twitch_users,
    }: UseQueryResult<{data: [{id: string, display_name: string, login: string, profile_image_url: string}]}, AxiosError> = useQuery(["twitch_users"], () => getTwitchUsersById(data?.user_twitch_id as string), {enabled: !!twitchId});


    const teamUuid = data?.team_uuid;

    const {
        data: team,
        isLoading: teamLoading
    }: UseQueryResult<Team, AxiosError> = useQuery(["teams", teamUuid], () => getTeam(teamUuid), {
        enabled: !!teamUuid
    });


    const remove = useMutation({
        mutationFn: deleteInvite,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['invites']})
            await queryClient.invalidateQueries({queryKey: ['invites', data.uuid]});
            redirect("/invites")
        }
    });

    const origin =
        typeof window !== 'undefined' && window.location.origin
            ? window.location.origin
            : '';

    return <Paper>
        <Box px={2} py={4}>
            { isLoading ? <>
                <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={12}>
                        <Typography variant={"h3"}><Skeleton /></Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><b>To team</b>: <Skeleton /></Typography>
                        <Typography><b>Created on</b>: <Skeleton /></Typography>
                        <Typography><b>Updated on</b>: <Skeleton /></Typography>
                    </Grid>
                </Grid>
            </> : <>
                { error && <ErrorMessage code={error.code} message={error.message} />}
                { data && <>
                  <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={12}>
                      <Typography variant={"h3"}>Invite for {data.user_twitch_id}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography><b>To team</b>: {!teamLoading ? (team && team.name) : <Skeleton />}</Typography>
                      <Typography><b>Created on</b>: {data.created_on && formatRFC7231(new Date(data.created_on))}</Typography>
                      <Typography><b>Updated on</b>: {data.updated_on && formatRFC7231(new Date(data.updated_on))}</Typography>
                      <Box py={2}>
                        <Grid container>
                          <Grid item xs={2}>
                              {twitch_users && "data" in twitch_users && twitch_users["data"].map(u => <div key={u.id}>
                                  <Grid container justifyContent={"space-around"} alignItems={"center"}>
                                      <Grid item><Avatar src={u.profile_image_url} /></Grid>
                                      <Grid item><Typography>{u.display_name}</Typography></Grid>
                                  </Grid>
                              </div>)}
                          </Grid>
                        </Grid>
                      </Box>
                      <Box py={2}>
                        <Grid container spacing={2}>
                          <Grid item><Button variant={"outlined"} color={"primary"} onClick={() => {navigator.clipboard.writeText(`${origin}/invites/redeem/${data?.uuid}`)}}>Copy link</Button></Grid>
                            {currentUser?.is_superadmin && <Grid item>
                              <Button variant={"outlined"} color={"error"} onClick={() => remove.mutate("uuid" in data ? data.uuid as string : "" )}><DeleteIcon /></Button>
                            </Grid>}
                        </Grid>
                      </Box>
                    </Grid>
                  </Grid>
                </>}
            </> }

        </Box>
    </Paper>;
}