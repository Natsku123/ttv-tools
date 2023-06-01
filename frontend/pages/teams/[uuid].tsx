import { useRouter } from 'next/router';
import {Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import {useQuery, UseQueryResult} from "@tanstack/react-query";
import {Team, User} from "@/services/types";
import {AxiosError} from "axios";
import ErrorMessage from "@/components/ErrorMessage";
import UserAvatar from "@/components/UserAvatar";
import Link from "next/link";
import { formatRFC7231 } from 'date-fns';
import {getTeam} from "@/services/teams";
import {getCurrentUser} from "@/services/users";

export default function TeamPage() {
    const router = useRouter();

    const {
        data,
        error,
        isLoading
    }: UseQueryResult<Team, AxiosError> = useQuery(["team", router.query.uuid], () => getTeam(router.query.uuid), {
        retry:  false
    });

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
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
                      <Typography><b>Created on</b>: {formatRFC7231(new Date(data.created_on))}</Typography>
                      <Typography><b>Updated on</b>: {data.updated_on ? formatRFC7231(new Date(data.updated_on)) : ""}</Typography>
                      <Box py={2}>
                        <Typography variant={"h4"}>Members</Typography>
                          { data.members && data.members.map((member) => <Grid container>
                              <Grid item xs={4}><UserAvatar user={member} /></Grid>
                              <Grid item xs={8}><Typography variant={"h5"}>{member.name}</Typography></Grid>
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