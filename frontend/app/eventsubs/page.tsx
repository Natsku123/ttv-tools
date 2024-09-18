'use client'
import {
    dehydrate,
    QueriesOptions,
    useMutation,
    useQueries,
    useQuery,
    useQueryClient,
    UseQueryResult
} from "@tanstack/react-query";
import {DiscordChannel, DiscordRole, DiscordServer, EventSubscription, User} from "@/src/services/types";
import {AxiosError} from "axios";
import {getCurrentUser, getUsers} from "@/src/services/users";
import {createEventSub, deleteEventSub, getEventSubs, getEventSubsByUser} from "@/src/services/eventsubs";
import ErrorMessage from "@/src/components/ErrorMessage";
import {
    Autocomplete,
    Box,
    Button,
    Grid,
    Paper, Skeleton,
    TextField,
    Typography
} from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import {useState} from "react";
import {getDiscordServers} from "@/src/services/discord";
import {Controller, RegisterOptions, useForm} from "react-hook-form";
import Link from "next/link";

interface FormValues {
    user: User | null;
    event: string;
    server: DiscordServer | null;
    channel: DiscordChannel | null;
    role: DiscordRole | null;
    message: string;
    title: string;
    description: string;
}

export default function EventsubsPage() {

    const queryClient = useQueryClient();

    const {control, handleSubmit, watch, reset} = useForm<FormValues>({
        mode: "onChange",
        defaultValues: {user: null, description: "", channel: null, event: "", server: null, title: ""}
    });

    const {
        data: currentUser,
    }: UseQueryResult<User, AxiosError> = useQuery(["currentUser"], getCurrentUser, {
        retry: false
    });

    const userUuid = currentUser?.uuid;
    const isSuperAdmin = currentUser?.is_superadmin;
    const discordId = currentUser?.discord_id;

    const selectedDServer = watch('server');

    const queries: Array<QueriesOptions<any>> = [
        {
            queryKey: ["eventsubs"],
            queryFn: () => isSuperAdmin ? getEventSubsByUser(userUuid) : getEventSubs(),
            options: {
                enabled: !!userUuid,
            }
        },
        {
            queryKey: ["users"],
            queryFn: getUsers,
            options: {
                enabled: !!isSuperAdmin,
                retry: !!isSuperAdmin
            }
        },
        {
            queryKey: ["discordServers"],
            queryFn: getDiscordServers,
            options: {
                enabled: !!discordId,
                retry: !!discordId
            }
        }
    ];

    const results: Array<UseQueryResult<any, AxiosError>> = useQueries(
        {queries}
    ) as Array<UseQueryResult<any, AxiosError>>;

    const [eventsubResult, usersResult, serversResult] = results;
    const {
        data: eventsubs,
        error,
        isLoading
    }: UseQueryResult<Array<EventSubscription>, AxiosError> = eventsubResult;
    const {
        data: users
    }: UseQueryResult<Array<User>, AxiosError> = usersResult;
    const {
        data: discordServers,
    }: UseQueryResult<Array<DiscordServer>, AxiosError> = serversResult;


    const create = useMutation({
        mutationFn: createEventSub,
        onSuccess: async data => {
            queryClient.setQueryData(['eventsubs', data.uuid], data);
            reset(data);
            await queryClient.invalidateQueries({queryKey: ['eventsubs']});
        }
    });
    const remove = useMutation({
        mutationFn: deleteEventSub,
        onSuccess: async data => {
            await queryClient.invalidateQueries({queryKey: ['eventsubs']})
            await queryClient.invalidateQueries({queryKey: ['eventsubs', data.uuid]});
        }
    });

    const [createEnabled, setCreateEnabled] = useState<boolean>(false);

    const eventOptions = [
        "channel.update",
        "channel.follow",
        "channel.subscribe",
        "channel.subscription.end",
        "channel.subscription.gift",
        "channel.subscription.message",
        "channel.cheer",
        "channel.raid",
        "channel.ban",
        "channel.unban",
        "channel.moderator.add",
        "channel.moderator.remove",
        "channel.channel_points_custom_reward.add",
        "channel.channel_points_custom_reward.update",
        "channel.channel_points_custom_reward.remove",
        "channel.channel_points_custom_reward_redemption.add",
        "channel.channel_points_custom_reward_redemption.update",
        "channel.poll.begin",
        "channel.poll.progress",
        "channel.poll.end",
        "channel.prediction.begin",
        "channel.prediction.progress",
        "channel.prediction.lock",
        "channel.prediction.end",
        "channel.charity_campaign.donate",
        "channel.charity_campaign.start",
        "channel.charity_campaign.progress",
        "channel.charity_campaign.stop",
        "drop.entitlement.grant",
        "extension.bits_transaction.create",
        "channel.goal.begin",
        "channel.goal.progress",
        "channel.goal.end",
        "channel.hype_train.begin",
        "channel.hype_train.progress",
        "channel.hype_train.end",
        "channel.shield_mode.begin",
        "channel.shield_mode.end",
        "channel.shoutout.create",
        "channel.shoutout.receive",
        "stream.online",
        "stream.offline",
        "user.authorization.grant",
        "user.authorization.revoke",
        "user.update"
    ];

    const onSubmit: (user: User, data: FormValues) => void = (user: User, data) => {
        if (!data.user) {
            data.user = user;
        }

        if (data.user.uuid === undefined) {
            return;
        }

        const message = (data.role && data.message) ? `${data.role.mention} ${data.message}` : data.role ? data.role.mention : data.message ? data.message : "";

        const eventSub: EventSubscription = {
            channel_discord_id: data.channel ? data.channel.discord_id : "",
            custom_description: data.description,
            custom_title: data.title,
            event: data.event,
            server_discord_id: data.server ? data.server.discord_id : "",
            user_uuid: data.user.uuid,
            message: message
        };

        create.mutate(eventSub);

    };

    const requiredRules: RegisterOptions = {required: true};

    return (
        <Box px={2} py={2}>
            <Grid container spacing={2}>
                {error && error.code === "ERR_BAD_REQUEST" &&
                    <Grid item xs={12}><Paper><Box px={2} py={2}><Typography variant={"h3"}>Feature not available :(</Typography></Box></Paper></Grid>}
                <Grid item xs={12} md={6}>
                    {!isLoading ? <>
                        {eventsubs && eventsubs.length > 0 ? <>
                            {eventsubs.map((eventsub) => <Paper key={eventsub.uuid}>
                                <Box py={2} px={2} my={2}>
                                    <Grid container justifyContent={"space-between"} alignItems={"center"}>
                                        <Grid item xs={8}>
                                            <Typography><b>Title</b>: {eventsub.custom_title}</Typography>
                                            <Typography><b>Event</b>: {eventsub.event}</Typography>
                                        </Grid>
                                        <Grid item container xs={4} justifyContent={"space-evenly"}>
                                            <Grid item>
                                                <Link href={`/eventsubs/${eventsub.uuid}`} passHref>
                                                    <Button variant={"outlined"}
                                                            color={"primary"}><VisibilityIcon/></Button>
                                                </Link>
                                            </Grid>
                                            <Grid item>
                                                <Button variant={"outlined"} color={"error"}
                                                        onClick={() => remove.mutate(eventsub.uuid as string)}><DeleteIcon/></Button>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                </Box>
                            </Paper>)}
                        </> : <Paper><Box py={2} px={2} my={2}><Typography variant={"h3"}>No event subscriptions
                            found!</Typography></Box></Paper>}
                    </> : <>
                        {[1, 2, 3].map(i => <Paper key={"skeleton-" + i}>
                            <Box py={2} px={2} my={2}>
                                <Grid container justifyContent={"space-between"} alignItems={"center"}>
                                    <Grid item xs={8}>
                                        <Typography><Skeleton variant="text" width={300}/></Typography>
                                        <Typography><Skeleton variant="text" width={300}/></Typography>
                                    </Grid>
                                    <Grid item container xs={4} justifyContent={"space-evenly"}>
                                        <Grid item>
                                            <Skeleton variant="rounded" width={64} height={36}/>
                                        </Grid>
                                        <Grid item>
                                            <Skeleton variant="rounded" width={64} height={36}/>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Box>
                        </Paper>)}
                    </>}
                    <Button variant={"outlined"} color={"primary"} onClick={() => setCreateEnabled(true)}
                            disabled={createEnabled}>Create</Button>
                </Grid>
                {createEnabled && currentUser && <Grid item xs={12} md={6}>
                    <Paper>
                        <Box px={2}>
                            <form onSubmit={handleSubmit((data) => onSubmit(currentUser, data))}>
                                {currentUser && currentUser.is_superadmin && users &&
                                    <Controller
                                        render={({field}) => <Autocomplete
                                            {...field}
                                            isOptionEqualToValue={(o, v) => o.uuid === v.uuid}
                                            getOptionLabel={(option) => option.name}
                                            renderInput={(params) => <TextField {...params} label="User"
                                                                                margin="normal"/>}
                                            options={users ? users : []}
                                            onChange={(_, data) => field.onChange(data)}/>}
                                        name="user" control={control}/>
                                }
                                <Controller
                                    render={({field}) => <Autocomplete
                                        {...field}
                                        renderInput={(params) => <TextField {...params} label="Event" margin="normal"/>}
                                        options={eventOptions}
                                        onChange={(_, data) => field.onChange(data)}/>}
                                    name="event" control={control} rules={requiredRules}/>
                                <Controller
                                    render={({field}) => <Autocomplete
                                        {...field}
                                        getOptionLabel={(option) => option.name}
                                        isOptionEqualToValue={(o, v) => o.discord_id === v.discord_id}
                                        renderInput={(params) => <TextField {...params}
                                                                            helperText={"If you aren't seeing your server, add the bot to the server below."}
                                                                            label="Discord Server" margin="normal"/>}
                                        options={discordServers ? discordServers : []}
                                        onChange={(_, data) => field.onChange(data)}/>}
                                    name="server" control={control} rules={requiredRules}/>
                                <Controller
                                    render={({field}) => <Autocomplete
                                        {...field}
                                        getOptionLabel={(option) => option.name}
                                        isOptionEqualToValue={(o, v) => o.discord_id === v.discord_id}
                                        renderInput={(params) => <TextField {...params} label="Discord Channel"
                                                                            margin="normal"/>}
                                        options={selectedDServer ? selectedDServer.channels : []}
                                        onChange={(_, data) => field.onChange(data)}/>}
                                    name="channel" control={control} rules={requiredRules}/>
                                <Controller
                                    render={({field}) => <Autocomplete
                                        {...field}
                                        getOptionLabel={(option) => option.name}
                                        isOptionEqualToValue={(o, v) => o.discord_id === v.discord_id}
                                        renderInput={(params) => <TextField {...params} label="Discord Role"
                                                                            margin="normal"/>}
                                        options={selectedDServer ? selectedDServer.roles : []}
                                        onChange={(_, data) => field.onChange(data)}/>}
                                    name="role" control={control} rules={requiredRules}/>
                                <Controller
                                    render={({field}) => <TextField {...field} fullWidth multiline label={"Message"}
                                                                    margin="normal" minRows={4}/>}
                                    name="message"
                                    control={control}/>
                                <Controller
                                    render={({field}) => <TextField {...field} fullWidth label={"Title"}
                                                                    margin="normal"/>}
                                    name="title"
                                    control={control}/>
                                <Controller
                                    render={({field}) => <TextField {...field} fullWidth multiline label={"Description"}
                                                                    margin="normal" minRows={4}/>}
                                    name="description"
                                    control={control}/>
                                <Box py={2}>
                                    <Button variant={"outlined"} color={"error"}
                                            onClick={() => setCreateEnabled(false)}>Close</Button>
                                    <Button variant={"contained"} color={"success"} type={"submit"}
                                            style={{marginLeft: 20}}>Create</Button>
                                </Box>
                            </form>
                            <Box py={2}>
                                <Link href={"/api/discord/addbot"}><Button variant={"outlined"} color={"success"}>Add
                                    bot</Button></Link>
                            </Box>
                        </Box>
                    </Paper>
                </Grid>}
            </Grid>
        </Box>

    );
}