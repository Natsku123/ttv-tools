'use client'
import {Box, Button, Grid, Paper, Skeleton, Typography} from "@mui/material";
import {QueriesOptions, useMutation, useQueries, useQuery, useQueryClient, UseQueryResult} from "@tanstack/react-query";
import {DiscordChannel, DiscordServer, EventSubscription, User} from "@/src/services/types";
import {AxiosError} from "axios";
import {deleteEventSub, getEventSub} from "@/src/services/eventsubs";
import ErrorMessage from "@/src/components/ErrorMessage";
import {formatRFC7231} from "date-fns";
import {getCurrentUser} from "@/src/services/users";
import {getDiscordServers} from "@/src/services/discord";
import {useEffect, useState} from "react";
import DeleteIcon from "@mui/icons-material/Delete";

export default function EventsubPage({params}: { params: { uuid: string } }) {
    const queryClient = useQueryClient();

    const [discordServer, setDiscordServer] = useState<DiscordServer | null>(null);
    const [discordChannel, setDiscrodChannel] = useState<DiscordChannel | null>(null);

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry:  false
    });

    const queries: Array<QueriesOptions<any>> = [
        {
            queryKey: ["eventsubs", params.uuid],
            queryFn: () => getEventSub(params.uuid),
            options: {
                retry: false
            }
        },
        {
            queryKey: ["discordServers"],
            queryFn: getDiscordServers,
            options: {
                enabled: !!currentUser?.discord_id
            }
        }
    ];

    const results: Array<UseQueryResult<any, AxiosError>> = useQueries(
        { queries }
    ) as Array<UseQueryResult<any, AxiosError>>;

    const [eventsubResult, serversResult] = results;
    const {
        data,
        error,
        isLoading
    }: UseQueryResult<EventSubscription, AxiosError> = eventsubResult;

    const {
        data: discordServers,
    }: UseQueryResult<Array<DiscordServer>, AxiosError> = serversResult;

    useEffect(() => {
        if (data && discordServers) {
            const dServer = discordServers.find(v => v.discord_id === data.server_discord_id);
            setDiscordServer(dServer ? dServer : null);
        }
    }, [data, discordServers]);

    useEffect(() => {
        if (data && discordServer) {
            const dChannel = discordServer.channels.find(v => v.discord_id === data.channel_discord_id);
            setDiscrodChannel(dChannel ? dChannel : null);
        }
    }, [data, discordServer]);

    const remove = useMutation({
        mutationFn: deleteEventSub,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['eventsubs']})
            await queryClient.invalidateQueries({queryKey: ['eventsubs', data.uuid]});
        }
    });

    return (<Paper>
        <Box px={2} py={4}>
            { isLoading ? <>
                <Grid container spacing={4} alignItems={"center"}>
                    <Grid item xs={12}>
                        <Typography variant={"h3"}><Skeleton /></Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography><b>Custom title</b>: <Skeleton /></Typography>
                        <Typography><b>Custom description</b>: <Skeleton /></Typography>
                        <Typography><b>Created on</b>: <Skeleton /></Typography>
                        <Typography><b>Updated on</b>: <Skeleton /></Typography>
                    </Grid>
                </Grid>
            </> : <>
                { error && <ErrorMessage code={error.code} message={error.message} />}
                { data && discordServer && discordChannel && <>
                    <Grid container spacing={4} alignItems={"center"}>
                        <Grid item xs={12}>
                            <Typography variant={"h3"}>{discordServer.name} - #{discordChannel.name}: {data.event}</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Typography><b>Custom title</b>: {data.custom_title}</Typography>
                            <Typography><b>Custom description</b>: {data.custom_description}</Typography>
                            <Typography><b>Created on</b>: {data.created_on && formatRFC7231(new Date(data.created_on))}</Typography>
                            <Typography><b>Updated on</b>: {data.updated_on && formatRFC7231(new Date(data.updated_on))}</Typography>
                        </Grid>
                        <Grid item xs>
                            <Button variant={"outlined"} color={"error"} onClick={() => remove.mutate(params.uuid as string)}><DeleteIcon /></Button>
                        </Grid>
                    </Grid>
                </>}
            </> }
        </Box>
    </Paper>);
}