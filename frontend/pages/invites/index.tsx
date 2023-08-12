import {Team, TeamInvite, User} from "@/services/types";
import {QueryClient} from "@tanstack/query-core";
import {dehydrate, useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Controller, RegisterOptions, useForm, useWatch} from "react-hook-form";
import {AxiosError} from "axios";
import {getCurrentUser} from "@/services/users";
import {
    Autocomplete,
    Avatar,
    Box,
    Button,
    Grid,
    Paper,
    Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow,
    TextField,
    Typography
} from "@mui/material";
import {getTeams} from "@/services/teams";
import {createInvite, getInvites} from "@/services/invites";
import {useState} from "react";
import {getTwitchUsers, getTwitchUsersById} from "@/services/twitch";
import {formatRFC7231} from "date-fns";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Link from "next/link";

interface FormValues {
    team: Team | null;
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

    const {control, handleSubmit, resetField} = useForm<FormValues>({mode: "onSubmit", defaultValues: {team: null, login: ""}});

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
        data: invites,
        isLoading: invitesLoading
    }: UseQueryResult<Array<TeamInvite>, AxiosError> = useQuery(["invites"], getInvites, {
        enabled: currentUser && currentUser.is_superadmin
    });

    const {
        data: twitch_users,
        refetch
    }: UseQueryResult<{data: [{id: string, display_name: string, login: string, profile_image_url: string}]}, AxiosError> = useQuery(["twitch_users"], () => getTwitchUsers(twitch_login as string), {enabled: false});

    const {
        data: existing_users,
        refetch: refetch_existing
    }: UseQueryResult<{data: [{id: string, display_name: string, login: string, profile_image_url: string}]}, AxiosError> = useQuery(["twitch_existing_users"], () => getTwitchUsersById(invites ? invites.map(i => i.user_twitch_id as string) : []), {enabled: !!invites});


    const create = useMutation({
        mutationFn: createInvite,
        onSuccess: async data => {
            queryClient.setQueryData(['invites', data.uuid], data);
            await queryClient.invalidateQueries({queryKey: ['invites']});
            await queryClient.invalidateQueries({queryKey: ["twitch_existing_users"]});
            await refetch_existing()
        }
    });

    const onSubmit: (data: FormValues) => void = (data) => {
        if (twitch && twitch.id && data.team) {
            const invite: TeamInvite = {
                user_twitch_id: twitch.id as string,
                team_uuid: data.team.uuid as string
            };

            create.mutate(invite);
        }
    };

    const requiredRules: RegisterOptions = {required: true};

    const getTwitchName = (users: [{id: string, display_name: string, login: string, profile_image_url: string}], invite: TeamInvite) => {
        let found_user = users.find(u => u.id === invite.user_twitch_id);
        if (found_user) {
            return found_user.display_name;
        } else {
            return ""
        }
    }

    const getTwitchAvatar = (users: [{id: string, display_name: string, login: string, profile_image_url: string}], invite: TeamInvite) => {
        let found_user = users.find(u => u.id === invite.user_twitch_id);
        if (found_user) {
            return found_user.profile_image_url;
        } else {
            return ""
        }
    }

    return (
        <Paper>
            <Box py={2} px={2}>
                { !isLoading ? <>
                    {currentUser ? <>
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
                                render={({field}) => <TextField {...field} fullWidth label={"Twitch User"} helperText={"Check carefully that the Twitch user is correct!"} margin="normal" onChange={(event) => field.onChange(event.target.value)}  />}
                                name="login"
                                control={control} />
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
                </> : <Typography variant={"h2"}>Loading...</Typography>}
            </Box>

            {currentUser && currentUser.is_superadmin &&
              <Box py={2} px={2}>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell></TableCell>
                          <TableCell>Twitch</TableCell>
                          <TableCell>Created on</TableCell>
                          <TableCell></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                          { invites && invites.map(invite => <TableRow key={invite.uuid}>
                              <TableCell><Avatar src={existing_users && getTwitchAvatar(existing_users.data, invite)} /></TableCell>
                              <TableCell>{existing_users && getTwitchName(existing_users.data, invite)}</TableCell>
                              <TableCell>{invite.created_on && formatRFC7231(new Date(invite.created_on))}</TableCell>
                              <TableCell>
                                  <Link href={`/invites/${invite.uuid}`} passHref>
                                      <Button variant={"outlined"} color={"primary"}><VisibilityIcon /></Button>
                                  </Link>
                              </TableCell>
                          </TableRow>)}
                      </TableBody>
                    </Table>
                  </TableContainer>
              </Box>
            }
        </Paper>
    )
}