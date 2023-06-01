interface Base {
    readonly uuid?: string;
    readonly created_on?: string;
    readonly updated_on?: string;
}

interface Team extends Base {
    name: string;
    description: string;
    members?: Array<User>
}

interface User extends Base{
    readonly discord_id?: string;
    readonly twitch_id: string;
    readonly name: string;
    readonly login_name?: string;
    readonly icon_url?: string;
    readonly offline_image_url?: string;
    readonly description?: string;
    is_superadmin: boolean;
    readonly teams?: Array<Team>;
}

interface DiscordChannel {
    readonly discord_id: string;
    readonly name: string;
    readonly jump_url: string;
}

interface DiscordUser {
    readonly discord_id: string;
    readonly avatar_url: string;
    readonly name: string;
    readonly mention: string;
    readonly is_admin: boolean;
}

interface DiscordServer {
    readonly discord_id: string;
    readonly name: string;
    readonly icon_url: string;
    readonly description: string;
    readonly owner: DiscordUser;
    readonly channels: Array<DiscordChannel>;
}

interface EventSubscription extends Base {
    user_uuid: string;
    server_discord_id: string;
    channel_discord_id: string;
    event: string;
    readonly twitch_id?: string;
    custom_title?: string;
    custom_description?: string;
}

interface TeamInvite extends Base {
    team_uuid: string;
    user_twitch_id: string;
}

interface Membership extends Base {
    team_uuid: string;
    user_uuid: string;
    is_admin: boolean;
    allowed_invites: boolean;
}

export {
    Team,
    User,
    DiscordServer,
    DiscordChannel,
    DiscordUser,
    Membership,
    TeamInvite,
    EventSubscription
}