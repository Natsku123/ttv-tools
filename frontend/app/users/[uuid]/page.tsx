'use client'
import {Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {User} from "@/src/services/types";
import {AxiosError} from "axios";
import {deleteUser, getCurrentUser, getUser} from "@/src/services/users";
import ErrorMessage from "@/src/components/ErrorMessage";
import UserAvatar from "@/src/components/UserAvatar";
import Link from "next/link";
import {formatRFC7231} from 'date-fns';
import DeleteIcon from "@mui/icons-material/Delete";
import {useRouter} from "next/navigation";

export default function UserPage({params}: { params: { uuid: string } }) {
    const queryClient = useQueryClient();
    const router = useRouter();

    const {
        data,
        error,
        isLoading
    }: UseQueryResult<User, AxiosError> = useQuery(["user", params.uuid], () => getUser(params.uuid), {
        retry: false
    });

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry: false
    });

    const remove = useMutation({
        mutationFn: deleteUser,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['users']})
            await queryClient.invalidateQueries({queryKey: ['users', data.uuid]});
            router.push("/");
            router.refresh();
        }
    });

    return <Paper>
        <Box px={2} py={4}>
            {isLoading ? <>
                <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={2}>
                        <Skeleton variant="circular" width={128} height={128}/>
                    </Grid>
                    <Grid item xs={10}>
                        <Typography variant={"h3"}><Skeleton/></Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><b>Twitch Description</b>: <Skeleton/></Typography>
                        <Typography><b>Twitch Login Name</b>: <Skeleton/></Typography>
                        <Typography><b>Created on</b>: <Skeleton/></Typography>
                        <Typography><b>Updated on</b>: <Skeleton/></Typography>
                        <Typography><b>Discord</b>: <Skeleton/></Typography>
                        <Box py={2}>
                            <Typography variant={"h4"}>Teams</Typography>
                        </Box>
                    </Grid>
                </Grid>
            </> : <>
                {error && <ErrorMessage code={error.code} message={error.message}/>}
                {data && <>
                    <Grid container spacing={4} alignItems={"center"}>
                        <Grid item xs={2}>
                            <UserAvatar user={data} sx={{width: 128, height: 128}}/>
                        </Grid>
                        <Grid item xs={10}>
                            <Typography variant={"h3"}>{data.name}</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography><b>Twitch Description</b>: {data.description}</Typography>
                            <Typography><b>Twitch Login Name</b>: {data.login_name}</Typography>
                            <Typography><b>Created on</b>: {data.created_on && formatRFC7231(new Date(data.created_on))}
                            </Typography>
                            <Typography><b>Updated on</b>: {data.updated_on && formatRFC7231(new Date(data.updated_on))}
                            </Typography>
                            <Grid container alignItems={"center"} spacing={2}>
                                <Grid item><Typography><b>Discord</b>: {data.discord_id ? "Linked" : "Not linked"}
                                </Typography></Grid>
                                <Grid item>
                                    {data.discord_id ? <Link href={"/api/discord/unlink"}><Button color={"error"}
                                                                                                  variant={"outlined"}>Unlink</Button></Link> :
                                        <Link href={"/api/discord/login"}><Button color={"success"}
                                                                                  variant={"outlined"}>Link</Button></Link>}
                                </Grid>
                                <Grid item xs={12} />
                                {currentUser && currentUser.uuid === data.uuid &&
                                    <Grid item><Button color={"error"} href={"/api/logout"}
                                                       variant={"outlined"}>Logout</Button></Grid>}
                                {currentUser && (currentUser.is_superadmin || currentUser.uuid === data.uuid) &&
                                    <Grid item><Button color={"error"} variant={"outlined"}
                                                       onClick={() => remove.mutate("uuid" in data ? data.uuid as string : "")}><DeleteIcon/></Button></Grid>}
                            </Grid>
                            <Box py={2}>
                                <Typography variant={"h4"}>Teams</Typography>
                                <Box py={2}>
                                    {data.teams && data.teams.map((team) => <Grid container key={team.team_uuid}
                                                                                  spacing={2}>
                                        <Grid item><Typography variant={"h5"}>{team.team.name}</Typography></Grid>
                                        <Grid item><Link href={`/teams/${team.team_uuid}`}
                                                         passHref><Button>Show</Button></Link></Grid>
                                    </Grid>)}
                                </Box>
                            </Box>
                        </Grid>
                    </Grid>
                </>}
            </>}

        </Box>
    </Paper>;
}