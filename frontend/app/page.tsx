"use client"
import Typography from "@mui/material/Typography";
import {Box, Grid, Link, Paper} from "@mui/material";
import {useQuery, UseQueryResult} from "@tanstack/react-query";
import {getCurrentUser} from "@/src/services/users";
import Button from "@mui/material/Button";
import * as React from "react";
import {User} from "@/src/services/types";
import {AxiosError} from "axios";

export default function Home() {

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry: false
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
                    <Grid item container direction={"column"} xs={12} spacing={2}>
                        <Grid item xs={12}>
                            <Typography variant={"body1"}>
                                The purpose of this tool is to integrate Twitch Events to Discord via a bot and a few
                                other tools to enable fast notifications on Discord on events occurring on Twitch. This
                                tool is maintained by Natsku alone so changes and fixes might not come quick. Most
                                critical issues will be fixed ASAP. Submit your issues <Link
                                href={"https://github.com/Natsku123/ttv-tools/issues"}>here</Link>.
                            </Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant={"body1"}>
                                Currently access is restricted to those who have been invited to use the platform. You
                                might be able to login, but might not be able to do anything else.
                            </Typography>
                        </Grid>
                        {!currentUser ?
                            <Grid item xs>
                                <Typography variant={"h5"}>Login: <Button
                                    href={"/api/twitch/login"}>Login</Button></Typography>
                            </Grid> : <Grid item xs>
                                <Typography variant={"body1"}>
                                    To get started, head over to <Link href={`/users/${currentUser.uuid}`}>your user
                                    page</Link> and link your Discord. Then head over to <Link href={"/eventsubs"}>
                                    Events</Link> to create and manage your event
                                    subscriptions. If you haven&apos;t added the bot already to your server, click
                                    the &quot;Add Bot&quot;
                                    button to invite the bot.
                                </Typography>
                            </Grid>
                        }
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    );
}