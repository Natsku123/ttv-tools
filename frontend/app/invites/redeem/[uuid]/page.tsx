'use client'
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Team, TeamInvite, User} from "@/src/services/types";
import {AxiosError} from "axios";
import {getInvite, redeemInvite} from "@/src/services/invites";
import {getCurrentUser} from "@/src/services/users";
import {getTwitchUsersById} from "@/src/services/twitch";
import {getTeam} from "@/src/services/teams";
import {Avatar, Box, Button, Grid, Paper, Typography} from "@mui/material";
import ErrorMessage from "@/src/components/ErrorMessage";
import {redirect} from "next/navigation";

export default function RedeemInvitePage({params}: { params: { uuid: string } }) {
    const queryClient = useQueryClient();

    const {
        data,
        error,
        isLoading
    }: UseQueryResult<TeamInvite, AxiosError> = useQuery(["invites", params.uuid], () => getInvite(params.uuid as string), {
        enabled: !!params.uuid
    });

    const {
        data: currentUser,
        isError: isUserError
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry: false
    });

    const twitchId = data?.user_twitch_id;


    const {
        data: twitch_users,
    }: UseQueryResult<{
        data: [{ id: string, display_name: string, login: string, profile_image_url: string }]
    }, AxiosError> = useQuery(["twitch_users"], () => getTwitchUsersById(data?.user_twitch_id as string), {enabled: !!twitchId});


    const teamUuid = data?.team_uuid;

    const {
        data: team,
        isLoading: teamLoading
    }: UseQueryResult<Team, AxiosError> = useQuery(["teams", teamUuid], () => getTeam(teamUuid), {
        enabled: !!teamUuid
    });

    const redeem = useMutation({
        mutationFn: redeemInvite,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['invites']})
            await queryClient.invalidateQueries({queryKey: ['invites', data.uuid]});
            redirect("/")
        }
    });

    return <Paper>
        <Box px={2} py={4}>
            {isLoading && !isUserError ? <>
                loading
            </> : <>
                {isUserError && <>
                    <Grid container spacing={2} justifyContent={"center"} alignItems={"center"} direction={"column"}>
                        <Grid item xs>
                            <Typography variant={"h3"}>Login to continue</Typography>
                        </Grid>
                        <Grid item xs>
                            <Button href={`/api/twitch/login?redirect=invites/redeem/${params.uuid}`} size={"large"}>Login</Button>
                        </Grid>
                    </Grid>
                </>}
                {error && !isUserError && <ErrorMessage code={error.code} message={error.message}/>}
                {data && !isUserError && currentUser && <>
                    {currentUser.twitch_id.toString() === data.user_twitch_id ? <>
                        <Grid container spacing={2} justifyContent={"center"} alignItems={"center"} direction="column">
                            <Grid item>
                                {twitch_users && <Avatar alt={twitch_users.data[0].display_name}
                                                         src={twitch_users.data[0].profile_image_url}
                                                         sx={{width: 256, height: 256}}/>}
                            </Grid>
                            <Grid item>
                                <Typography variant={"h4"}>You, <b>{currentUser.name}</b>, have been invited to
                                    join <b>{team?.name}</b>!!</Typography>
                            </Grid>
                            <Grid item>
                                <Button variant={"outlined"}
                                        onClick={() => redeem.mutate(params.uuid as string)}>Join!</Button>
                            </Grid>
                        </Grid>
                    </> : <>
                        <Typography variant={"h4"}>This invite is not for you, sorry!</Typography>
                    </>}
                </>}
            </>}
        </Box>
    </Paper>;
}