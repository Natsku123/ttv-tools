import {useRouter} from "next/router";
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Team, TeamInvite, User} from "@/services/types";
import {AxiosError} from "axios";
import {deleteInvite, getInvite, redeemInvite} from "@/services/invites";
import {getCurrentUser} from "@/services/users";
import {getTwitchUsersById} from "@/services/twitch";
import {getTeam} from "@/services/teams";
import {redirect} from "next/navigation";
import {Avatar, Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import ErrorMessage from "@/components/ErrorMessage";
import {formatRFC7231} from "date-fns";
import DeleteIcon from "@mui/icons-material/Delete";

export default function RedeemInvitePage() {

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

    const redeem = useMutation({
        mutationFn: redeemInvite,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['invites']})
            await queryClient.invalidateQueries({queryKey: ['invites', data.uuid]});
        }
    });

    return <Paper>
        <Box px={2} py={4}>
            { isLoading ? <>
                loading
            </> : <>
            { error && <ErrorMessage code={error.code} message={error.message} />}
            { data && <>
                { currentUser?.twitch_id === data.user_twitch_id ? <>
                    <Grid container spacing={2} justifyContent={"center"} alignItems={"center"} direction="column">
                        <Grid item>
                            { twitch_users && <Avatar alt={twitch_users.data[0].display_name} src={twitch_users.data[0].profile_image_url} sx={{ width: 256, height: 256 }} /> }
                        </Grid>
                        <Grid item>
                            <Typography variant={"h4"}>You, <b>{currentUser.name}</b>, have been invited to join <b>{team?.name}</b>!!</Typography>
                        </Grid>
                        <Grid item>
                            <Button variant={"outlined"} onClick={() => redeem.mutate(router.query.uuid as string)}>Join!</Button>
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