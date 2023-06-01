import {useQuery, UseQueryResult} from "@tanstack/react-query";
import {User} from "@/services/types";
import {AxiosError} from "axios";
import {getCurrentUser} from "@/services/users";
import {Box, Button, Grid, Typography} from "@mui/material";
import Link from "next/link";
import UserAvatar from "@/components/UserAvatar";

export const UserBar = () => {
    const {
        data,
        error
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });

    return (
        <>
            {data && data?.name &&
              <Box px={2}>
                <Link href={`/users/${data.uuid}`}>
                    <Grid container alignItems={"center"}>
                      <Grid item>
                        <Box px={2}>
                          <Typography>{ data.name }</Typography>
                        </Box>
                      </Grid>
                      <Grid item>
                        <UserAvatar user={data} />
                      </Grid>
                    </Grid>
                </Link>
              </Box>
            }
            {error &&
              <Box px={2}>
                <Button href={"/api/twitch/login"}>Login</Button>
              </Box>
            }
        </>
    )
}