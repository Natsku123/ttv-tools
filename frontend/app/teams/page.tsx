'use client'
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Controller, useForm} from "react-hook-form";
import {Membership, Team, User} from "@/src/services/types";
import {AxiosError} from "axios";
import {getCurrentUser} from "@/src/services/users";
import {createTeam, deleteTeam, getTeams} from "@/src/services/teams";
import {Box, Button, Grid, Paper, Skeleton, TextField, Typography} from "@mui/material";
import ErrorMessage from "@/src/components/ErrorMessage";
import Link from "next/link";
import VisibilityIcon from "@mui/icons-material/Visibility";
import DeleteIcon from "@mui/icons-material/Delete";
import {useState} from "react";

interface FormValues {
    name: string;
    description: string;
}


export default function TeamsPage() {
    const queryClient = useQueryClient();

    const { control, handleSubmit, reset } = useForm<FormValues>({ mode: "onChange"});

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });

    const {
        data: teams,
        error,
        isLoading
    }: UseQueryResult<Array<Team | Membership>, AxiosError> = useQuery(["teams"], getTeams);

    const create = useMutation({
        mutationFn: createTeam,
        onSuccess: async data => {
            queryClient.setQueryData(['teams', data.uuid], data);
            reset(data);
            await queryClient.invalidateQueries({queryKey: ['teams']});
        }
    });
    const remove = useMutation({
        mutationFn: deleteTeam,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['teams']})
            await queryClient.invalidateQueries({queryKey: ['teams', data.uuid]});
        }
    });

    const [createEnabled, setCreateEnabled] = useState<boolean>(false);

    const onSubmit: (data: FormValues) => void = (data) => {
        create.mutate(data);
    };

    return (
        <Box px={2} py={2}>
            <Grid container spacing={2}>
                {error && <Grid item xs={12}><Paper><ErrorMessage code={error.code} message={error.message} /></Paper></Grid>}
                <Grid item xs={12} md={6}>
                    {!isLoading ? <>
                        { teams && teams.length > 0 ? <>
                            {teams.map(t => "team_uuid" in t && t.team_uuid && t.user_uuid ? t.team : t as Team).map((team) => <Paper key={team.uuid}>
                                <Box py={2} px={2} my={2}>
                                    <Grid container justifyContent={"space-between"} alignItems={"center"}>
                                        <Grid item xs={8}>
                                            <Typography><b>Name</b>: {team.name}</Typography>
                                        </Grid>
                                        <Grid item container xs={4} justifyContent={"space-evenly"}>
                                            <Grid item>
                                                <Link href={`/teams/${team.uuid}`} passHref>
                                                    <Button variant={"outlined"} color={"primary"}><VisibilityIcon /></Button>
                                                </Link>
                                            </Grid>
                                            {currentUser?.is_superadmin && <Grid item>
                                                <Button variant={"outlined"} color={"error"} onClick={() => remove.mutate(team.uuid as string)}><DeleteIcon /></Button>
                                            </Grid>}
                                        </Grid>
                                    </Grid>
                                </Box>
                            </Paper>)}
                        </> : <Paper><Box py={2} px={2} my={2}><Typography variant={"h3"}>No teams found!</Typography></Box></Paper>}
                    </> : <>
                        {[1, 2, 3].map(i => <Paper key={"skeleton-" + i}>
                            <Box py={2} px={2} my={2}>
                                <Grid container justifyContent={"space-between"} alignItems={"center"}>
                                    <Grid item xs={8}>
                                        <Typography><Skeleton variant="text" width={300} /></Typography>
                                    </Grid>
                                    <Grid item container xs={4} justifyContent={"space-evenly"}>
                                        <Grid item>
                                            <Skeleton variant="rounded" width={64} height={36} />
                                        </Grid>
                                        <Grid item>
                                            <Skeleton variant="rounded" width={64} height={36} />
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Box>
                        </Paper>)}
                    </>}
                    {currentUser && currentUser.is_superadmin && <Button variant={"outlined"} color={"primary"} onClick={() => setCreateEnabled(true)} disabled={createEnabled}>Create</Button>}
                </Grid>
                {createEnabled && currentUser && currentUser.is_superadmin && <Grid item xs={12} md={6}>
                  <Paper>
                    <Box px={2}>
                      <form onSubmit={handleSubmit(onSubmit)}>
                        <Controller
                          render={({field}) => <TextField {...field} fullWidth label={"Name"} margin="normal" />}
                          name="name"
                          control={control} rules={{required: true,}} />
                        <Controller
                          render={({field}) => <TextField {...field} fullWidth multiline label={"Description"} margin="normal" minRows={4} />}
                          name="description"
                          control={control} rules={{required: true,}} />
                        <Box py={2}>
                          <Button variant={"outlined"} color={"error"} onClick={() => setCreateEnabled(false)}>Close</Button>
                          <Button variant={"contained"} color={"success"} type={"submit"} style={{marginLeft: 20}}>Create</Button>
                        </Box>
                      </form>
                    </Box>
                  </Paper>
                </Grid>}
            </Grid>
        </Box>
    )
}