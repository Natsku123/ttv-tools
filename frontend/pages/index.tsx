import {Box, Grid, Paper, Typography, Link as MuiLink, Button} from '@mui/material';
import {useQuery, UseQueryResult} from "@tanstack/react-query";
import {User} from "@/services/types";
import {AxiosError} from "axios";
import {getCurrentUser} from "@/services/users";
import Link from "next/link";

const HomePage = () => {

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });
    return (
      <Paper>
        <Box px={2} py={2}>
            <Grid container spacing={2} direction={"column"} justifyContent={"center"} alignItems={"center"}>
                <Grid item xs>
                    <Typography variant={"h1"}>Welcome to TTV tools!</Typography>
                </Grid>
                <Grid item xs>
                    <Typography variant={"h5"}>
                        A Twitch integration tool by Natsku.
                    </Typography>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant={"body1"}>
                        The purpose of this tool is to integrate Twitch Events to Discord via a bot and a few other
                        tools to enable fast notifications on Discord on events occuring on Twitch. This tool is
                        maintained by Natsku alone so changes and fixes might not come quick. Most critical issues will
                        be fixed ASAP. Submit your issues <MuiLink href={"https://github.com/Natsku123/ttv-tools/issues"}>here</MuiLink>.
                    </Typography>
                </Grid>
                {!currentUser ?
                    <Grid item xs>
                        <Typography variant={"h5"}>Login: <Button href={"/api/twitch/login"}>Login</Button></Typography>
                    </Grid> : <Grid item xs>
                        <Typography variant={"body1"}>
                            To get started, head over to <MuiLink><Link href={`/users/${currentUser.uuid}`}>your user
                            page</Link></MuiLink> and link your Discord. Then head over to <MuiLink>
                            <Link href={"/eventsubs"}>Events </Link></MuiLink> to create and manage your event
                            subscriptions. If you haven&apos;t added the bot already to your server, click the &quot;Add Bot&quot;
                            button to invite the bot.
                        </Typography>
                    </Grid>
                }

            </Grid>
        </Box>
      </Paper>
    );
};

export default HomePage;