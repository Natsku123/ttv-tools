import { useRouter } from 'next/router';
import {Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import {useMutation, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {Membership, Team, User} from "@/services/types";
import {AxiosError} from "axios";
import ErrorMessage from "@/components/ErrorMessage";
import UserAvatar from "@/components/UserAvatar";
import Link from "next/link";
import { formatRFC7231 } from 'date-fns';
import {deleteTeam, getMembers, getTeam} from "@/services/teams";
import {getCurrentUser} from "@/services/users";
import DeleteIcon from "@mui/icons-material/Delete";

export default function TeamPage() {
    const router = useRouter();

    const queryClient = useQueryClient();

    const {
        data,
        error,
        isLoading
    }: UseQueryResult<Team, AxiosError> = useQuery(["teams", router.query.uuid], () => getTeam(router.query.uuid), {
        retry:  false
    });

    const {
        data: members,
    }: UseQueryResult<Array<Membership>, AxiosError> = useQuery(["members", router.query.uuid], () => getMembers(router.query.uuid as string), {
        enabled: !!router.query.uuid
    });

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });

    const remove = useMutation({
        mutationFn: deleteTeam,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['teams']})
            await queryClient.invalidateQueries({queryKey: ['teams', data.uuid]});
        }
    });

    return <Paper>
        <Box px={2} py={4}>
            { isLoading ? <>
                <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={12}>
                        <Typography variant={"h3"}><Skeleton /></Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><b>Description</b>: <Skeleton /></Typography>
                        <Typography><b>Created on</b>: <Skeleton /></Typography>
                        <Typography><b>Updated on</b>: <Skeleton /></Typography>
                        <Box py={2}>
                            <Typography variant={"h4"}>Members</Typography>
                        </Box>
                    </Grid>
                </Grid>
            </> : <>
                { error && <ErrorMessage code={error.code} message={error.message} />}
                { data && <>
                  <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={12}>
                      <Typography variant={"h3"}>{data.name}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography><b>Description</b>: {data.description}</Typography>
                      <Typography><b>Created on</b>: {data.created_on && formatRFC7231(new Date(data.created_on))}</Typography>
                      <Typography><b>Updated on</b>: {data.updated_on && formatRFC7231(new Date(data.updated_on))}</Typography>
                      {currentUser?.is_superadmin && <Grid item>
                        <Button variant={"outlined"} color={"error"} onClick={() => remove.mutate("uuid" in data ? data.uuid as string : "" )}><DeleteIcon /></Button>
                      </Grid>}
                      <Box py={2}>
                        <Typography variant={"h4"}>Members</Typography>
                          { members && members.map((member) => <Grid container key={member.uuid}>
                              <Grid item xs={4}><UserAvatar user={member.user} /></Grid>
                              <Grid item xs={8}><Typography variant={"h5"}>{member.user.name}</Typography></Grid>
                              {currentUser?.is_superadmin && currentUser.is_superadmin &&
                                  <Grid item xs={12}>
                                    <Link href={`/users/${member.uuid}`} passHref><Button>Show</Button></Link>
                                  </Grid>
                              }
                          </Grid>) }
                      </Box>
                    </Grid>
                  </Grid>
                </>}
            </> }

        </Box>
    </Paper>;
}