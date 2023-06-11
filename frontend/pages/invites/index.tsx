import {Team, TeamInvite, User} from "@/services/types";
import {QueryClient} from "@tanstack/query-core";
import {dehydrate, useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Controller, RegisterOptions, useForm, useWatch} from "react-hook-form";
import {AxiosError} from "axios";
import {getCurrentUser} from "@/services/users";
import {Autocomplete, Avatar, Box, Button, Grid, Paper, TextField, Typography} from "@mui/material";
import {getTeams} from "@/services/teams";
import {createInvite} from "@/services/invites";
import {useState} from "react";
import {getTwitchUsers} from "@/services/twitch";

interface FormValues {
    team: Team;
    login: string;
}

export async function getStaticProps() {
    const queryClient = new QueryClient()

    return {
        props: {
            dehydratedState: dehydrate(queryClient),
        },
    }
}

export default function InvitesPage() {
    const queryClient = useQueryClient();

    const {control, handleSubmit, resetField} = useForm<FormValues>({mode: "onChange"});

    const twitch_login = useWatch<FormValues>({control, name: "login"});

    const [twitch, setTwitch] = useState<{id: string, display_name: string, login: string, profile_image_url: string}>();


    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry: false
    });

    const userUuid = currentUser?.uuid;

    const {
        data: teams,
        isLoading
    }: UseQueryResult<Array<Team>, AxiosError> = useQuery(["teams"], getTeams, { enabled: !!userUuid});

    const {
        data: twitch_users,
        refetch
    }: UseQueryResult<{data: [{id: string, display_name: string, login: string, profile_image_url: string}]}, AxiosError> = useQuery(["twitch_users"], () => getTwitchUsers(twitch_login as string), {enabled: !!twitch_login});

    const create = useMutation({
        mutationFn: createInvite,
        onSuccess: async data => {
            queryClient.setQueryData(['invites', data.uuid], data);
            await queryClient.invalidateQueries({queryKey: ['invites']});
        }
    });

    const onSubmit: (data: FormValues) => void = (data) => {
        if (twitch && twitch.id) {
            const invite: TeamInvite = {
                user_twitch_id: twitch.id as string,
                team_uuid: data.team.uuid as string
            };

            create.mutate(invite);
        }
    };

    const requiredRules: RegisterOptions = {required: true};

    return (
        <Paper>
            <Box py={2} px={2}>
                {currentUser && !isLoading ? <>
                    <form onSubmit={handleSubmit(onSubmit)}>
                        <Controller
                            render={({field}) => <Autocomplete
                                {...field}
                                getOptionLabel={(option) => option.name}
                                isOptionEqualToValue={(o, v) => o.uuid === v.uuid}
                                renderInput={(params) => <TextField {...params} label="Team" margin="normal" />}
                                options={teams ? teams : []}
                                onChange={(_, data) => field.onChange(data)} />}
                            name="team" control={control} rules={requiredRules} />
                        <Controller
                            render={({field}) => <TextField {...field} fullWidth label={"Twitch User"} helperText={"Check carefully that the Twitch user is correct!"} margin="normal" />}
                            name="login"
                            control={control} rules={requiredRules} />
                        <Button color={"success"} onClick={() => refetch()}>Search</Button>

                        <Box py={2} width={250}>
                            {twitch_users && "data" in twitch_users && twitch_users["data"].map(u => <div key={u.id}>
                                <Grid container justifyContent={"space-around"} alignItems={"center"}>
                                    <Grid item><Avatar src={u.profile_image_url} /></Grid>
                                    <Grid item><Typography>{u.display_name}</Typography></Grid>
                                    <Grid item><Button color={"success"} onClick={() => setTwitch(u)}>Select</Button></Grid>
                                </Grid>
                            </div>)}

                        </Box>
                        <Box py={2}>
                            <Typography><b>Selected user</b>: {twitch && twitch.display_name}</Typography>
                        </Box>
                        <Box py={2}>
                            <Button variant={"contained"} color={"success"} type={"submit"} style={{marginLeft: 20}}>Create</Button>
                        </Box>
                    </form>
                </>  : <Typography variant={"h2"}>Not logged in!</Typography>}
            </Box>
        </Paper>
    )
}